=====================================
Configure and deploy basic management
=====================================

At this point, you should have the bluebanquise user setup
with Ansible and BlueBanquise collections installed.

.. image:: images/clusters/documentation_example_single_island_step_1.svg
   :align: center

Understand Environment
======================

By default, Ansible will check presence of configuration file at multiple
locations:

1. Environment variable **ANSIBLE_CONFIG**
2. ansible.cfg in the current working directory
3. .ansible.cfg in the home directory
4. /etc/ansible/ansible.cfg

The first found is used as main configuration.

The bootstrap script created an entry in your bluebanquise user .bashrc 
file that export ANSIBLE_CONFIG variable:

.. code-block::

  ANSIBLE_CONFIG=$HOME/bluebanquise/ansible.cfg

The script also created 2 other exports:

.. code-block::

  export PATH=$HOME/bluebanquise/.local/bin:$PATH
  export PYTHONPATH=$(pip3 show ClusterShell | grep Location | awk -F ' ' '{print $2}')

First one adds Ansible and related binaries into PATH to be usable from shell.
Second one ensures your PYTHONPATH will be exported later when executing commands as sudo.

You can also check the /etc/sudoers file. The bootstrap script added the line:

.. code-block::

  Defaults env_keep += "PYTHONPATH"

This ensure your PYTHONPATH is exported into sudo environment.

All collections were installed by *ansible-galaxy* into ``$HOME/.ansible/collections/ansible_collections/bluebanquise/``.
You should avoid editing these files to allow simpler updates later.

Configure inventory
===================

By default, main location are the following:

.. image:: images/inventory/key_paths.svg
   :align: center

We are going to create a standard BlueBanquise Ansible inventory.
However, in case of very small cluster, you can create an all in one file with INI format. Please refer to BEN_BEN.

.. raw:: html

   <br>
   <div class="tip_card">                
   <div class="tip_card_img_container"><img src="../_static/img_avatar.png" style="width:100px; border-radius: 5px 0 0 5px; float: left;" /></div>
   <div class="tip_card_title_container"><b>Tip from the penguin:</b></div>
   <div class="tip_card_content_container"><p>Since inventory is fully text based, you should strongly consider to version it with a git.</p></div>
   </div>
   <br>

Create folder (path can be as your convenience) ``inventory``, and all the needed subfolders:

.. code-block::

  mkdir inventory
  mkdir inventory/cluster
  mkdir inventory/cluster/nodes
  mkdir inventory/cluster/groups
  mkdir inventory/group_vars
  mkdir inventory/group_vars/all

Few explanations:

* ``cluster/nodes/`` and ``cluster/groups/``: this is where nodes are listed, with their dedicated network parameters, and linked to desired groups.
* ``group_vars/all/``: this is where stack global values are set (logical networks, domain name, nfs, etc.). All means that variable set here will be seen by all nodes.

.. image:: images/inventory/node_get_values.svg
   :align: center

.. warning::
  Ansible will read **ALL** files in the inventory. **NEVER do a backup of a file
  here!**, as it will be read too.
  Backup in another location, outside of ``inventory`` folder.

Time now to define our management1 node.

Defining management1
--------------------

Node and groups
^^^^^^^^^^^^^^^

The first step here is to define the management1 management node as a basic Ansible host.

Create file ``inventory/cluster/nodes/managements.yml`` (name of the file doesn't matter),
and add the first management node inside:

.. code-block::yaml

  all:
    hosts:
      management1:

And lets check the node is identified by Ansible:

.. code-block::

  ansible-inventory -i inventory --graph

Should output:

.. code-block::

  @all:
    |--management1
    |--@ungrouped:

We can see that management1 node is part of group all. Since it is a management node, we also need it to be
part of **mg_managements** group, so the BlueBanquise stack identifies it as a special node. Remember, ``mg_`` groups
define the purpose of nodes.

Create file ``inventory/cluster/groups/mg.yml`` (name of the file doesn't matter), and add the
following INI content:

.. code-block::ini

  [mg_managements]
  management1

And check again groups structure:

.. code-block::

  ansible-inventory -i inventory --graph

Should output:

.. code-block::

  @all:
    |--@mg_managements:
    |  |--management1
    |--@ungrouped:

We are not going to define the related equipment group for now (``ep_``).

Networking
^^^^^^^^^^

We now need to link the management1 node to a logical network.

First step is to create this network. It will be used to deploy, reach, and manage the other nodes of the cluster.
This is a **management network**.

Create file  ``inventory/group_vars/all/networks.yml`` (name of the file doesn't matter,
but path ``inventory/group_vars/all/`` is important),
and define network ``net-admin`` inside.
Note that a management network must always be prefixed by ``net_``.

.. code-block::yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0

Now, lets link our **management1** dedicated network interfaces
to this network, and assign it ip ``10.10.0.1``. We will assume interface is ``eno1``, but it could be 
enp0s1, eth2, etc. Use command ``ip a`` to list available network interfaces.

Edit file ``inventory/cluster/nodes/managements.yml``
and add network_interfaces information under host name (ensure MAC address matches the one of your host):

.. code-block::yaml

  all:
    hosts:
      management1:
        network_interfaces:
          - interface: eno1
            ip4: 10.10.0.1
            mac: 1a:2b:3c:4d:5e:9f
            network: net-admin

management1 **eno1** NIC is now set with ip **10.10.0.1** and linked to network **net-admin** with prefix **16** and subnet **10.10.0.0**.

Time now to add the other nodes of the cluster. If the cluster is very large, an smart strategy at this point 
is to only define 1 node of each kind, then proceed to the remaining of the documentation to ensure all nodes can deploy,
and come back to this point later to add remaining nodes.

Defining other nodes
--------------------

We now have to define the remaining nodes. In this example, this includes:

* storage1
* login1
* computes[1-4]

Create file ``inventory/cluster/nodes/storages.yml`` and add inside:

.. code-block::yaml

  all:
    hosts:
      storage1:

Create file ``inventory/cluster/nodes/logins.yml`` and add inside:

.. code-block::yaml

  all:
    hosts:
      login1:

Create file ``inventory/cluster/nodes/computes.yml`` and add inside:

.. code-block::yaml

  all:
    hosts:
      compute1:
      compute2:
      compute3:
      compute4:

.. raw:: html

   <br>
   <div class="tip_card">                
   <div class="tip_card_img_container"><img src="../_static/img_avatar.png" style="width:100px; border-radius: 5px 0 0 5px; float: left;" /></div>
   <div class="tip_card_title_container"><b>Tip from the penguin:</b></div>
   <div class="tip_card_content_container"><p>For very large clusters, you can create one file per rack for example. All files are read and merged during Ansible execution.</p></div>
   </div>
   <br>

Then, add nodes into dedicated mg groups.

Edit file ``inventory/cluster/groups/mg.yml`` and add other groups so that file matches the following:

.. code-block::ini

  [mg_managements]
  management1

  [mg_storages]
  storage1

  [mg_logins]
  login1

  [mg_computes]
  compute[1:4]

.. warning::
   Note that Ansible INI range syntax is not the same than ClusterShell syntax. A range here is defined by ``[1:4]`` instead of ``[1-4]``.

Now, check all is setup properly and understood by Ansible:

.. code-block::

  ansible-inventory -i inventory --graph

Should output:

.. code-block::

  @all:
    |--@mg_managements:
    |  |--management1
    |--@mg_storages:
    |  |--storage1
    |--@mg_logins:
    |  |--login1
    |--@mg_computes:
    |  |--compute1
    |  |--compute2
    |  |--compute3
    |  |--compute4
    |--@ungrouped:

Now link all nodes to ``net-admin`` network. It works the same way than with **management1** node.
For example, for computes nodes, assuming their main NIC is named enp0s1:

.. code-block::yaml

  all:
    hosts:
      compute1:
        network_interfaces:
          - interface: enp0s1
            ip4: 10.10.3.1
            mac: 1a:2b:3c:4d:1e:9f
            network: net-admin
      compute2:
        network_interfaces:
          - interface: enp0s1
            ip4: 10.10.3.2
            mac: 1a:2b:3c:4d:2e:9f
            network: net-admin
      compute3:
        network_interfaces:
          - interface: enp0s1
            ip4: 10.10.3.3
            mac: 1a:2b:3c:4d:3e:9f
            network: net-admin
      compute4:
        network_interfaces:
          - interface: enp0s1
            ip4: 10.10.3.4
            mac: 1a:2b:3c:4d:4e:9f
            network: net-admin

Ensure MAC address match the ones of the nodes, and do the same for **storage1** and **login1**.

All our nodes are now defined, and linked to the same administration network.

BMS (optional)
--------------

If your servers are attached and managed by embed BMCs, it needs to be defined too, so the stack can
register BMCs into dedicated tools (power management, remote consoles, monitoring, etc.).
If you do not have BMCs, please skip this part.

To define a BMC, simply attach it to an host, and link its network interface to a network. In this example
we will link BMCs to the ``net-admin`` network.
Note however that it is a good practice to later isolate BMCs on a dedicated network.

We will assume here that **storage1** has a BMC, called **bstorage1**, with ip ``10.10.101.1``.
Edit file ``inventory/cluster/nodes/storages.yml`` and add BMC settings, at same level than ``network_interfaces``, as follow:

.. code-block::yaml

  all:
    hosts:
      storage1:
        bmc:
          name: bstorage1
          ip4: 10.10.101.1
          mac: 08:00:27:dc:f8:f6
          network: net-admin
        network_interfaces:
          - interface: enp0s1
            ip4: 10.10.1.4
            mac: 1a:2b:3c:4d:7e:9f
            network: net-admin

It is now time to define services endpoint.

Define services
---------------

To operate, a cluster of nodes needs services. The most vital ones are:

* dhcp
* pxe (http, tftp)
* dns
* time

On our cluster, all these services will be hosted on management1 node. And all other nodes will
bind to these services over ``net-admin`` network. To do so, we need to define in the inventory that
management1 will be the main host of all services, and that its ip ``10.10.0.1`` will be the endpoint for that.

Edit file ``inventory/group_vars/all/networks.yml``, and define key ``services_ip`` under ``net-admin`` network, 
as follow:

.. code-block::yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0
      services_ip: 10.10.0.1

You will be able later to fine define endpoint ip/hostname for each service. But for now, we want all of them to simply
rely on management1 node.

Equipment groups
----------------

We could now deploy configuration on management1 node. However, we haven't defined any OS related parameters:

* Linux distribution and distribution version
* Partitioning desired on deployed nodes
* Specific kernel parameters (including consoles if needed)
* IPMI password if needed
* Admin password and ssh keys
* etc.

Equipment groups are Ansible group, that define for their member nodes all deployment parameters, and can also store
useful data like hardware vendor, comments, etc.
Most of the time, each kind of server / workstation will refer to a dedicated equipment group.

By default, if nodes are not member of any equipment group, they will belong to ``all`` *magic* equipment group and so
be configured according to pxe_stack role defaults (x86_64 Ubuntu 22.04).

Equipment groups (except *all*) are always prefixed with ``equipment_``. Then remaining naming convention is up to administrator.

We will assume here that management1 is part of ``equipment_SUPERMICRO_16C_32G``, login and computes nodes are part of
``equipment_GIGABYTE_64C_256G`` and storage1 node is part of ``equipment_5TB_NVME`` (again, as long as prefix is respected, naming is up to you).

Operating system
^^^^^^^^^^^^^^^^

Create file ``inventory/cluster/groups/equipment.yml`` and add nodes as follow:

.. code-block::ini

  [equipment_SUPERMICRO_16C_32G]
  management1

  [equipment_5TB_NVME]
  storage1

  [equipment_GIGABYTE_64C_256G]
  login1
  compute[1:4]

Now, create folders that will contain dedicated files of each group:

.. code-block::text

  mkdir inventory/group_vars/equipment_SUPERMICRO_16C_32G
  mkdir inventory/group_vars/equipment_GIGABYTE_64C_256G
  mkdir inventory/group_vars/equipment_5TB_NVME

We will assume that the cluster is homogenous, and that it relies on AlmaLinux 9 Linux distribution. Procedure is
nearly the same whatever the target distribution.

Create file ``inventory/group_vars/equipment_SUPERMICRO_16C_32G/os.yml`` and add the following content:

.. code-block::yaml

  ep_console:
  ep_kernel_parameters:

  ep_partitioning:

  ep_operating_system:
    distribution: almalinux
    distribution_major_version: 9

  ep_configuration:
    keyboard_layout: us  # us, fr, etc.
    system_language: en_US.UTF-8  # You should not update this if you want to google issues...

Note that if left empty, ``ep_partitioning`` will use native OS auto-partitioning, which might fail if hardware is not
generic, or result in loss of data if only a specific disk should be targeted on a multi-disks system.
You can provide native distribution partitioning. For a RedHat like system, an example could be:

.. code-block::yaml

  ep_partitioning: |
    clearpart --all --initlabel
    part /boot --fstype=ext4 --size=1024
    part / --fstype=ext4 --size=60000
    part /home --fstype=ext4 --size=4096 --grow

Please read your Linux distribution documentation for extended / complex partitioning syntax.
Few examples are provided at BEN_BEN

A full list of available equipment ``ep_`` keys are available at BEN_BEN.

Do now the same for all other equipment groups, by creating files
``inventory/group_vars/equipment_GIGABYTE_64C_256G/os.yml`` and
``inventory/group_vars/equipment_5TB_NVME/os.yml``

Access and security
^^^^^^^^^^^^^^^^^^^

Now generate an admin password SHA512 hash, using:

.. code-block::python

  python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'

And copy the output.

Then grab ssh public key of current user (should be bluebanquise user by default).

.. code-block::text

  cat $HOME/.ssh/id_ed25519.pub

And copy the output.

Then create file ``inventory/group_vars/equipment_SUPERMICRO_16C_32G/security.yml`` and add the following content:

.. code-block::yaml


  ep_access_control: enforcing  # We set SELinux to enforcing
  ep_firewall: true  # We want firewall to be enabled

ep_admin_password_sha512

ep_admin_ssh_keys

  ep_host_authentication:  # comment if not needed. Login/password for BMC, storage bay controller, switch, etc.
    - protocol: IPMI
      user: admin
      password: admin

Comment/remove ``ep_host_authentication`` and ``ep_console`` if you do not have BMCs on these equipment.


Hardware
^^^^^^^^

.. code-block::yaml


  ep_equipment_type: server  # If server, a pxe profile will be generated





In BlueBanquise, there are 3 main types of groups, apart of user's custom groups.

Use command ansible-inventory to display current groups in the inventory:

.. code-block:: text

  bluebanquise@localhost:~/ ansible-inventory --graph
  @all:
    |--@internal:
    |  |--dummy
    |--@mg_computes:
    |  |--@equipment_typeC:
    |  |  |--compute1
    |  |  |--compute2
    |  |  |--compute3
    |  |  |--compute4
    |--@mg_logins:
    |  |--@equipment_typeL:
    |  |  |--login1
    |--@mg_managements:
    |  |--@equipment_typeM:
    |  |  |--management1
    |--@mg_storages:
    |  |--@equipment_typeS:
    |  |  |--storage1
    |--@rack_1:
    |  |--compute1
    |  |--compute2
    |  |--compute3
    |  |--compute4
    |  |--login1
    |  |--management1
    |  |--storage1
    |--@ungrouped:

In this example inventory, you can see **mg_** groups, and **equipment_** groups.
*rack_1* group is a user's custom group and is not important for the stack to
operate properly.

**mg_** groups are called master groups, and define global
purpose of their nodes: storages, managements, logins, computes, etc.

**equipment_** groups are called equipment profile groups, and define equipment
related settings of their nodes. These groups are linked to the hardware of
nodes. For example, if in **mg_computes** group, your cluster contains 2 type of
nodes, for example model_A and model_B servers, then you need to create 2
equipment profile groups, called equipment_model_A and equipment_model_B, that
contain their related nodes.

Equipment profiles are subgroups of master groups.

Review nodes
------------

First step is to review the provided example configuration, and adapt it to your
configuration. The following part assume all path are relative to
~/bluebanquise/inventory/ folder.

Management node
^^^^^^^^^^^^^^^

Open file cluster/nodes/managements.yml, and visualize content:

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
              - interface: enp0s3
                ip4: 10.10.0.1
                mac: 08:00:27:dc:f8:f5
                network: ice1-1
              - interface: ib0
                ip4: 10.20.0.1
                network: interconnect-1

This file contains our management node configuration. Let’s review it, to
understand it.

First, the groups:

.. code-block:: yaml

  mg_managements:         # This is the master group (also called main group), it is very useful with advanced configuration
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
              - interface: enp0s3       # This is the NIC name ('ip a' command to get NIC list)
                ip4: 10.10.0.1          # This is the expected ipv4 for this NIC
                mac: 08:00:27:dc:f8:f5  # This is the NIC MAC address, for the DHCP
                network: ice1-1         # This is the logical network this NIC is linked to
              - interface: ib0          # This is another NIC, not in the dhcp so no MAC is provided
                ip4: 10.20.0.1
                network: interconnect-1

It should not be too difficult to understand this file.

What is essential here is to understand that order network interfaces are
defined under *network_interfaces* variable matters. Rules are the following:

* The first interface in the list is the resolution interface. This is the one a ping will try to reach.
* The first management network attached interface (management networks are explain in the next chapter) is the main network interface. This is the one ssh and so Ansible will use to connect to the node.

If these rules do not comply with your needs, remember that the stack logic can
be precedenced: simply define new *j2_node_main_resolution_network*,
*j2_node_main_network*, etc variables (these variables are stored into *internal*
folder)

.. note::
  More network features and configurations are available, see the **nic** role
  readme file for more information.

Other nodes
^^^^^^^^^^^

Now, review computes, logins and storages nodes in their respective
*cluster/nodes/computes.yml*, *cluster/nodes/logins.yml* and
*cluster/nodes/storages.yml* files. Same rules apply.
You can also add more nodes, or if you have for example multiple type
of equipment for computes nodes, add other equipment groups
this way:

.. code-block:: yaml

  mg_computes:
    children:
      equipment_typeC:
        hosts:
          compute1:
          [...]
      equipment_typeD:
        hosts:
          compute5:
          [...]
      equipment_typeE:
        hosts:
          compute10:
          [...]

Now, let's have a look at the logical networks.

Review logical networks
-----------------------

In **BlueBanquise**, nodes are connected together through logical networks. Most
of the time, logical networks will match your physical network, but for advanced
networking, it can be different.

All networks are defined in *group_vars/all/general_settings/network.yml* file.
In this current example inventory, there are two networks provided:
``ice1-1`` and ``interconnect-1``.

Before reviewing the file, please read this **IMPORTANT** information: in
**BlueBanquise** there are two kind of networks: **administration/management
networks**, and the "others".

An **administration network** is used to deploy and manage the nodes. It will be for
example used to run a DHCP server, handle the PXE stack, etc, and also all the
Ansible ssh connections. Administration networks have a strict naming
convention, which by default is: **iceX-Y** with X the iceberg number, and Y the
subnet number in this iceberg X. In our case, we are working on iceberg1
(default when disabling icebergs mechanism), and we only have one subnet, so our
administration network will be ice1-1. If we would need another subnet, its name
would have been ice1-2, etc.

Interconnect-1 is not an administration network as it is not using **iceX-Y**
pattern. So it belongs to the "others" networks.

.. note::
  In new versions of the stack, it is now possible to replace the number Y by a
  string compatible with [0-9][a-z][A-Z] regex. For example ice1-prod.

Open file *group_vars/all/general_settings/network.yml* and let's check part of
its content:

.. code-block:: yaml

  networks:                                             # This defines the list of networks
    ice1-1:                                             # Network name
      subnet: 10.10.0.0                                 # Network subnet
      prefix: 16                                        # Network prefix
      netmask: 255.255.0.0                              # Network netmask, must comply with prefix
      broadcast: 10.10.255.255                          # Broadcast, deduced from subnet and prefix/netmask
      dhcp_unknown_range: 10.10.254.1 10.10.254.254     # Optional, this is the range of ip where unknown nodes (i.e. not in the inventory) will be placed if asking for an ip
      gateway: 10.10.0.1                                # Optional, define a gateway
      is_in_dhcp: true                                  # If you want this network to be in the dhcp (only apply to management networks)
      is_in_dns: true                                   # If you want this network to be in the dns
      services_ip:                                      # IPs or virtual IPs to bind to for each service. In our case, all services will be running on management1 so 10.10.0.1 for all
        pxe_ip: 10.10.0.1
        dns_ip: 10.10.0.1
        repository_ip: 10.10.0.1
        time_ip: 10.10.0.1
        log_ip: 10.10.0.1

All explanations are given above.

One note about ``services_ip``: it is used if services are spread over multiple
managements, or in case of High Availability with virtual IPs. Ansible is not
able to gather this information alone from playbooks (it could, but this would
end up with a way too much complex stack), and so we have to provide it manually.
You can also set here an IP address from another subnet if your system has
network routing.

Now check content of the second network, ``interconnect-1`` in file
*group_vars/all/general_settings/network.yml* . As this is **not** an
administration network, its configuration is easy.

That is all for basic networking. General network parameters are set in
*group_vars/all/general_settings/network.yml* file, and nodes parameters are
defined in the node’s files.
Nodes ``network_interfaces`` are linked to logical networks.

Now, let's have a look at the general configuration.

Review general configuration
----------------------------

General configuration is made in *group_vars/all/general_settings*.

Externals
^^^^^^^^^

File *group_vars/all/general_settings/external.yml* allows to configure external
resources. It should be self understandable.

Network
^^^^^^^

File *group_vars/all/general_settings/network.yml* allows to configure network
related parameters, and detail all networks of the cluster.

Repositories
^^^^^^^^^^^^

File *group_vars/all/general_settings/repositories.yml* configure repositories to
use for all nodes (using groups and variable precedence, repositories can be
tuned for each group of nodes, or even each node).

It is important to set correct repositories to avoid issues during deployments.

By default, recommanded settings are:

* RHEL like system:

.. raw:: html

  <div style="padding: 6px;">
  <b>RHEL</b> <img src="_static/logo_rhel.png">, <b>CentOS</b> <img src="_static/logo_centos.png">, <b>RockyLinux</b> <img src="_static/logo_rocky.png">, <b>OracleLinux</b> <img src="_static/logo_oraclelinux.png">, <b>CloudLinux</b> <img src="_static/logo_cloudlinux.png">, <b>AlmaLinux</b> <img src="_static/logo_almalinux.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - os            # Will bind to OS iso for BaseOS and AppStream base repositories
    - bluebanquise  # Will bind to bluebanquise repository

* Ubuntu system:

.. raw:: html

  <div style="padding: 6px;">
  <b>Ubuntu</b> <img src="_static/logo_ubuntu.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    # No need for os, as Ubuntu directly grab packages from the web
    - bluebanquise  # Will bind to bluebanquise repository

See the repositories_client role part of the documentation for advanced
configurations (list accept basic repos naming, but also advanced paterns).

Note also that if you wish to define different repositories per equipment, you
can easily use variable precedence mechanism seen in the Ansible tutorial to
define repositories variable in each equipment group, or even for each node.

NFS
^^^

File *group_vars/all/general_settings/nfs.yml* allows to set NFS shared folders
inside the cluster. Comments in the file should be enough to understand this
file.

Tune this file according to your need, or remove it if you do not plan to use NFS.

General
^^^^^^^

File *group_vars/all/general_settings/general.yml* configure few main parameters:

* Time zone (very important, should match the one of your current management server)

Do not bother right now about the other parameters.

And that is all for general configuration. Finally, let’s check the equipment
default parameters.

Review equipment default parameters
-----------------------------------

Last part, and probably the most complex, are equipment profile groups default
parameters. As seen before, equipment profile groups are groups related to the
hardware, the models, of the nodes. Variables related to these groups will
define parameters related to hardware, but also operating system deployed on
them, etc.

Equipment variables are defined at a global level, then redefined if needed for
each equipment.

Remember Ansible precedence mechanism. All variables in *group_vars/all/* have
less priority, while variables in *group_vars/** have a higher priority.

The idea here is the following: *group_vars/all/equipment_all/* folder contains
equipment default/global parameters for all nodes. Here authentication, and
equipment_profile. You have to tune these parameters to match your exact
"global" need, and then copy (if needed) part of these files into dedicated
group_vars folder for each equipment group, and tune them according to these
equipment specific parameters.

.. note::
  You can copy the whole equipment_profile.yml content from equipment_all to
  equipment_X folders, **or better**, create a new file in equipment_X and only
  set the parameters that are different from the global parameters.

For example, open file
*group_vars/all/equipment_all/equipment_profile.yml*,
and check access_control variable. It is set to enforcing:

.. code-block:: yaml

  ep_access_control: enforcing

Ok, but so all nodes will get this value. Let's check computes nodes, that are
in equipment_typeC group. Let's check compute1:

.. code-block:: bash

  [root@]# ansible-inventory --host compute1 --yaml | grep ep_access_control
    ep_access_control: enforcing
  [root@]#

Lets say this is not good, and we want to disable access_control on computes.
We need to change that.

Open file *group_vars/equipment_typeC/equipment_profile.yml* and set
``access_control`` to  *disabled*.

Now check again:

.. code-block:: bash

  [root@]# ansible-inventory --host compute1 --yaml | grep ep_access_control
    ep_access_control: disabled
  [root@]#

Same apply for all equipment_profile parameters. You define a global set of
parameters in equipment_all, which act as a global/default set, and then copy
(all or a part of them) and tune this set for each equipment group if needed.

.. image:: images/misc/warning.svg
   :align: center
|
.. warning::
  **IMPORTANT**: equipment_profile variables and authentication variables **are
  not standard**. It is **STRICTLY FORBIDDEN** to tune them outside default
  (group_vars/all/equipment_all/equipment_profile.yml) or an equipment group
  (group_vars/equipment_*). For example, you cannot create a custom group and
  define some equipment_profile parameters for this group. If you really need to
  do that, add more equipment groups and tune this way. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.


-------------

Once done, configuration is ready.

Remember that a data model is available in *resources/data_model.md* on the
BlueBanquise github.

It is time to deploy configuration on management1.
