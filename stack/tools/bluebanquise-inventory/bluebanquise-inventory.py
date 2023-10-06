from argparse import ArgumentParser
import os
import yaml
import json
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import importlib

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

if passed_arguments.server:
    print("Now running as server")
    print("URLs map:")
    print(app.url_map)
    app.run(debug=True)
    quit()
else:
    print("Now running as cli")

    cli_method = cli_request[0]
    if cli_method not in ['get', 'post', 'add', 'delete', 'put', 'update']:
        print('Error, unknown ' + str(cli_method) + ' method')
        quit()
    if cli_method == "add": cli_method = "post"
    if cli_method == "update": cli_method = "put"

    cli_url = cli_request[1]

    if len(cli_request[2:]) > 0 and cli_request[2:] is not None:
        cli_data = ' '.join(cli_request[2:])
    else:
        print("Using empty data")
        cli_data = "{}"

    #print(cli_url.split('/')[0])
    #print(cli_method)
    #print(cli_url)
    #print(cli_data)

    adapter = app.url_map.bind('localhost')
    try:
        url_match = adapter.match("/" + cli_url, method=cli_method)
    except:
        print("Could not found url")
        quit()

    #print(url_match)
    #print(url_match[0])
    my_cla=getattr(dyn_modules[url_match[0].split('.')[0]],url_match[0].split('.')[1])()
    if cli_method in ['post', 'put']:
        print(getattr(my_cla,cli_method)(**url_match[1], data=cli_data))
    else:
        print(getattr(my_cla,cli_method)(**url_match[1]))
    
    quit()
