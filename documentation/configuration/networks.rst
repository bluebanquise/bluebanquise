========
Networks
========

BlueBanquise networking relies on the ``networks`` dict definition in the Ansible inventory, and on nodes ``network_interfaces`` definitions.

Understanding logic
===================

Before listing available parameters, it is important to understand the network logic.

Under ``networks`` key: each network listed that starts with previx ``net-`` is considered **a management network** (also refered as an administration network), while other networks are considered basic networks.
A management network is designed to host low level vital resources, like DHCP, DNS, NTP, PXE, BMCs management (IPMI/RedFish), etc, while basic networks are designed to host all other usages, like data transfers, calculations exchanges, etc.

Under ``network_interfaces`` of a node:

1. First interface in the list is considered by the stack the "ping" (node_main_resolution) interface, and so resolving direct node hostname will end up on this interface
2. First interface in the list, linked to a management network, is considered by the stack being the node deployment interface (node_main_network), and so is used by PXE and Ansible (ssh) to deploy and reach the node.

If you need, you can check the logic code (Jinja2) in the vars plugin of bluebanquise infrastructure collection.

Networks definition
===================

Networks are defined under ``networks`` dict key. While in normal time in ``group_vars/all/networks.yml`` file, the networks definition can be defined at multiple places in the inventory (groups, hosts, etc.) to allow sophisticated configurations.
For example, if ``networks`` configuration must be different on node **login1** than on the other nodes, it is possible to create folder ``host_vars/login1/``, and redefine networks here, so that **login1** will inherit this configuration instead of the global one.

Note that while IPv4 is supported everywhere, IPv6 is only experimentaly supported by most roles of the stack. If you need full IPv6 support, please open a Feature request on github.

Mandatory keys
--------------

The bare minimal to define a network is the following:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16

``subnet`` and ``prefix`` keys are mandatory.

Gateway and routes
------------------

It is possible to define a gateway or custom routes for a network.

To define a gateway, use ``gateway4`` (``gateway4`` replaces ``gateway`` which is now deprecated):

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      gateway4: 10.10.2.1

If you need to define routes, it is possible to use the ``routes4`` list to define your routes.
Format then is the following: ``<subnet/prefix> <gateway> <metric>``, metric being optional.

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      routes4:
        - 10.11.0.0/24 10.10.0.2
        - 10.12.0.0/24 10.10.0.2 300

MTU
---

It is possible to define an MTU for a whole network, using the ``mtu`` key:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      mtu: 9000
