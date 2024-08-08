import os
import re
import json
import yaml
from flask import Blueprint, render_template, request,jsonify
from flask_restful import Api, Resource, url_for

bootstrap = Blueprint('bootstrap', __name__)
api = Api(bootstrap)

# Define the path to the YAML file
yaml_file_path = 'inventory/cluster/nodes.yml'

#################### MAPPING ####################

# HTTP
class bootstrap_root(Resource):  # /bootstrap
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http

        return 
api.add_resource(bootstrap_root, '/bootstrap')

example= """
cluster:
  nodes:
    cc[001-004]:
      bmc:
        name: bcc[001-004]
        ip4: 10.10.100.[1-4]
        mac:
          - ZX.XX.XX.XX.XX
          - ZA.AA.AA.AA.AA
          - ZB.BB.BB.BB.BB
          - ZC.CC.CC.CC.CC
        network: net-bmc
      network_interfaces:
        - interface: eno1
          ip4: 10.10.0.[1-4]
          mac:
            - XX.XX.XX.XX.XX
            - AA.AA.AA.AA.AA
            - BB.BB.BB.BB.BB
            - CC.CC.CC.CC.CC
          network: net-admin
        - interface: ib0
          ip4: 10.10.20.[1-4]
          network: ib
  equipments:
    - name: ep_type_A
      nodes: cc001
      settings:
        ep_equipment_type: server
        ep_operating_system:
          distribution: ubuntu
          distribution_version: 22.04
          distribution_major_version: 22
    - name: ep_type_B
      nodes: cc[002-004]
      settings:
        ep_equipment_type: server
        ep_operating_system:
          distribution: ubuntu
          distribution_version: 22.04
          distribution_major_version: 22
  managements: cc001
  networks:
    net-admin:
        prefix: 16
        subnet: 10.10.0.0
        dhcp_server: true
        dns_server: true
        services_ip: 10.10.0.1
    net-bmc:
        prefix: 16
        subnet: 10.10.100.0
    ib:
        prefix: 16
        subnet: 10.10.20.0
"""