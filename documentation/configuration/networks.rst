========
Networks
========

=================
Configure Network
=================

BlueBanquise networking relies on the ``networks`` dict definition in the Ansible inventory, and on nodes ``network_interfaces`` definitions.

Understanding logic
===================

Before listing available parameters, it is important to understand the network logic.

Under ``networks`` key: each network listed that starts with previx ``net_`` is considered a management network, while other networks are considered basic networks.
A management network is designed to host low level vital resources, like DHCP, DNS, NTP, PXE, BMCs management (IPMI/RedFish), etc, while basic networks are designed to host all other usages, like data transfers, calculations exchanges, etc.

Under ``network_interfaces`` of a node:

1. First interface in the list is considered by the stack the "ping" (node_main_resolution) interface, and so resolving direct node hostname will end up on this interface
2. First interface in the list, linked to a management network, is considered by the stack being the node deployment interface (node_main_network), and so is used by PXE and Ansible (ssh) to deploy and reach the node.

The logic behind is the following:

.. code-block:: yaml

  j2_node_main_resolution_network: "{{ network_interfaces[0].network | default(none) }}"
  j2_node_main_resolution_address: "{{ (network_interfaces[0].ip4 | default('')).split('/')[0] | default(none) }}"
  j2_node_main_network: "{{ network_interfaces | default([]) | selectattr('network','defined') | selectattr('network','match','^'+j2_current_iceberg_network+'-[a-zA-Z0-9]+') | map(attribute='network') | list | first | default(none) }}"
  j2_node_main_network_interface: "{{ network_interfaces[j2_node_main_network].interface | default(none) }}"
  j2_node_main_address: "{{ network_interfaces[j2_node_main_network].ip4 | default(none) }}"

Networks definition
===================

Networks are defined under ``networks`` dict key. While in normal time in ``inventory/group_vars/all/networks.yml`` file, the networks definition can be defined at multiple places in the inventory (groups, hosts, etc.) to allow sophisticated configurations.
For example, if ``networks`` configuration must be different on node **login1** than on the other nodes, it is possible to create folder ``inventory/host_vars/login1/``, and redefine networks here, so that **login1** will inherit this configuration instead of the global one.

Note that while IPv4 is supported everywhere, IPv6 is only experimentaly supported by most roles of the stack. If you need full IPv6 support, please open a Feature request.

Mandatory keys
--------------

The bare minimal to define a network is the following:

.. code-block:: yaml

  networks:
    net-1:
      subnet: 10.10.0.0
      prefix: 16

``subnet`` and ``prefix`` keys are mandatory.

Gateway and routes
------------------

It is possible to define a gateway or custom routes for a network.

To define a single gateway, use ``gateway4`` (``gateway4`` replaces ``gateway`` which is now deprecated):

.. code-block:: yaml

  networks:
    net-1:
      subnet: 10.10.0.0
      prefix: 16
      gateway4: 10.10.2.1

Or to define mutliple gateways, define ``gateway4`` as a list:

.. code-block:: yaml

  networks:
    net-1:
      subnet: 10.10.0.0
      prefix: 16
      gateway4:
        - 10.10.2.1
        - 10.10.2.2

If you need to define routes, it is possible to use the ``routes4`` list to define your routes.
Format then is the following: ``<subnet/prefix> <gateway> <metric>``

.. code-block:: yaml

  networks:
    net-1:
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
    net-1:
      subnet: 10.10.0.0
      prefix: 16
      mtu: 9000



add network
-----------

|
.. image:: images/configure_bluebanquise/management1_2.svg
   :align: center
|

Lets now add the network. All our hosts will be connected to a network ``10.10.0.0/16`` called ``net-1``.

Create file ``group_vars/all/networks.yml`` with the following content:

.. code-block:: yaml

  networks:
    net-1:
      subnet: 10.10.0.0
      prefix: 16

In BlueBanquise, nodes are connected together through networks. Most
of the time, logical networks will match your physical network, but for advanced
networking, it can be different.

All networks are defined in ``group_vars/all/networks.yml`` file.

It is **IMPORTANT** to understand that the prefix ``net-`` means to the stack "this is a administration network".

In BlueBanquise there are two kind of networks: **administration networks**, and **simple networks**.

Any network starting its name with prefix ``net-`` will be considered an admininstration network. All other networks will be considered simple networks.

An **administration network** is used to deploy and manage the nodes. It will be for
example used to run a DHCP server, handle the PXE stack, etc, and also all the
Ansible ssh connections. Administration networks have a strict naming
convention, which by default is: ``net-``.


Network settings
----------------

Networks are set as a dict (not a list).

The order doesnt matter, but naming follows a specific rule:
each network starting with prefix ``net-`` is considered an administration network, other networks are considered simple networks.
Admininstration networks are used to deploy systems (PXE, DHCP, etc.) and to handle all vital services (DNS, NTP, etc.). Note that 
most roles take into account if a network is an administration network or not.

For each network, the following parameters are available:

- **prefix**: (mandatory) define the prefix of the network.
- **subnet**: (mandatory) define the subnet of the network.
- **gateway**: define the ip4 gateway of the network if exists.
- **dhcp_server**: add this network (and all linked hosts) to the dhcp server (default True).
- **dns_server**: add this network (and all linked hosts) to the dns server (default True).
- **shared_network**: name of the shared network if exists.
- **services_ip**: allows to define all services ip of the network in once, using a single ip for all (meaning a single management hosts for this network).

Example:

.. code-block:: yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0
      dhcp_server: true
      gateway: 10.10.0.1
      services_ip: 10.10.0.1
    interconnect:
      prefix: 16
      subnet: 10.20.0.0

- **services**: allows to define services ip of the network with more capabilities. Each known service takes an hostname and an ip.
  This can be used for example when services are distributed over multiple management hosts, or when services are using floating virtual ip.

Example:

.. code-block:: yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0
      services:
        dns:
          - ip4: 10.10.0.2
            hostname: mg2-dns4
          - ip4: 8.8.8.8
            hostname: google-public-dns
        pxe:
          - ip4: 10.10.0.1
            hostname: mg1-pxe
        ntp:
          - ip4: 10.10.0.4
            hostname: mg4-time
    interconnect:
      prefix: 16
      subnet: 10.20.0.0

.. note::
  `4` or `6` at end of some keys are related to ipv4 or ipv6, but the ipv6 support is for now limited (if needed, please open a feature request).
