=====
Nodes
=====

Nodes are defined by default at ``inventory/`` root level.
For convenience, we most of the time store the nodes file(s) and group files inside a dedicated ``inventory/cluster/`` folder.



Create inventory
================

It is important to understand inventory structure.

By default, main location are the following (assuming relative to ``inventory/``):

.. image:: images/inventory/key_paths.png
   :align: center

|

* ``cluster/nodes/`` and ``cluster/groups/``: this is where nodes are listed, with their dedicated network parameters, and linked to desired groups
* ``group_vars/my_group_name/``: this is where groups are described (OS to be used, kernel parameters, partitioning, iPXE settings, etc.)
* ``group_vars/all/``: this is where stack global values are set (logical networks, domain name, etc.)

Then, each described node will inherit from these settings. It is important to understand that some settings are linked. For example,
a node set as member of group ``os_debian_12`` will inherit this group parameters. Also, if a network interface of this node is 
linked to logical network ``net-1``, it will inherit all ``net-1`` network parameters. Etc.

.. image:: images/inventory/node_get_values.png
   :align: center

|

Create needed folders first:

.. code-block::

  mkdir -p inventory/group_vars/all/
  mkdir -p inventory/cluster/nodes
  mkdir inventory cluster/groups

We are now going to populate inventory for the following basic example cluster:

.. image:: images/configure_bluebanquise/example_single_island.svg
   :align: center
|

Whatever the future cluster shape, you should start small with this, and extend it once working fine.

Add first management node
-------------------------

|
.. image:: images/configure_bluebanquise/management1_1.svg
   :align: center
|

Let's add the first node, ``management1``. This is a special node, as it will be the manager of the cluster.

Create file ``cluster/nodes/management.yml`` (YAML file) and add the following content inside:

.. code-block:: yaml

  all:
    hosts:
      management1:

.. note::
  We create here one file per function, as it seems easier to maintain. However, all these files are flattened by
  Ansible during execution, which means we could create a single ``nodes.yml`` file that would contain all the nodes in once.
  It is up to you.

Now create file ``cluster/groups/fn`` (INI file) with the following content:

.. code-block:: ini

  [fn_management]
  management1

We will assume in this example that this server is a supermicro_X10DRT and that we are going to deploy AlmaLinux 9 on it.

Create file ``cluster/groups/hw`` (INI file) with the following content:

.. code-block:: ini

  [hw_supermicro_X10DRT]
  management1

Then create file ``cluster/groups/os`` (INI file) with the following content:

.. code-block:: ini

  [os_almalinux_9]
  management1

Now check the result:

.. code-block:: text

  oxedions@prima:~/$ ansible-inventory -i inventory/ --graph
  @all:
    |--@ungrouped:
    |--@fn_management:
    |  |--management1
    |--@hw_supermicro_X10DRT:
    |  |--management1
    |--@os_almalinux_9:
    |  |--management1
  oxedions@prima:~/$ 

We can see that our management1 host is part of 3 groups:

1. ``fn_management`` which is its function (a management node)
2. ``hw_supermicro_X10DRT`` which is the hardware definition
3. ``os_almalinux_9`` which is the os definition

This creates a new equipment profile (see vocabulary section of this documentation).


Connect node to network
-----------------------

|
.. image:: images/configure_bluebanquise/management1_3.svg
   :align: center
|

Now connect management1 to this network. Edit file ``cluster/nodes/management.yml`` and add management1
network interface:

.. code-block:: yaml

  all:
    hosts:
      management1:
        network_interfaces:
          - interface: enp0s3
            ip4: 10.10.0.1
            mac: 08:00:27:dc:f8:f5
            network: net-1

It should not be too difficult to understand this file.

What is essential here is to understand that order network interfaces are
defined under *network_interfaces* variable matters. Rules are the following:

1. The first interface in the list is the **resolution interface**. This is the one a ping will try to reach.
2. The first interface attached to a management network is the **main network interface** (remember, management networks are the ones prefixed ``net-``). This is the one ssh and so Ansible will use to connect to the node.

If these rules do not comply with your needs, remember that the stack logic can
be precedenced: simply re-define logic variables like ``j2_node_main_resolution_network`` or
``j2_node_main_network`` manually under host.

.. note::
  You may not already know the interface name, or even the MAC address.
  You will be able to update it later, once server is reachable.


Add remaining nodes
-------------------

|
.. image:: images/configure_bluebanquise/others_1.svg
   :align: center
|

Proceed as with management1 node. We will do computes1 to compute4, other nodes can then be added the same way.

First create file ``cluster/nodes/compute.yml`` (YAML file) and add the following content inside:

.. code-block:: yaml

  all:
    hosts:
      compute1:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.1
            mac: 08:00:27:dc:f8:a1
            network: net-1
      compute2:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.2
            mac: 08:00:27:dc:f8:a2
            network: net-1
      compute3:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.3
            mac: 08:00:27:dc:f8:a3
            network: net-1
      compute4:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.3.4
            mac: 08:00:27:dc:f8:a4
            network: net-1

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