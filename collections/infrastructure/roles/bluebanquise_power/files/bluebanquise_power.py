#!/usr/bin/env python3
from argparse import ArgumentParser
import os
import yaml
import json
import importlib
from ClusterShell.NodeSet import NodeSet

# bluebanquise-power c001 power on

# Define the path to the YAML file
configuration_file_path = 'bluebanquise-power.yml'

if os.path.exists(configuration_file_path):
    with open(configuration_file_path, 'r') as file:
        power_configuration = yaml.safe_load(file)

# Get arguments
parser = ArgumentParser()
#parser.add_argument('-p', action='store', dest='param', default=UNSPECIFIED, nargs='?')
parser.add_argument("--dryrun", action='store', dest='dryrun', nargs='?', const=True, help="Enable dryrun mode")
parser.add_argument("--debug", action='store', dest='debug', nargs='?', const=True, help="Enable debug mode")

passed_arguments, cli_request = parser.parse_known_args()

parameters = vars(passed_arguments)

power_modules = {}
plugins_dir = '/usr/share/bluebanquise/bluebanquise-power'

# Load plugins from the specified directory
power_modules = {}
for file_path in os.listdir(plugins_dir):
    if file_path.endswith('.py') and os.path.isfile(os.path.join(plugins_dir, file_path)):
        module_name = file_path.replace('.py', '')
        module_path = f"{plugins_dir}.{module_name}"
        print("Loading '" + module_name + "' plugin")
        power_modules[module_name] = importlib.import_module(f"{plugins_dir}.{module_name}")

nodes = NodeSet(cli_request[0])
action = cli_request[1]
action_parameters = cli_request[2:]

for node in nodes:
    if node in power_configuration['nodes']:
        node_configuration = power_configuration['nodes'][node]
        node_protocol = node_configuration['protocol']
        return_code = getattr(power_modules[node_protocol],action)(node, node_configuration, action_parameters, parameters)
        if return_code != 0:
            print('Error on node ' + node)
    else:
        print('Error: node ' + node + ' not found in configuration file. Skipping.')

quit()
