# -*- coding: utf-8 -*-
#
# Make coding more python3-ish
# Original idea from Bruno Travouillon, @btravouillon

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ClusterShell.NodeSet import NodeSet
from ansible.module_utils.common.text.converters import to_native


def nodeset(nodes_list):
    '''Convert a list of nodes to ClusterShell's NodeSet'''

    try:
        nodeset = NodeSet(",".join(nodes_list))
    except Exception as e:
        raise AnsibleError('Error joining nodeset, original exception: %s' % to_native(e))

    return nodeset


class FilterModule(object):
    ''' NodeSet Jinja2 filter. '''

    def filters(self):
        return {
            'nodeset': nodeset,
        }