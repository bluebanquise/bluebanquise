import os
import re
import json
import yaml
from flask import Blueprint, render_template, request,jsonify
from flask_restful import Api, Resource, url_for

nodes = Blueprint('nodes', __name__)
api = Api(nodes)

# Define the path to the YAML file
yaml_file_path = 'inventory/cluster/nodes.yml'

#################### MAPPING ####################

# HTTP
class nodes_root(Resource):  # /nodes
    def get(self):
        return nodes_get()
api.add_resource(nodes_root, '/nodes')

class nodes_resource(Resource):  # /nodes/<string:node_id>
    def get(self, node_id):
        return nodes_resource_get(node_id)
    def post(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        return nodes_resource_post(node_id, data)
    def put(self, node_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        return nodes_resource_put(node_id, data)
    def delete(self, node_id):
        return nodes_resource_delete(node_id)
api.add_resource(nodes_resource, '/nodes/<string:node_id>')

class nodes_network_interfaces_root(Resource):  # /nodes/<string:node_id>/network_interfaces
    def get(self, node_id):
        return nodes_network_interfaces_get(node_id)
api.add_resource(nodes_network_interfaces_root, '/nodes/<string:node_id>/network_interfaces')

class nodes_network_interfaces_resource(Resource):  # /nodes/<string:node_id>/network_interfaces/<string:network_interface_id>
    def get(self, node_id, network_interface_id):
        return nodes_network_interfaces_resource_get(node_id, network_interface_id)
    def post(self, node_id, network_interface_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        return nodes_network_interfaces_resource_post(node_id, network_interface_id, data)
    def put(self, node_id, network_interface_id, data=None):
        if data is None: data = json.dumps(request.json)  # Switch between cli and http
        return nodes_network_interfaces_resource_put(node_id, network_interface_id, data)
    def delete(self, node_id, network_interface_id):
        return nodes_network_interfaces_resource_delete(node_id, network_interface_id)
api.add_resource(nodes_network_interfaces_resource, '/nodes/<string:node_id>/network_interfaces/<string:network_interface_id>')

# class nodes_test(Resource):
#     def get(self, node_id):
#         return node_id
#     def post(self, node_id, data=None):
#         if data is None:
#             data = request.json
#         return str(node_id) + str(data)
# api.add_resource(nodes_test, '/nodes/<string:node_id>/test')


# # CLI
# def cli_main(http_method, http_url, data):
#     print("nodes cli main")
#     #print(http_url)
#     #print(http_method)
#     #print(data)
#     if http_url == "nodes" and http_method == "get":  # /nodes
#         return nodes_get()
#     else:
#         node_id = http_url.split('/')[1]
#         if len(http_url.split('/')) == 2:  # /nodes/<string:node_id>
#             if http_method == "get":
#                 return nodes_resource_get(node_id)
#             elif http_method == "post":
#                 return nodes_resource_post(node_id, data)
#             elif http_method == "put":
#                 return nodes_resource_put(node_id, data)
#             elif http_method == "delete":
#                 return nodes_resource_delete(node_id)
#         if len(http_url.split('/')) == 3:  # /nodes/<string:node_id>/{network_interfaces|bmc}
#             if http_url.split('/')[2] == "network_interfaces" and http_method == "get":  # /nodes/<string:node_id>/network_interfaces
#                 return nodes_network_interfaces_get(node_id)
#         elif len(http_url.split('/')) == 4 and http_url.split('/')[2] == "network_interfaces":
#             network_interface_id = http_url.split('/')[3]
#             if http_method == "get":
#                 return nodes_network_interfaces_resource_get(node_id, network_interface_id)
#             elif http_method == "post":
#                 return nodes_network_interfaces_resource_post(node_id, network_interface_id, data)
#             elif http_method == "put":
#                 return nodes_network_interfaces_resource_put(node_id, network_interface_id, data)
#             elif http_method == "delete":
#                 return nodes_network_interfaces_resource_delete(node_id, network_interface_id)

#################### GLOBAL FUNCTIONS ####################
# Load nodes data from the YAML file
def load_nodes_from_file():
    if os.path.exists(yaml_file_path):
        with open(yaml_file_path, 'r') as file:
            nodes = yaml.safe_load(file)['all']['hosts']
            return nodes
    else:
        return {}

# Save nodes data to the YAML file
def save_nodes_to_file(nodes):
    with open(yaml_file_path, 'w') as file:
        all_nodes = {'all': {'hosts': {}}}
        all_nodes['all']['hosts'] = nodes
        yaml.dump(all_nodes, file, default_flow_style=False)


#################### ROOT CALL /nodes ####################
def nodes_get():
    nodes = load_nodes_from_file()
    if nodes is None:
        return {'error': 'No nodes found'}, 400
    nodes_list = []
    for k, v in nodes.items():
        nodes_list.append(k)
    return nodes_list, 200


#################### RESOURCES CALL /nodes/<string:node_id> ####################
def nodes_resource_get(node_id):
    nodes = load_nodes_from_file()
    if nodes is None:
        return {'error': 'No nodes found'}, 400
    if node_id not in nodes:
        return {'error': 'Node ' + node_id + 'not found'}, 400
    return nodes[node_id], 200

def nodes_resource_post(node_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if node_id in nodes:
        return {'error': 'Node already exists'}, 409
    nodes[node_id] = {
        'network_interfaces': [],
        'bmc': {
            'ip4': None,
            'name': None,
            'mac': None,
            'network': None
        }
    }
    nodes[node_id].update(json.loads(data))
    save_nodes_to_file(nodes)
    return {'ok': 'Node added successfully'}, 201

def nodes_resource_put(node_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if node_id not in nodes:
        return {'error': 'Node does not exists'}, 409
    nodes[node_id].update(json.loads(data))
    save_nodes_to_file(nodes)
    return {'ok': 'Node updated successfully'}, 201

def nodes_resource_delete(node_id):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    del nodes[node_id]
    save_nodes_to_file(nodes)
    return {'ok': 'Node deleted successfully'}, 201


#################### ROOT CALL /nodes/<string:node_id>/network_interfaces ####################
def nodes_network_interfaces_get(node_id):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    network_interfaces_list = []
    for nic in nodes[node_id]['network_interfaces']:
        if 'interface' in nic:
            network_interfaces_list.append(nic['interface'])
    return network_interfaces_list, 200

################### RESOURCES CALL /nodes/<string:node_id>/network_interfaces/<string:network_interface_id> ####################
def nodes_network_interfaces_resource_get(node_id, network_interface_id):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    nic_exists = False
    for nic in nodes[node_id]['network_interfaces']:
        if 'interface' in nic:
            if nic['interface'] == network_interface_id:
                nic_exists = True
    if not nic_exists:
        return {'error': 'Network interface does not exists'}, 409
    for nic in nodes[node_id]['network_interfaces']:
        if 'interface' in nic:
            if nic['interface'] == network_interface_id:
                return nic, 200

def nodes_network_interfaces_resource_post(node_id, network_interface_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    nic_exists = False
    for nic in nodes[node_id]['network_interfaces']:
        if 'interface' in nic:
            if nic['interface'] == network_interface_id:
                nic_exists = True
    if nic_exists:
        return {'error': 'Network interface already exists'}, 409
    new_nic = {
        'interface': network_interface_id,
        'type': 'ethernet',
        'state': 'present',
        'skip': False,
        'ip4': None,
        'mac': None,
        'network': None
        }
    new_nic.update(json.loads(data))
    nodes[node_id]['network_interfaces'].append(new_nic)
    save_nodes_to_file(nodes)
    return {'ok': 'Network interface added successfully'}, 201

def nodes_network_interfaces_resource_put(node_id, network_interface_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    nic_exists = False
    for nic in nodes[node_id]['network_interfaces']:
        if 'interface' in nic:
            if nic['interface'] == network_interface_id:
                nic_exists = True
    if not nic_exists:
        return {'error': 'Network interface does not exists'}, 409
    nic_index = -1
    for index, nic in enumerate(nodes[node_id]['network_interfaces']):
        if 'interface' in nic:
            if nic['interface'] == network_interface_id:
                nic_index = index
    nodes[node_id]['network_interfaces'][nic_index].update(json.loads(data))
    save_nodes_to_file(nodes)
    return {'ok': 'Network interface updated successfully'}, 201

def nodes_network_interfaces_resource_delete(node_id, network_interface_id):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    nic_exists = False
    for nic in nodes[node_id]['network_interfaces']:
        if 'interface' in nic:
            if nic['interface'] == network_interface_id:
                nic_exists = True
    if not nic_exists:
        return {'error': 'Network interface does not exists'}, 409
    nic_index = -1
    for index, nic in enumerate(nodes[node_id]['network_interfaces']):
        if 'interface' in nic:
            if nic['interface'] == network_interface_id:
                nic_index = index
    del nodes[node_id]['network_interfaces'][nic_index]
    save_nodes_to_file(nodes)
    return {'ok': 'Network interface deleted successfully'}, 201
