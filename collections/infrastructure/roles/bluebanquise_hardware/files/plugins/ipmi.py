# IPMI legacy protocol
import logging
import subprocess

logger = logging.getLogger(__name__)

# This function executes a cmd in a subprocess and returns stdout, stderr and exit code
# stdout and stderr are decoded
def sub_exec(node, cmd, dryrun=False):
    logging.debug('[' + node + '][sub_exec] Executing ' + cmd)
    if not dryrun:
        cmd_call = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
            )
        stdout, stderr = cmd_call.communicate()
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        exit_code = cmd_call.returncode
        if exit_code != 0:
            logging.error('[' + node + '][sub_exec] command failed!')
            logging.error('[' + node + '][sub_exec] cmd: ' + cmd)
            logging.error('[' + node + '][sub_exec] exit_code: ' + str(exit_code))
            logging.error('[' + node + '][sub_exec] stdout: ' + stdout)
            logging.error('[' + node + '][sub_exec] stderr: ' + stderr)
        else:
            logging.debug('[' + node + '][sub_exec] exit_code: ' + str(exit_code))
            logging.debug('[' + node + '][sub_exec] stdout: ' + stdout)
            logging.debug('[' + node + '][sub_exec] stderr: ' + stderr)
        return str(stdout), str(stderr), exit_code
    else:
        print('[' + node + '][sub_exec] /!\ dryrun /!\ - Executing ' + cmd)
        return '', '', 0

class HardwareConnector(object):

    def __init__(self, dryrun=False):
        # IPMI does not need any kind of init procedure
        self.dryrun = dryrun
        return None

    def power(self, node, node_items, action_arguments):
        logging.debug('[' + node + '] TOTO')
        if action_arguments == 'on':
            cmd = (
                "ipmitool -I lanplus" +
                " -H " + node_items['bmc'] +
                " -U " + node_items['power']['parameters']['user'] +
                " -P " + node_items['power']['parameters']['password'] +
                " chassis power on"
            )
            stdout, stderr, exit_code = sub_exec(node, cmd, self.dryrun)
        if action_arguments == 'off':
            cmd = (
                "ipmitool -I lanplus" +
                " -H " + node_items['bmc'] +
                " -U " + node_items['power']['parameters']['user'] +
                " -P " + node_items['power']['parameters']['password'] +
                " chassis power off"
            )
            stdout, stderr, exit_code = sub_exec(node, cmd, self.dryrun)
            
        return exit_code