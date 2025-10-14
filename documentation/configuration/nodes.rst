=====
Nodes
=====

Nodes are defined by default at root level of the inventory.
For convenience, we will store the nodes files and group files inside a dedicated ``cluster/`` folder.

Nodes are always part of 3 groups:

1. A function group, prefixed with ``fn_``. For example: ``fn_management`` or ``fn_compute``, etc.
2. An hardware definition group, prefixed with ``hw_``. For example ``hw_supermicro_X10DRT`` or ``hw_model_A``, etc.
3. An OS definition group, prefixed with ``os_``. For example: ``os_almalinux_9`` or ``os_ubuntu_2404``, etc.

.. note::

  You can create as many groups as you need, as long as they respect the prefixing convention.
  For example, you can split ``hw_supermicro_X10DRT`` into ``hw_supermicro_X10DRT_IBHDR_T40`` and ``hw_supermicro_X10DRT_IBHDR`` for 1 version with a T40 GPU and one version without GPU.

This creates a new **equipment profile** (see vocabulary section of this documentation).

Nodes definition
================

Nodes must always be under ``all`` then and ``hosts`` keys inside their YAML files.

By default, we store all nodes into the same file, ``cluster/nodes.yml``, but nothing prevents from splitting this file into smaller ones.
Just be sure to always start the file with:

.. code-block:: yaml

  all:
    hosts:

Then you can add nodes as dict keys under hosts, using their hostname.

For example:

.. code-block:: yaml

  all:
    hosts:
      mgt1:

Nodes network interfaces
------------------------

Under node hostname, it is possible to define network interfaces, as a list inside ``network_interfaces`` key.
Each new interface must at least contain the interface key as the interface name.

.. code-block:: yaml

  all:
    hosts:
      mgt1:
        network_interfaces:
          - interface: enp0s8

You can then link the interfaces to networks defined before (see networks section), and set their ipv4.
If you plan to deploy the node via this interface over the network (PXE) you will also need to set a way to identify it, like its mac.

.. code-block:: yaml

  all:
    hosts:
      mgt1:
        network_interfaces:
          - interface: enp0s8
            ip4: 10.10.0.1
            mac: 08:00:27:dc:f8:f5
            network: net-1

You can add another interface, for example an infiniband interface, on interconnect network:

.. code-block:: yaml

  all:
    hosts:
      mgt1:
        network_interfaces:
          - interface: enp0s8
            ip4: 10.10.0.1
            mac: 08:00:27:dc:f8:f5
            network: net-1
          - interface: ib0
            ip4: 10.20.0.1
            network: interconnect
            type: infiniband

The full list of available parameters is defined in the nmcli Ansible module `https://ansible.readthedocs.io/projects/ansible/3/collections/community/general/nmcli_module.html <https://ansible.readthedocs.io/projects/ansible/3/collections/community/general/nmcli_module.html>`_.

.. note::
  
  If you are creating your inventory before having access to the cluster, you may not already know the interface name, or even the MAC address.
  You will be able to update it later, once server is reachable.

An example of a file could be for computes nodes:

.. code-block:: yaml

  all:
    hosts:
      c001:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.1
            mac: 08:00:27:dc:f8:a1
            network: net-1
      c002:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.2
            mac: 08:00:27:dc:f8:a2
            network: net-1
      c003:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.3
            mac: 08:00:27:dc:f8:a3
            network: net-1
      c004:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.4
            mac: 08:00:27:dc:f8:a4
            network: net-1

BMC
---

Your server might have a BMC, to manage it over the network.
If so, you can define it under the hostname, along with its network parameters, so it is taken into account:

.. code-block:: yaml

  all:
    hosts:
      mgt1:
        bmc:
          name: bmgt1
          ip4: 10.10.100.1
          network: net-admin
          mac: 2a:2b:3c:4d:5e:6f
        network_interfaces:
          - interface: enp0s8
            ip4: 10.10.0.1
            mac: 08:00:27:dc:f8:f5
            network: net-1
          - interface: ib0
            ip4: 10.20.0.1
            network: interconnect
            type: infiniband

Nodes groups
============

Each node needs to be in at least 3 specific groups:

1. A function group, prefixed with ``fn_``.
2. An hardware definition group, prefixed with ``hw_``.
3. An OS definition group, prefixed with ``os_``.

You can then also add nodes into custom groups for ease, as long as they do not use the 3 reserved prefixes.

Function group
--------------

Function groups define the purpose of the nodes.
Most of the time, these groups are also used to create the associated Ansible playbooks, to define what to configure on nodes of the same function group.

Function groups are always prefixed by ``fn_``.

To add a node in a function group, edit/create file ``cluster/fn`` (not ``cluster/fn.yml`` as this is not a YAML format here, but INI).
Each group is between ``[ ]`` and nodes inside this group are just listed bellow.

.. code-block:: ini

  [fn_management]
  mgt1

  [fn_compute]
  c001
  c002
  c003
  c004

.. note::

  Protip: you can use ranges to define nodes in group files. In this example, the 4 c00X nodes can also be written ``c00[1:4]``.
  BEWARE, this is not Clustershell syntax!

  .. code-block:: ini

    [fn_management]
    mgt1

    [fn_compute]
    c00[1:4]

Operating system group
----------------------

OS groups define the OS related settings of the associated nodes.

OS groups are always prefixed by ``os_``.

To add a node in an OS group, edit/create file ``cluster/os``, like for function groups.

For example:

.. code-block:: ini

  [os_ubuntu_2404]
  mgt1
  c001
  c002
  c003
  c004

Please refer to os settings section of this documentation to learn how to add settings to these groups.

Hardware group
--------------

Hardware groups define the hardware related settings of the associated nodes.

Hardware groups are always prefixed by ``hw_``.

To add a node in an hardware group, edit/create file ``cluster/hw``, like for function groups.

For example:

.. code-block:: ini

  [hw_supermicro_X10DRT]
  mgt1

  [hw_supermicro_X13QEH]
  c00[1:3]

  [hw_supermicro_X13QEH_NvidiaT4_HDR]
  c004

Please refer to hardware settings section of this documentation to learn how to add settings to these groups.

.. note::

  You can check the result of your groups configuration using the ansible-inventory command:

  .. code-block:: text

    (pydevs) oxedions@prima:~/$ ansible-inventory -i inventories/default/ --graph
    @all:
      |--@ungrouped:
      |--@fn_management:
      |  |--mgt1
      |--@fn_compute:
      |  |--c001
      |  |--c002
      |  |--c003
      |  |--c004
      |--@hw_supermicro_X10DRT:
      |  |--mgt1
      |--@hw_supermicro_X13QEH:
      |  |--c001
      |  |--c002
      |  |--c003
      |  |--c004
      |--@os_almalinux_9:
      |  |--mgt1
      |  |--c001
      |  |--c002
      |  |--c003
      |  |--c004
    (pydevs) oxedions@prima:~/$ 


Generate range of nodes
=======================

Since nodes are based on YAML files, it is easy to generate them using a bash script.
A small example is given bellow, please adapt it to your needs.

Create a file /tmp/gen.sh with the following content:

.. code-block:: text

  #!/bin/bash
  cat <<EOF > computes.yml
  all:
    hosts:
  EOF
  for ((i=1;i<=$1;i++)); do
  cat <<EOF >> computes.yml
      c$i:
        bmc:
          name: bc$i
          ip4: 10.10.103.$i
          mac:
          network: ice1-1
        network_interfaces:
          - interface: enp0s9
            ip4: 10.10.3.$i
            mac:
            network: ice1-1
          - interface: ib0
            ip4: 10.20.3.$i
            network: interconnect-1
  EOF
  done

Save, make this script executable, and run it asking for 4 nodes:

.. code-block:: text

  chmod +x /tmp/gen.sh
  /tmp/gen.sh 4

This will generate a file to edit, just need to add MAC addresses once you know them.

Alias
=====

When needed, it is possible to add alias to hosts.

An alias can be added at 3 location:

Global host alias
-----------------

Just add the alias as a list of alias under the host name, this will result in an entry that will be linked to the node hostname.

For example:

.. code-block:: yaml

  all:
    hosts:
      mgt1:
        alias:
          - foobar
        bmc:
          name: bmgt1
          ip4: 10.10.100.1
          network: net-admin
          mac: 2a:2b:3c:4d:5e:6f
        network_interfaces:
          - interface: enp0s8
            ip4: 10.10.0.1
            mac: 08:00:27:dc:f8:f5
            network: net-1
          - interface: ib0
            ip4: 10.20.0.1
            network: interconnect
            type: infiniband

Pinging foobar will endup on 10.10.0.1, like pinging mgt1.

Per nic alias
-------------

You can add the alias inside a nic interface dict, this will result in an entry that will be linked to the node nic.

For example:

.. code-block:: yaml

  all:
    hosts:
      mgt1:
        bmc:
          name: bmgt1
          ip4: 10.10.100.1
          network: net-admin
          mac: 2a:2b:3c:4d:5e:6f
        network_interfaces:
          - interface: enp0s8
            ip4: 10.10.0.1
            mac: 08:00:27:dc:f8:f5
            network: net-1
          - interface: ib0
            alias: foobar
            ip4: 10.20.0.1
            network: interconnect
            type: infiniband

Pinging foobar will endup on 10.20.0.1, like pinging mgt1-ib0.

.. warning::

  If you disabled ``hosts_file_enable_extended_names``, then this nic alias feature will also be disabled.

BMC alias
---------

You can add an alias to the BMC too:

.. code-block:: yaml

  all:
    hosts:
      mgt1:
        bmc:
          name: bmgt1
          alias: foobarbmc
          ip4: 10.10.100.1
          network: net-admin
          mac: 2a:2b:3c:4d:5e:6f
        network_interfaces:
          - interface: enp0s8
            ip4: 10.10.0.1
            mac: 08:00:27:dc:f8:f5
            network: net-1
          - interface: ib0
            ip4: 10.20.0.1
            network: interconnect
            type: infiniband

Pinging foobarbmc will result in pinging 10.10.100.1.
