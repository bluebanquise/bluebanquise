from argparse import ArgumentParser
import os
import yaml
import multiprocessing as mp
#import json
#from flask import Flask, request, jsonify
#from flask_restful import Api, Resource
import importlib
import sys
import logging

import time


# bluebanquise-hardware c001 power on
# bluebanquise-hardware c001 boot pxe

# c001:
#   power:
#     protocol: ipmi
#     parameters:
#       user: ADMIN
#       password: ADMIN
#   boot:
#   console:

# bluebanquise-power c001/power/on
# bluebanquise-power c001/boot/pxe


def rangeexpand(txt):
    """
    Expand a range of nodes for nodeset function
    """
    lst = []
    for r in txt.split(','):
        zlen = len(str(r).split('-')[0])
        lstlen_0 = len(lst)
        if '-' in r[1:]:
            r0, r1 = r[1:].split('-', 1)
            lst += range(int(r[0] + r0), int(r1) + 1)
        else:
            lst.append(int(r))
        lstlen_1 = len(lst)
        for i in range(lstlen_0, lstlen_1):
            lst[i] = str(lst[i]).zfill(zlen)
    return lst


def nodesetexpand(znodeset):
    """
    Expand a basic nodeset, prevents need of Clustershell
    """
    nodeset = []
    for n in znodeset.split(','):
        # supports a single range per element
        if '[' in n and ']' in n:
            n1 = n.split('[')[0]
            n3 = n.split(']')[1]
            for nn in rangeexpand(n.replace(n1 + '[', '').replace(']' + n3, '')):
                nodeset.append(n1 + nn + n3)
        else:
            nodeset.append(n)
    return nodeset

# Get arguments
parser = ArgumentParser()
parser.add_argument("-v", "--verbose", dest="enable_verbose",
                    help="Enable verbosity.", action="store_true", default=False)
parser.add_argument("-d", "--dryrun", dest="enable_dryrun",
                    help="Enable dryrun.", action="store_true", default=False)
parser.add_argument("-p", "--poolsize", dest="pool_size",
                    help="Set size of execution pool, if not set will use the number of system cores.", default=None)


passed_arguments, cli_request = parser.parse_known_args()

if passed_arguments.enable_verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


logging.debug("Loading plugins...")
hardware_plugins = {} 
for hwdp in ['ipmi']:
    logging.debug("  - Loading " + str(hwdp))
    hardware_plugins[hwdp] = importlib.import_module('plugins.' + hwdp)

nodes = cli_request[0]
action = cli_request[1]
action_arguments = cli_request[2]

logging.debug("Loading configuration...")
configuration_file_path = 'bluebanquise-hardware.yml'

if os.path.exists(configuration_file_path):
    with open(configuration_file_path, 'r') as file:
        hardware_configuration = yaml.safe_load(file)
else:
    print("ERROR - Configuration file not found at " + configuration_file_path)
    quit(1)

def node_execute_action(node):
    logging.debug("[" + node + "] Executing action")
    # try:
    if not node in hardware_configuration['nodes']:
        logging.warning("[" + node + "] Node not in configuration file, skipping.")
        return -2, node
    node_current_action_protocol = hardware_configuration['nodes'][node][action]['protocol']
    logging.debug("[" + node + "] action protocol: " + node_current_action_protocol)
    node_hardware_plugin = hardware_plugins[node_current_action_protocol]
    node_connector = node_hardware_plugin.HardwareConnector(dryrun=passed_arguments.enable_dryrun)
    #return_code = node_hardware_connection[action](action_arguments, node_current_action_parameters)
    return_code = getattr(node_connector,action)(node, hardware_configuration['nodes'][node], action_arguments)
    return return_code, node
    # except Exception as e:
    #     report_error(e)
    #     return 1

if __name__ == "__main__":

    logging.debug("Running main execution loop...")

    if passed_arguments.pool_size is not None:
        pool = mp.Pool(int(passed_arguments.pool_size))
    else:
        pool = mp.Pool(mp.cpu_count())

    nodes = nodesetexpand(nodes)

    print('Executing hardware request on nodes ' + str(','.join(nodes)))
    result = pool.map(node_execute_action, nodes)

    # Display result
    print('Execution result:')
    for node_result in result:
        if node_result[0] == 0:
            print('  - ' + str(node_result[1]) + ' : OK')
        elif node_result[0] == -2:
            print('  - ' + str(node_result[1]) + ' : WARNING')
        else:
            print('  - ' + str(node_result[1]) + ' : ERROR')
    # for node in nodesetexpand(nodes):
    #     if not node in hardware_configuration['nodes']:
    #         print("ERROR - node " + str(node) + " not in configuration file.")
    #         continue
    #     node_current_action_protocol = hardware_configuration['nodes'][node][action]['protocol']
    #     node_hardware_plugin = hardware_plugins[node_current_action_protocol]
    #     node_connector = node_hardware_plugin.HardwareConnector()
    #     #return_code = node_hardware_connection[action](action_arguments, node_current_action_parameters)
    #     return_code = getattr(node_connector,action)(node, hardware_configuration['nodes'][node], action_arguments)



