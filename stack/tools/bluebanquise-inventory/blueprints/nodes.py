import os
import re
import json
import yaml
from flask import Blueprint, render_template, request,jsonify
from flask_restful import Api, Resource, url_for
import configparser

nodes = Blueprint('nodes', __name__)
api = Api(nodes)

# Define the path to the YAML file
inventory_path = 'inventory'
inventory_cluster_nodes_path = inventory_path + '/cluster/nodes.yml'
inventory_cluster_groups_path = {}
inventory_cluster_groups_path['groups'] = inventory_path + '/cluster/groups'
inventory_cluster_groups_path['equipments'] = inventory_path + '/cluster/equipments'
inventory_cluster_groups_path['roles'] = inventory_path + '/cluster/roles'

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
        if data is None: data = request.json  # Switch between cli and http
        return nodes_resource_post(node_id, data)
    def put(self, node_id, data=None):
        if data is None: data = request.json  # Switch between cli and http
        return nodes_resource_put(node_id, data)
    def delete(self, node_id):
        return nodes_resource_delete(node_id)
api.add_resource(nodes_resource, '/nodes/<string:node_id>')

class nodes_bmc_root(Resource):  # /nodes/<string:node_id>/bmc
    def get(self, node_id):
        return nodes_bmc_resource_get(node_id)
    def post(self, node_id, data=None):
        if data is None: data = request.json  # Switch between cli and http
        return nodes_bmc_resource_post(node_id, data)
    def put(self, node_id, data=None):
        if data is None: data = request.json  # Switch between cli and http
        return nodes_bmc_resource_put(node_id, data)
    def delete(self, node_id):
        return nodes_bmc_resource_delete(node_id)
api.add_resource(nodes_bmc_root, '/nodes/<string:node_id>/bmc')

class nodes_network_interfaces_root(Resource):  # /nodes/<string:node_id>/network_interfaces
    def get(self, node_id):
        return nodes_network_interfaces_get(node_id)
api.add_resource(nodes_network_interfaces_root, '/nodes/<string:node_id>/network_interfaces')

class nodes_network_interfaces_resource(Resource):  # /nodes/<string:node_id>/network_interfaces/<string:network_interface_id>
    def get(self, node_id, network_interface_id):
        return nodes_network_interfaces_resource_get(node_id, network_interface_id)
    def post(self, node_id, network_interface_id, data=None):
        if data is None: data = request.json  # Switch between cli and http
        return nodes_network_interfaces_resource_post(node_id, network_interface_id, data)
    def put(self, node_id, network_interface_id, data=None):
        if data is None: data = request.json  # Switch between cli and http
        return nodes_network_interfaces_resource_put(node_id, network_interface_id, data)
    def delete(self, node_id, network_interface_id):
        return nodes_network_interfaces_resource_delete(node_id, network_interface_id)
api.add_resource(nodes_network_interfaces_resource, '/nodes/<string:node_id>/network_interfaces/<string:network_interface_id>')

#################### GLOBAL FUNCTIONS ####################
# Load nodes data from the YAML file
def load_nodes_from_file():
    if os.path.exists(inventory_cluster_nodes_path):
        with open(inventory_cluster_nodes_path, 'r') as file:
            nodes = yaml.safe_load(file)['all']['hosts']
            return nodes
    else:
        return {}

# Save nodes data to the YAML file
def save_nodes_to_file(nodes):
    with open(inventory_cluster_nodes_path, 'w') as file:
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
    node_data = nodes[node_id]
    node_groups = get_node_groups(node_id, "equipments")
    for group in node_groups:
        if group.startswith('ep_'): node_data['equipment'] = group
    node_groups = get_node_groups(node_id, "roles")
    for group in node_groups:
        if group.startswith('mg_'): node_data['role'] = group
    return node_data, 200

def nodes_resource_post(node_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if node_id in nodes: # Check node doesnt already exist
        return {'error': 'Node already exists'}, 409
    if not 'equipment' in data:
        return {'error': 'Missing node equipment'}, 400
    else:
        equipment = data.pop('equipment')
        if not equipment.startswith('ep_'):
            return {'error': 'Node equipment must start with "ep_" prefix'}, 400
    if not 'role' in data:
        return {'error': 'Missing node role'}, 400
    else:
        role = data.pop('role')
        if not role.startswith('mg_'):
            return {'error': 'Node role must start with "mg_" prefix'}, 400
    nodes[node_id] = {
        'network_interfaces': [],
        'bmc': {
            'ip4': None,
            'name': None,
            'mac': None,
            'network': None
        }
    }
    nodes[node_id].update(data)
    save_nodes_to_file(nodes)
    add_node_to_group(node_id, equipment, "equipments")
    add_node_to_group(node_id, role, "roles")
    return {'ok': 'Node added successfully'}, 201

def nodes_resource_put(node_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file() # Check node effectively exists
    if node_id not in nodes:
        return {'error': 'Node does not exists'}, 409
    if 'equipment' in data: # Request an equipment update
        equipment = data.pop('equipment')
        if not equipment.startswith('ep_'):
            return {'error': 'Node equipment must start with "ep_" prefix'}, 400
        node_groups = get_node_groups(node_id, "equipments")
        for group in node_groups:
            if group.startswith('ep_'): del_node_from_group(node_id, group, "equipments")
        add_node_to_group(node_id, equipment, "equipments")
    if 'role' in data: # Request a role update
        role = data.pop('role')
        if not role.startswith('mg_'):
            return {'error': 'Node role must start with "mg_" prefix'}, 400
        node_groups = get_node_groups(node_id, "roles")
        for group in node_groups:
            if group.startswith('mg_'): del_node_from_group(node_id, group, "roles")
        add_node_to_group(node_id, role, "roles")
    # Now update other parameters
    nodes[node_id].update(data)
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
    for group_type in ["equipments", "roles", "groups"]:
        node_groups = get_node_groups(node_id, group_type)
        for group in node_groups:
            del_node_from_group(node_id, group, group_type)
    return {'ok': 'Node deleted successfully'}, 201


#################### RESOURCES CALL /nodes/<string:node_id>/bmc ####################
def nodes_bmc_resource_get(node_id):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    return nodes[node_id]['bmc'], 200

def nodes_bmc_resource_post(node_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    new_bmc = {
            'ip4': None,
            'name': None,
            'mac': None,
            'network': None
        }
    new_bmc.update(data)
    nodes[node_id]['bmc'] = new_bmc
    save_nodes_to_file(nodes)
    return {'ok': 'Bmc added successfully'}, 201

def nodes_bmc_resource_put(node_id, data):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    nodes[node_id]['bmc'].update(data)
    save_nodes_to_file(nodes)
    return {'ok': 'Bmc updated successfully'}, 201

def nodes_bmc_resource_delete(node_id):
    if node_id is None:
        return {'error': 'Missing node_id'}, 400
    nodes = load_nodes_from_file()
    if not node_id in nodes:
        return {'error': 'Node does not exists'}, 409
    new_bmc = {
            'ip4': None,
            'name': None,
            'mac': None,
            'network': None
        }
    nodes[node_id]['bmc'] = new_bmc
    save_nodes_to_file(nodes)
    return {'ok': 'Bmc deleted successfully'}, 201

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
    new_nic.update(data)
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
    nodes[node_id]['network_interfaces'][nic_index].update(data)
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

def add_node_to_group(node_id, group_name, group_type):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(inventory_cluster_groups_path[group_type])
    if not group_name in config:
        config[group_name] = {}
    config[group_name][node_id] = None
    with open(inventory_cluster_groups_path[group_type], 'w') as configfile:
        config.write(configfile)
    return

def get_node_groups(node_id, group_type):
    node_groups = []
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(inventory_cluster_groups_path[group_type])
    for group, nodes in config.items():
        if node_id in nodes:
            node_groups.append(group)
    return node_groups

def del_node_from_group(node_id, group_name, group_type):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(inventory_cluster_groups_path[group_type])
    config[group_name].pop(node_id)
    with open(inventory_cluster_groups_path[group_type], 'w') as configfile:
        config.write(configfile)
    return
