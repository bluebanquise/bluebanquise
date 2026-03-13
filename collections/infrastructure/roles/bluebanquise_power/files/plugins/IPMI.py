import os
import re
import json
import yaml
import subprocess

def execute_ipmi_command(node, node_configuration, command):
    cmd = (
        "ipmitool -I lanplus " +
        "-H " + node_configuration['bmc']['name'] +
        " -U " + node_configuration['user'] +
        " -P " + node_configuration['password'] +
        " " + command
    )

    cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = cmd_call.communicate()
    exit_code = cmd_call.returncode

    if exit_code != 0:
        print(f'[{node}] Error executing IPMI command.')
        print(f'[{node}] exit code: {exit_code}')
        print(f'[{node}] stdout: {stdout.decode()}')
        print(f'[{node}] stderr: {stderr.decode()}')
        return 1
    else:
        return 0, stdout.decode()

def power(node, node_configuration, action_parameters, parameters):
    if action_parameters[0] == "on":
        if not parameters.get('dryrun', False):
            exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power on")
            if exit_code == 0:
                print(f'[{node}] Powered on.')
                return 0
            else:
                return 1
        else:
            cmd = (
                "ipmitool -I lanplus " +
                "-H " + node_configuration['bmc']['name'] +
                " -U " + node_configuration['user'] +
                " -P " + node_configuration['password'] +
                " chassis power on"
            )
            print(f'[{node}] Dryrun. Cmd: {cmd}')
            return 0

    elif action_parameters[0] == "off":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power off")
        if exit_code == 0:
            print(f'[{node}] Powered off.')
            return 0
        else:
            return 1

    elif action_parameters[0] == "reset":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power reset")
        if exit_code == 0:
            print(f'[{node}] Reset.')
            return 0
        else:
            return 1

    elif action_parameters[0] == "status":
        exit_code, stdout = execute_ipmi_command(node, node_configuration, "chassis power status")
        if exit_code == 0:
            print(f'[{node}] Power status: {stdout}')
            return 0
        else:
            return 1

    else:
        print(f'[{node}] Error, unknown power action {action_parameters[0]}')
        return 1

def boot(node, node_configuration, action_parameters, parameters):
    if action_parameters[0] == "disk":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev disk")
        if exit_code == 0:
            print(f'[{node}] Next boot set to disk.')
            return 0
        else:
            return 1

    elif action_parameters[0] == "bios":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev bios")
        if exit_code == 0:
            print(f'[{node}] Next boot set to BIOS.')
            return 0
        else:
            return 1

    elif action_parameters[0] == "pxe":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev pxe")
        if exit_code == 0:
            print(f'[{node}] Next boot set to PXE.')
            return 0
        else:
            return 1

    else:
        print(f'[{node}] Error, unknown boot action {action_parameters[0]}')
        return 1
