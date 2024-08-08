#!/usr/bin/env python3

# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# https://github.com/bluebanquise/
# Benoit Leveugle <benoit.leveugle@gmail.com>
# 1.0.1

from flask import Flask, request, jsonify
from celery import Celery
import time
import os
import sys
import subprocess
from subprocess import Popen, PIPE
import yaml
import logging
from ClusterShell.NodeSet import NodeSet
import ssh_wait
from datetime import datetime

# Colors, from https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_file(filename):
    logging.info(bcolors.OKBLUE+'Loading '+filename+bcolors.ENDC)

    with open(filename, 'r') as f:
        # Select YAML loader (needs PyYAML 5.1+ to be safe)
        if int(yaml.__version__.split('.')[0]) > 5 or (int(yaml.__version__.split('.')[0]) == 5 and int(yaml.__version__.split('.')[1]) >= 1):
            return yaml.load(f, Loader=yaml.FullLoader)
        return yaml.load(f)

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'pyamqp://root:root@localhost//'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

##############################################################################
########### FLASK
##############################################################################

@app.route('/start_task', methods=['GET', 'POST', 'DELETE', 'PUT'])
def flask_start_task():
    task_data = request.get_json()
    print('Got new task with arguments:')
    print(task_data)
    print('Sending task to worker cluster queue...')
    counters = {'stage': 0, 'retry': 0}
    task = celery_execute_task.delay(task_data,tasks_list,counters)
    return jsonify({"Automate":"task submitted"})

##############################################################################
########### CELERY
##############################################################################

@celery.task
def celery_execute_task(task_data, tasks_list, counters):

    stage = counters['stage']
    stage_return_code = 0

###############################################################################################
    ######################## Internal processing
    ################

    ## Logs
    if 'node' in task_data:
        logs_path = '/var/log/bluebanquise/automate/' + task_data['node'] + '.log'
    else:
        logs_path = '/var/log/bluebanquise/automate/global.log'
    logger = logging.getLogger()
    handler = logging.FileHandler(logs_path)
    formatter = logging.Formatter('[%(levelname)s](%(asctime)s) %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('Entering new stage ' + str(stage) + ' for task ' + task_data['task'])
    logger.info('Stage name: ' + tasks_list[task_data['task']][stage]['name'])

###############################################################################################
    ######################## Tasks loop
    ################
    for task in tasks_list[task_data['task']][stage]['tasks']:

        ## COMMANDS
        if 'command' in task:
            if 'exit_code' in task:
                exit_code = task['exit_code']
            else:
                exit_code = 0
            try:
                logger.info('Executing command: ' + eval(task['command']))
                child = subprocess.Popen( eval(task['command']), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                stdout,stderr = child.communicate()
                if stdout is not None:
                    logger.info(stdout.decode("utf-8"))
                if stderr is not None:
                    logger.info(stderr.decode("utf-8"))
                rc = child.returncode
                if rc != exit_code:
                    logger.error("Command was terminated by signal " + str(rc))
                    stage_return_code = 1
                    break
            except OSError as e:
                logger.error("Command execution failed:" + str(e))
                stage_return_code = 1
                break

        ## ACTIONS
        if 'action' in task:
            if task['action'] == 'wait':
                logger.info('Waiting ' + str(task['delay']) + 's ...')
                time.sleep(task['delay'])
            if task['action'] == 'ssh_wait':
                logger.info('Waiting for ssh connectivity on host ' + task_data['node'] +' ...')
                rc=ssh_wait.ssh_wait(task_data['node'], service='ssh', wait=True, wait_limit=task['delay'], log_fn=print)
                if rc != 0:
                    logger.warning('Failed to establish ssh connectivity to host, timed out.')
                    stage_return_code = 1
                    break
                else:
                    logger.info('Success to establish ssh connectivity to host.')

###############################################################################################
    ######################## Log final status
    ################
    if stage_return_code == 0:
        logger.info('Stage executed successfully.')
    else:
        logger.warning('Stage executed with issues.')

###############################################################################################
    ######################## Evaluate end of global task
    ################
    if (stage + 1) == len(tasks_list[task_data['task']]) and stage_return_code == 0:
        print('Task ' + tasks_list[task_data['task']][stage]['name'] + ' done.')
        logger.info('Global task executed successfully. Exiting.')
        return 0

###############################################################################################
    ######################## Next stage submittion
    ################
    if stage_return_code == 0:
        logger.info('Now submitting next stage to scheduler...')
        counters['stage'] = counters['stage'] + 1 # Increment stage counter
        counters['retry'] = 0                     # Reset retry counter
        task = celery_execute_task.delay(task_data, tasks_list, counters)
        logger.info('Done. Bye Bye.\n')
        return 0
    elif 'retry' in tasks_list[task_data['task']][stage]:
        if counters['retry'] < tasks_list[task_data['task']][stage]['retry']:
            logger.info('Now submitting same stage to scheduler with retry count ' + str(counters['retry']) + '/' + str(tasks_list[task_data['task']][stage]['retry']) + '...')
            counters['retry'] = counters['retry'] + 1
            task = celery_execute_task.delay(task_data, tasks_list, counters)
            logger.info('Done. Bye Bye.\n')
            return 1

    logger.info('Done. Bye Bye.\n')
    return 2


##############################################################################
########### MAIN
##############################################################################

if __name__ == '__main__':

    print("""\

                  ....,,
                .::o::;'          .....
               ::::::::        .::::o:::.,
              .::' `:::        :::::::''"
              :::     :       ::'   `.
             .:::     :       :'      ::
            .:::       :     ,:       `::
           .' :        :`. ." :        :::
          .' .:        :  :  .:        : :
          : ::'        ::. :' :        : :
          :: :         :`: :  :        :`:
          :  :         :  ''  :        : '
        _.---:         :___   :        :
             :        :`   `--:        :
        l42   : :---: :        : :---: :`---.
              '```  '```      '''   ''''

                BlueBanquise Automate
                        1.0.1
                   Benoit LEVEUGLE

                    """)
    # global g_user
    # global g_password
    global tasks_list
    # with open('/etc/worker_cluster/parameters.yml', 'r') as f:
    #     worker_cluster_parameters = yaml.load(f)
#    with open('/etc/bbautomate/tasks.yml', 'r') as f:
#        tasks_list = yaml.load(f, Loader = yaml.FullLoader)
    tasks_list = load_file('/etc/bbautomate/tasks.yml')
    #g_user = worker_cluster_parameters['http_user']
    #g_password = worker_cluster_parameters['http_password']
    app.run()
