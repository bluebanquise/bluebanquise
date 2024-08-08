from argparse import ArgumentParser
import os
import yaml
import json
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import importlib
import logging


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


logging.basicConfig(level=logging.INFO)


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
    logging.debug(bcolors.OKBLUE + "Loading '" + to_load_blueprint + "' blueprint" + bcolors.ENDC)
    dyn_modules[to_load_blueprint] = importlib.import_module('blueprints.' + to_load_blueprint, package='app')
    app.register_blueprint(getattr(dyn_modules[to_load_blueprint], to_load_blueprint))

if passed_arguments.server:
    logging.info(bcolors.OKGREEN + "Running as server" + bcolors.ENDC)
    logging.info(bcolors.OKBLUE + "URLs map:" + bcolors.ENDC)
    logging.info(app.url_map)
    app.run(debug=True)
    quit()
else:
    logging.debug(bcolors.OKGREEN + "Running as CLI" + bcolors.ENDC)
    logging.debug(bcolors.OKBLUE + "URLs map:" + bcolors.ENDC)
    logging.debug(app.url_map)

    if len(cli_request) == 0:
        logging.error('Error, no URL passed')
        quit()

    cli_method = cli_request[0]
    if cli_method not in ['get', 'post', 'add', 'del', 'delete', 'put', 'update']:
        logging.error('Error, unknown ' + str(cli_method) + ' method')
        quit()
    if cli_method == "add": cli_method = "post"
    if cli_method == "update": cli_method = "put"
    if cli_method == "del": cli_method = "delete"

    cli_url = cli_request[1]

    if len(cli_request[2:]) > 0 and cli_request[2:] is not None:
        cli_data = ' '.join(cli_request[2:])
    else:
        logging.debug("Using empty data")
        cli_data = "{}"
    
    if "=" in cli_data:
        cli_data = '{"' + cli_data.replace('=','":"').replace(',','","') + '"}'
    try:
        cli_data = json.loads(cli_data)
    except:
        logging.error("Failed to read data")
        quit()

    adapter = app.url_map.bind('localhost')
    try:
        url_match = adapter.match("/" + cli_url, method=cli_method)
    except:
        logging.error("Could not found URL")
        quit()

    my_cla=getattr(dyn_modules[url_match[0].split('.')[0]],url_match[0].split('.')[1])()
    if cli_method in ['post', 'put']:
        output, error_code = getattr(my_cla,cli_method)(**url_match[1], data=cli_data)
    else:
        output, error_code = getattr(my_cla,cli_method)(**url_match[1])
    try:
        print("YAML output:\n")
        print(yaml.dump(yaml.safe_load(str(output))))
    except:
        print("RAW output:\n")
        print(output)
    print("End of line")
    if error_code != 200:
        quit(1)
    else:
        quit(0)
