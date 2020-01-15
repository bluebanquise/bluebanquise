======================
Configure BlueBanquise
======================

At this point, you should have an operating system with Ansible installed on it, and basic OS repositories.

Get BlueBanquise
================

Install needed basic packages:

.. code-block:: bash

  yum install wget createrepo git

Now, download latest **BlueBanquise** version from git:

.. code-block:: bash

  git clone https://github.com/oxedions/bluebanquise.git /etc/bluebanquise

ansible will read ANSIBLE_CONFIG, ansible.cfg in the current working directory, .ansible.cfg in the home directory or /etc/ansible/ansible.cfg, whichever it finds first.

To use /etc/bluebanquise/ansible.cfg, either change the current working directory or set ANSIBLE_CONFIG:

.. code-block:: bash

  export ANSIBLE_CONFIG=/etc/bluebanquise/ansible.cfg
  cd /etc/bluebanquise

Finally, edit /etc/hosts file, and add "management1" (or whatever your current management node hostname) on localhost line:

.. code-block:: text

  127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4 management1
  ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

It is time to configure the inventory to match cluster needs.

Configure inventory
===================

This documentation will cover the configuration of a very simple cluster:

.. image:: images/example_cluster_small.svg

Important before we start
-------------------------

Ansible will read **ALL** files in the inventory. **NEVER do a backup of a file here!**

Backup in another location, outside of /etc/bluebanquise/inventory.

Check example inventory
-----------------------

An inventory example is provided in /etc/bluebanquise/resources/examples/simple_cluster/ as a base for our work.

This example is based on the picture provided just above.

Lets copy it to use it as our new inventory:

.. code-block:: bash

  cp -a /etc/bluebanquise/resources/examples/simple_cluster/inventory /etc/bluebanquise/inventory

Review nodes
------------

Time to review the provided example configuration, and adapt it to your configuration.

First, the nodes.

Management node
^^^^^^^^^^^^^^^

Open file cluster/nodes/managements.yml:

.. code-block:: yaml

  mg_managements:
    children:
      equipment_typeM:
        hosts:
          management1:
            bmc:
              name: bmanagement1
              ip4: 10.10.100.1
              mac: 08:00:27:dc:f8:f6
              network: ice1-1
            network_interfaces:
              enp0s3:
                ip4: 10.10.0.1
                mac: 08:00:27:dc:f8:f5
                network: ice1-1
              ib0:
                ip4: 10.20.0.1
                network: interconnect-1

This file contains our management node configuration. Let’s review it, to understand it.

First, the groups:

.. code-block:: yaml

  mg_managements:         # This is the main group (also called master group), it is very useful with advanced configuration
    children:             # This is an Ansible instruction, indicating the below group is included in mg_managements group
      equipment_typeM:    # This is the equipment group of the management node. It always starts by 'equipment_'
        hosts:            # This is an Ansible instruction, to list below the hosts member of this group
          management1:    # This is the hostname

Now the BMC (if exist):

.. code-block:: yaml

  mg_managements:
    children:
      equipment_typeM:
        hosts:
          management1:
            bmc:                      # This instruction defines an attached BMC
              name: bmanagement1      # This is the hostname of the BMC
              ip4: 10.10.100.1        # This is the ipv4 of the BMC
              mac: 08:00:27:dc:f8:f6  # This is the MAC hardware address of the BMC (for DHCP)
              network: ice1-1         # This is the logical network this interface is connected to. Logical networks will be seen later.

Then the network interfaces and their associated networks:

.. code-block:: yaml

  mg_managements:
    children:
      equipment_typeM:
        hosts:
          management1:
            bmc:
              name: bmanagement1
              ip4: 10.10.100.1
              mac: 08:00:27:dc:f8:f6
              network: ice1-1
            network_interfaces:         # This is an instruction, to define bellow all host's NIC (Network Interface Controllers)
              enp0s3:                   # This is the NIC name ('ip a' command to get NIC list)
                ip4: 10.10.0.1          # This is the expected ipv4 for this NIC
                mac: 08:00:27:dc:f8:f5  # This is the NIC MAC address, for the DHCP
                network: ice1-1         # This is the logical network this interface is linked to
              ib0:                      # This is another interface, not in the dhcp so no MAC is provided
                ip4: 10.20.0.1
                network: interconnect-1

It should not be too difficult to understand this file.

Other nodes
^^^^^^^^^^^

Now, review computes nodes and logins nodes in respectively files cluster/nodes/computes.yml and cluster/nodes/logins.yml. Same rules apply. You can also add more nodes, or if you have for example multiple type of equipment for computes nodes or login nodes, add another equipment group this way:

.. code-block:: yaml

  mg_computes:
    children:
      equipment_typeC:
        hosts:
          c001:
          [...]
      equipment_typeD:
        hosts:
          c005:
          [...]
      equipment_typeE:
        hosts:
          c010:
          [...]

Now, let's have a look at the logical networks.

Review logical networks
-----------------------

In **BlueBanquise**, nodes are connected together through logical network. Most of the time, logical networks will match your physical network, but for advanced networking, it can be different.

All networks are defined in group_vars/all/networks directory, with one file per network. In this current example inventory, there are two networks provided: ice1-1 and interconnect-1.

Before reviewing the file, please read this **IMPORTANT** information: in **BlueBanquise** there are two kind of networks: administration networks, and the others.

An administration network is used to deploy and manage the nodes. It will be for example used to run a DHCP server, handle the PXE stack, etc, and also all the Ansible ssh connections. Administration networks have a strict naming convention, which by default is: **iceX-Y** with X the iceberg number, and Y the subnet number in this iceberg X. In our case, we are working on iceberg1 (default when disabling icebergs mechanism), and we only have one subnet, so our administration network will be ice1-1. If we would need another subnet, its name would have been ice1-2, etc. Interconnect-1 is not an administration network.

Open file group_vars/all/networks/ice1-1.yml and let's check its content:

.. code-block:: yaml

  networks:                                             # This defines a new network
    ice1-1:                                             # Network name
      subnet: 10.10.0.0                                 # Network subnet
      prefix: 16                                        # Network prefix
      netmask: 255.255.0.0                              # Network netmask, must comply with prefix
      broadcast: 10.10.255.255                          # Broadcast, deduced from subnet and prefix/netmask
      dhcp_unknown_range: 10.10.254.1 10.10.254.254     # This is the range of ip where unknown nodes (i.e. not in the inventory) will be placed if asking for an ip
      gateway: 10.10.0.1                                # Optional, define a gateway
      is_in_dhcp: true                                  # If you want this network to be in the dhcp (only apply to management networks)
      is_in_dns: true                                   # If you want this network to be in the dns
      services_ip:                                      # IPs or virtual IPs to bind to for each service. In our case, all services will be running on management1 so 10.10.0.1 for all
        pxe_ip: 10.10.0.1
        ntp_ip: 10.10.0.1
        dns_ip: 10.10.0.1
        repository_ip: 10.10.0.1
        authentication_ip: 10.10.0.1
        time_ip: 10.10.0.1
        log_ip: 10.10.0.1

All explanations are given above.

One note for services_ip. It is used if services are spread over multiple managements, or in case of High Availability with virtual IPs. Ansible is not able to gather this information alone from playbooks (it could, but this would end up with a way too much big stack), and so we have to provide it manually. You can also set here an IP from another subnet if your system has network routing.

Then check content of file group_vars/all/networks/interconnect-1.yml . As this is **not** an administration network, its configuration is easy.

That is all for basic networking. General network parameters are set in group_vars/all/networks/ files, and nodes parameters are defined in the node’s files.

Now, let's have a look at the general configuration.

Review general configuration
----------------------------

General configuration is made in group_vars/all/general_settings.

Externals
^^^^^^^^^

File group_vars/all/general_settings/external.yml allows to connect cluster to the external world or network. It should be self understandable.

Network
^^^^^^^

File group_vars/all/general_settings/network.yml allows to configure few network related parameters.

Repositories
^^^^^^^^^^^^

File group_vars/all/general_settings/repositories.yml configure repositories to use for all nodes (using groups and variable precedence, repositories can be tuned for each group of nodes, or even each node).

Right now, only *os* and *bluebanquise* are set. This means two repositories will be added to nodes, and they will bind to repository_ip in ice1-1.yml .

NFS
^^^

File group_vars/all/general_settings/nfs.yml allows to set NFS shared folders inside the cluster. Comments in the file should be enough to understand this file.

General
^^^^^^^

File group_vars/all/general_settings/general.yml configure few main parameters:

* Time zone (very important)

Do not bother about the other parameters.

And that is all for general configuration. Finally, let’s check the default parameters.

Review Default parameters
-------------------------

Last part, and probably the most complicated, are default parameters.

Remember Ansible precedence mechanism. All variables in group_vars/all/ have less priority, while variables in group_vars/* have a higher priority.

The idea here is the following: group_vars/all/all_equipment/ folder contains all the default parameters for all nodes. Here authentication, and equipment_profile. You have to tune these parameters to match your exact "global" need, and then tune dedicated parameters for each equipment group.

Equipment profile
^^^^^^^^^^^^^^^^^

For example, open file /etc/bluebanquise/inventory/group_vars/all/all_equipment/equipment_profile.yml, and check access_control variable. It is set to true:

.. code-block:: yaml

  equipment_profile:
    access_control: true

Ok, but so all nodes will get this value. Let's check computes nodes, that are in equipment_typeC group. Let's check c001:

.. code-block:: bash

  [root@]# ansible-inventory --host c001 --yaml | grep access_control
    access_control: true
  [root@]#

Not good. We need to change that.

Open file group_vars/equipment_typeC/equipment_profile.yml and set access_control to false (line is just commented, uncomment it).

Now check again:

.. code-block:: bash

  [root@]# ansible-inventory --host c001 --yaml | grep access_control
    access_control: false
  [root@]#

Same apply for all equipment_profile parameters. You define a global one in default, and then tune it for each equipment group.

**IMPORTANT**: equipment_profile variable is not standard. It is **STRICTLY FORBIDDEN** to tune it outside default (group_vars/all/all_equipments/equipment_profile.yml) or an equipment group (group_vars/equipment_*). For example, you cannot create a custom group and define some equipment_profile parameters for this group. If you really need to do that, add more equipment groups and tune this way. If you do not respect this rule, unexpected behavior will happen during configuration deployment.

Authentication
^^^^^^^^^^^^^^

Authentication file allows to define default root password for all nodes, and default public ssh keys lists.

We need to ensure our management1 node ssh public key is set here.

Get the content of /root/.ssh/id_ras.pub and add it in this file. At the same time, **remove the ssh key provided here as example**.

Review groups parameters
------------------------

Last step is to check and review example of equipment_profile tuning in each of the group_vars/equipment_XXXXXX folders. Adapt them to your needs.

If you prefer, you can copy the whole group_vars/all/all_equipment/equipment_profile.yml file into these folders, or simply adjust the parameters you wish to change from default.

Once done, configuration is ready.

It is time to deploy configuration on management1.

