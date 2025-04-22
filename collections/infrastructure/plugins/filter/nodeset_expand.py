# -*- coding: utf-8 -*-
#
# Make coding more python3-ish
# Original idea from Bruno Travouillon, @btravouillon

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ClusterShell.NodeSet import NodeSet
from ClusterShell.NodeSet import expand
from ansible.module_utils.common.text.converters import to_native


def nodeset_expand(nodes_list):
    '''Convert a list of nodes to expanded ClusterShell's NodeSet'''

    try:
        nodeset_expand = ",".join(expand(NodeSet(",".join(nodes_list))))
    except Exception as e:
        raise AnsibleError('Error joining nodeset, original exception: %s' % to_native(e))

    return nodeset_expand

class FilterModule(object):
    ''' NodeSet Jinja2 filter. '''

    def filters(self):
        return {
            'nodeset_expand': nodeset_expand,
        }
