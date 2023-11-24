import os
import re
import json
import yaml
from flask import Blueprint, render_template, request,jsonify
from flask_restful import Api, Resource, url_for
import subprocess

IPMI = Blueprint('IPMI', __name__)
api = Api(IPMI)

configuration_file_path = 'bluebanquise-power.yml'

if os.path.exists(configuration_file_path):
    with open(configuration_file_path, 'r') as file:
        power_configuration = yaml.safe_load(file)

#################### MAPPING ####################

# HTTP

class ipmi_power_on(Resource):  # /<string:node_id/power/on
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

api.add_resource(ipmi_power_on, '/<string:node_id>/power/on')

class ipmi_power_off(Resource):  # /<string:node_id/power/off
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        cmd = ("ipmitool -I lanplus " +
              " -H " + power_configuration['nodes'][node_id]['bmc']['name'] +
              " -U " + power_configuration['nodes'][node_id]['user'] +
              " -P " + power_configuration['nodes'][node_id]['password'] +
              " chassis power off")
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr), "returncode": cmd_call.returncode, "cmd": cmd}

api.add_resource(ipmi_power_off, '/<string:node_id>/power/off')

class ipmi_power_reset(Resource):  # /<string:node_id/power/reset
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        cmd = ("ipmitool -I lanplus " +
              " -H " + power_configuration['nodes'][node_id]['bmc']['name'] +
              " -U " + power_configuration['nodes'][node_id]['user'] +
              " -P " + power_configuration['nodes'][node_id]['password'] +
              " chassis power reset")
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr), "returncode": cmd_call.returncode, "cmd": cmd}

api.add_resource(ipmi_power_reset, '/<string:node_id>/power/reset')

class ipmi_power_status(Resource):  # /<string:node_id/power/status
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        cmd = ("ipmitool -I lanplus " +
              " -H " + power_configuration['nodes'][node_id]['bmc']['name'] +
              " -U " + power_configuration['nodes'][node_id]['user'] +
              " -P " + power_configuration['nodes'][node_id]['password'] +
              " chassis power status")
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr), "returncode": cmd_call.returncode, "cmd": cmd}

api.add_resource(ipmi_power_status, '/<string:node_id>/power/status')


class ipmi_boot_disk(Resource):  # /<string:node_id/boot/disk
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        cmd = ("ipmitool -I lanplus " +
              " -H " + power_configuration['nodes'][node_id]['bmc']['name'] +
              " -U " + power_configuration['nodes'][node_id]['user'] +
              " -P " + power_configuration['nodes'][node_id]['password'] +
              " chassis bootdev disk")
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr), "returncode": cmd_call.returncode, "cmd": cmd}

api.add_resource(ipmi_boot_disk, '/<string:node_id>/boot/disk')

class ipmi_boot_pxe(Resource):  # /<string:node_id/boot/pxe
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        cmd = ("ipmitool -I lanplus " +
              " -H " + power_configuration['nodes'][node_id]['bmc']['name'] +
              " -U " + power_configuration['nodes'][node_id]['user'] +
              " -P " + power_configuration['nodes'][node_id]['password'] +
              " chassis bootdev pxe")
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr), "returncode": cmd_call.returncode, "cmd": cmd}

api.add_resource(ipmi_boot_pxe, '/<string:node_id>/boot/pxe')

class ipmi_boot_bios(Resource):  # /<string:node_id/boot/bios
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        cmd = ("ipmitool -I lanplus " +
              " -H " + power_configuration['nodes'][node_id]['bmc']['name'] +
              " -U " + power_configuration['nodes'][node_id]['user'] +
              " -P " + power_configuration['nodes'][node_id]['password'] +
              " chassis bootdev bios")
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        return {"stdout": str(stdout), "stderr": str(stderr), "returncode": cmd_call.returncode, "cmd": cmd}

api.add_resource(ipmi_boot_bios, '/<string:node_id>/boot/bios')