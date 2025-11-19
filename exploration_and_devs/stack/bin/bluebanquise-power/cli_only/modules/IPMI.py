import os
import re
import json
import yaml
import subprocess


def power(node, node_configuration, action_parameters, parameters):

    if action_parameters[0] == "on":
        cmd = ( "ipmitool -I lanplus " +
            " -H " + node_configuration['bmc']['name'] +
            " -U " + node_configuration['user'] +
            " -P " + node_configuration['password'] +
            " chassis power on"
        )
        if not parameters.get('dryrun', False):
            cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = cmd_call.communicate()
            exit_code = cmd_call.returncode
            if exit_code != 0:
                print('[' + node + '] Error, could not power on node.')
                print('[' + node + '] exit code:')
                print(exit_code)
                print('[' + node + '] stdout:')
                print(stdout)
                print('[' + node + '] stderr:')
                print(stderr)
                return 1
            else:
                print('[' + node + '] Powered on.')
                return 0
        else:
            print('[' + node + '] Dryrun. Cmd: ' + cmd)
            return 0

    elif action_parameters[0] == "off":
        cmd = ( "ipmitool -I lanplus " +
            " -H " + node_configuration['bmc']['name'] +
            " -U " + node_configuration['user'] +
            " -P " + node_configuration['password'] +
            " chassis power off"
        )
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode
        if exit_code != 0:
            print('[' + node + '] Error, could not power off node.')
            print('[' + node + '] exit code:')
            print(exit_code)
            print('[' + node + '] stdout:')
            print(stdout)
            print('[' + node + '] stderr:')
            print(stderr)
            return 1
        else:
            print('[' + node + '] Powered off.')

    elif action_parameters[0] == "reset":
        cmd = ( "ipmitool -I lanplus " +
            " -H " + node_configuration['bmc']['name'] +
            " -U " + node_configuration['user'] +
            " -P " + node_configuration['password'] +
            " chassis power reset"
        )
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode
        if exit_code != 0:
            print('[' + node + '] Error, could not power reset node.')
            print('[' + node + '] exit code:')
            print(exit_code)
            print('[' + node + '] stdout:')
            print(stdout)
            print('[' + node + '] stderr:')
            print(stderr)
            return 1
        else:
            print('[' + node + '] Reseted.')

    elif action_parameters[0] == "status":
        cmd = ( "ipmitool -I lanplus " +
            " -H " + node_configuration['bmc']['name'] +
            " -U " + node_configuration['user'] +
            " -P " + node_configuration['password'] +
            " chassis power status"
        )
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode
        if exit_code != 0:
            print('[' + node + '] Error, could not get node power status.')
            print('[' + node + '] exit code:')
            print(exit_code)
            print('[' + node + '] stdout:')
            print(stdout)
            print('[' + node + '] stderr:')
            print(stderr)
            return 1
        else:
            print('[' + node + '] Power status: ' + stdout)
    else:
        print('[' + node + '] Error, unknown power action ' + action_parameters)
        return 1

def boot(node, node_configuration, action_parameters, passed_arguments):

    if action_parameters[0] == "disk":
        cmd = ( "ipmitool -I lanplus " +
            " -H " + node_configuration['bmc']['name'] +
            " -U " + node_configuration['user'] +
            " -P " + node_configuration['password'] +
            " chassis bootdev disk"
        )
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode
        if exit_code != 0:
            print('[' + node + '] Error, could not set next boot to disk.')
            print('[' + node + '] exit code:')
            print(exit_code)
            print('[' + node + '] stdout:')
            print(stdout)
            print('[' + node + '] stderr:')
            print(stderr)
            return 1
        else:
            print('[' + node + '] Next boot set to disk.')

    elif action_parameters[0] == "bios":
        cmd = ( "ipmitool -I lanplus " +
            " -H " + node_configuration['bmc']['name'] +
            " -U " + node_configuration['user'] +
            " -P " + node_configuration['password'] +
            " chassis bootdev bios"
        )
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode
        if exit_code != 0:
            print('[' + node + '] Error, could not set next boot to bios.')
            print('[' + node + '] exit code:')
            print(exit_code)
            print('[' + node + '] stdout:')
            print(stdout)
            print('[' + node + '] stderr:')
            print(stderr)
            return 1
        else:
            print('[' + node + '] Next boot set to bios.')

    elif action_parameters[0] == "pxe":
        cmd = ( "ipmitool -I lanplus " +
            " -H " + node_configuration['bmc']['name'] +
            " -U " + node_configuration['user'] +
            " -P " + node_configuration['password'] +
            " chassis bootdev pxe"
        )
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode
        if exit_code != 0:
            print('[' + node + '] Error, could not set next boot to pxe.')
            print('[' + node + '] exit code:')
            print(exit_code)
            print('[' + node + '] stdout:')
            print(stdout)
            print('[' + node + '] stderr:')
            print(stderr)
            return 1
        else:
            print('[' + node + '] Next boot set to pxe.')
    
    else:
        print('[' + node + '] Error, unknown boot action ' + action_parameters)
        return 1
