import os
import re
import json
import yaml
from flask import Blueprint, render_template, request,jsonify
from flask_restful import Api, Resource, url_for
import configparser

roles = Blueprint('roles', __name__)
api = Api(roles)

# Define the path to the YAML file
inventory_path = 'inventory'
inventory_cluster_groups_path = {}
inventory_cluster_groups_path['groups'] = inventory_path + '/cluster/groups'
inventory_cluster_groups_path['equipments'] = inventory_path + '/cluster/equipments'
inventory_cluster_groups_path['roles'] = inventory_path + '/cluster/roles'

#################### MAPPING ####################

# HTTP
class roles_root(Resource):  # /roles
    def get(self):
        return roles_get()
api.add_resource(roles_root, '/roles')

#################### GLOBAL FUNCTIONS ####################
# Load roles and nodes related
def load_roles():
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(inventory_cluster_groups_path['roles'])
    return config

#################### ROOT CALL /nodes ####################
def roles_get():
    roles = load_roles()
    roles_list = []
    for role, role_nodes in roles.items():
        roles_list.append(role)
    return roles_list, 200
