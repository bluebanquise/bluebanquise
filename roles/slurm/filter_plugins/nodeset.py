# -*- coding: utf-8 -*-
#
# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ClusterShell.NodeSet import NodeSet

def nodeset(nodes_list):
    '''Convert a list of nodes to ClusterShell's NodeSet'''
    nodeset = NodeSet(",".join(nodes_list))
    return nodeset

class FilterModule(object):
    ''' NodeSet Jinja2 filter. '''

    def filters(self):
        return {
            'nodeset': nodeset,
        }
