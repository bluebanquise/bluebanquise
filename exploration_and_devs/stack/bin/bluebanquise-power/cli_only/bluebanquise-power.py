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

for file_path in os.listdir('modules'):
    # check if current file_path is a file
    if os.path.isfile(os.path.join('modules', file_path)):
        print("Loading '" + file_path.replace('.py', '') + "' module")
        power_modules[file_path.replace('.py', '')] = importlib.import_module('modules.' + file_path.replace('.py', ''), package='app')

nodes = NodeSet(cli_request[0])
action = cli_request[1]
action_parameters = cli_request[2:]

for node in nodes:
    if node in power_configuration['nodes']:
        node_configuration = power_configuration['nodes'][node]
        node_protocol = node_configuration['protocol']
        getattr(power_modules[node_protocol],action)(node, node_configuration, action_parameters, parameters)
    else:
        print('Error: node ' + node + ' not found in configuration file. Skipping.')

quit()