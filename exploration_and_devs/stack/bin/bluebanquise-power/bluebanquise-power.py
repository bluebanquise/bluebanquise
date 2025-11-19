from argparse import ArgumentParser
import os
import yaml
import json
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import importlib


# bluebanquise-power c001/power/on
# bluebanquise-power c001/boot/pxe

# Define the path to the YAML file
configuration_file_path = 'bluebanquise-power.yml'

if os.path.exists(configuration_file_path):
    with open(configuration_file_path, 'r') as file:
        power_configuration = yaml.safe_load(file)

# Get arguments
parser = ArgumentParser()
parser.add_argument("-s", "--server", dest="server",
                    help="Enable or disable server mode", metavar="NODE", default=False)

passed_arguments, cli_request = parser.parse_known_args()


app = Flask(__name__)
api = Api(app)

dyn_modules = {}
to_load_blueprints = []
for file_path in os.listdir('blueprints'):
    # check if current file_path is a file
    if os.path.isfile(os.path.join('blueprints', file_path)):
        to_load_blueprints.append(file_path.replace('.py', ''))
for to_load_blueprint in to_load_blueprints:
    print("Loading '" + to_load_blueprint + "' blueprint")
    dyn_modules[to_load_blueprint] = importlib.import_module('blueprints.' + to_load_blueprint, package='app')
    app.register_blueprint(getattr(dyn_modules[to_load_blueprint], to_load_blueprint))

print(app.url_map)


if passed_arguments.server:
    print("Now running as server")
    print("URLs map:")
    print(app.url_map)
    app.run(debug=True)
    quit()
else:
    print("Now running as cli")

    cli_url = cli_request[0]
    node = cli_request[0].split('/')[0]
    action = cli_request[0].split('/')[1:]

    if len(cli_request[1:]) > 0 and cli_request[1:] is not None:
        cli_data = ' '.join(cli_request[1:])
    else:
        print("Using empty data")
        cli_data = "{}"

    adapter = app.url_map.bind('localhost')
    print("/" + cli_url)
    try:
        url_match = adapter.match("/" + cli_url, method="post")
    except:
        print("Could not found url")
        quit()

    my_cla=getattr(dyn_modules[power_configuration['nodes'][node]['protocol']],url_match[0].split('.')[1])()
    print(getattr(my_cla, "post")(**url_match[1], data=cli_data))
    
    quit()