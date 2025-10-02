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

The full list of available parameters is defined in the nmcli Ansible module `https://ansible.readthedocs.io/projects/ansible/3/collections/community/general/nmcli_module.html<https://ansible.readthedocs.io/projects/ansible/3/collections/community/general/nmcli_module.html>`_.

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

Hardware group
--------------



Now edit file ``cluster/groups/fn`` (INI file) with the following content:

.. code-block:: ini

  [fn_management]
  management1

  [fn_compute]
  compute[1:4]

We will assume in this example that these servers are supermicro_X13QEH and that we are going to deploy AlmaLinux 9 (like management1) on it.
So it means these servers will share the same os group than management1, but will have a different hw group.

Edit file ``cluster/groups/hw`` (INI file) with the following content:

.. code-block:: ini

  [hw_supermicro_X10DRT]
  management1

  [hw_supermicro_X13QEH]
  compute[1:4]

Then Edit file ``cluster/groups/os`` (INI file) with the following content:

.. code-block:: ini

  [os_almalinux_9]
  management1
  compute[1:4]

Now check the result:

.. code-block:: text

  (pydevs) oxedions@prima:~/tmp_devs$ ansible-inventory -i inventory/ --graph
  @all:
    |--@ungrouped:
    |--@fn_management:
    |  |--management1
    |--@fn_compute:
    |  |--compute1
    |  |--compute2
    |  |--compute3
    |  |--compute4
    |--@hw_supermicro_X10DRT:
    |  |--management1
    |--@hw_supermicro_X13QEH:
    |  |--compute1
    |  |--compute2
    |  |--compute3
    |  |--compute4
    |--@os_almalinux_9:
    |  |--management1
    |  |--compute1
    |  |--compute2
    |  |--compute3
    |  |--compute4
  (pydevs) oxedions@prima:~/tmp_devs$ 

Finally, create the new hw profile. Create file ``group_vars/hw_supermicro_X13QEH/settings.yml`` with the following content:

.. code-block:: yaml

  hw_equipment_type: server

  hw_specs:
    cpu:
      name: Intel 6416H
      cores: 144
      cores_per_socket: 18
      sockets: 4
      threads_per_core: 2
    gpu:

  hw_console: console=tty0 console=ttyS1,115200

  hw_board_authentication: # Authentication to BMC
    - protocol: IPMI
      user: ADMIN
      password: ADMIN

You can check which parameters are linked to a specific node using the ansible-inventory command:

.. code-block:: text

  (pydevs) oxedions@prima:~/tmp_devs$ ansible-inventory -i inventory/ --host management1 --yaml
  hw_board_authentication:
  - password: ADMIN
    protocol: IPMI
    user: ADMIN
  hw_console: console=tty0 console=ttyS1,115200
  hw_equipment_type: server
  hw_kernel_parameters: nomodeset
  hw_specs:
    cpu:
      cores: 32
      cores_per_socket: 8
      name: Intel E5-2667 v4
      sockets: 2
      threads_per_core: 2
    gpu: null
  hw_vendor_url: https://www.supermicro.com/en/products/motherboard/X10DRT-L
  os_access_control: enforcing
  os_admin_password_sha512: $6$JLtp9.SYoijB3T0Q$q43Hv.ziHgC9mC68BUtSMEivJoTqUgvGUKMBQXcZ0r5eWdQukv21wHOgfexNij7dO5Mq19ZhTR.JNTtV89UcH0
  os_firewall: true
  os_keyboard_layout: us
  os_operating_system:
    distribution: almalinux
    distribution_major_version: 9
  os_partitioning: clearpart --all --initlabel autopart --type=plain --fstype=ext4
  os_system_language: en_US.UTF-8
  (pydevs) oxedions@prima:~/tmp_devs$ 

Proceed the same way to add all nodes to the inventory.

Connect cluster to the world (optional)
---------------------------------------

|
.. image:: images/configure_bluebanquise/example_single_island.svg
   :align: center
|

You may need to connect the cluster to a gateway, or even configure a server as a gateway.
In this example, login1 will act as a gateway.


Create a file /root/gen.sh with the following content:

.. code-block:: text

  #!/bin/bash
  cat <<EOF > computes.yml
  mg_computes:
    children:
      equipment_typeC:
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

  chmod +x /root/gen.sh
  /root/gen.sh 4


Host settings
-------------

- **bmc**: dict that defines an attached BMC to the host, with its name, ip4, mac and attached network.

Example:

.. code-block:: yaml

  c001:
    bmc:
      name: node001-bmc
      ip4: 10.10.103.1
      mac: 08:00:27:0d:44:91
      network: net-admin

- **network_interfaces**: list of dicts that defines all network interfaces of the host. Note that order is important. First interface in the list is the resolution (ping) interface,
  while first in the list linked to an admininstration network (see Network settings) is the ssh/Ansible interface (which can be the same than the resolution interface).

Example:

.. code-block:: yaml

  node001:
    network_interfaces:
      - interface: eth1
        ip4: 10.10.3.1
        mac: 08:00:27:0d:44:90
        network: net-admin
      - interface: eth0
        skip: true
      - interface: ib0
        ip4: 10.20.3.1
        network: interconnect
        type: infiniband

Available settings for each interface are the ones listed in `the Ansible nmcli_module. <https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html>`_
Note that only RHEL and Suse support all these settings. Available settings for Debian and Ubuntu are currently limited in the stack, but can be extended on demand (please open a feature request).

- **alias**: add an alias to the host, that will be added in the /etc/hosts file and in the dns server.
- **global_alias**: add a global alias not limited to the current iceberg (multiple icebergs mode only).