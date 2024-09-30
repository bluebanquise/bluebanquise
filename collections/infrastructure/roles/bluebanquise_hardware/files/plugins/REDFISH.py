import os
import re
import json
import yaml
from flask import Blueprint, render_template, request,jsonify
from flask_restful import Api, Resource, url_for
import subprocess

REDFISH = Blueprint('REDFISH', __name__)
api = Api(REDFISH)

configuration_file_path = 'bluebanquise-power.yml'

if os.path.exists(configuration_file_path):
    with open(configuration_file_path, 'r') as file:
        power_configuration = yaml.safe_load(file)

#################### MAPPING ####################

# HTTP

class redfish_power_on(Resource):  # /<string:node_id/power/on
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        cmd = ("ipmitool -I lanplus " +
              " -H " + power_configuration['nodes'][node_id]['bmc']['name'] +
              " -U " + power_configuration['nodes'][node_id]['user'] +
              " -P " + power_configuration['nodes'][node_id]['password'] +
              " chassis power on")
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr), "returncode": cmd_call.returncode, "cmd": cmd}

api.add_resource(redfish_power_on, '/<string:node_id>/power/on')
