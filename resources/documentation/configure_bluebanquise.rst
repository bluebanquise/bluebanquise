===============================
[Core] - Configure BlueBanquise
===============================

At this point, you should have an operating system with Ansible installed on it,
and basic OS repositories. You also have installed BlueBanquise package and its
dependencies, and your main NIC (Network Interface Controller) is configured and
activated (up).

.. image:: images/clusters/documentation_example_single_island_step_1.svg
   :align: center

Enable BlueBanquise and ssh
===========================

By default, Ansible will check presence of configuration file at multiple
locations:

1. Environment variable **ANSIBLE_CONFIG**
2. ansible.cfg in the current working directory
3. .ansible.cfg in the home directory
4. /etc/ansible/ansible.cfg

The first found is used as main configuration.

To enable BlueBanquise, we need Ansible to use /etc/bluebanquise/ansible.cfg.
To do so, set ANSIBLE_CONFIG:

.. code-block:: bash

  export ANSIBLE_CONFIG=/etc/bluebanquise/ansible.cfg

.. note::
  You can revert to Ansible default behavior by unsetting this variable. It
  allows to use both default Ansible and BlueBanquise together.

Edit /etc/hosts file, and add "management1" (or whatever your current
management node hostname) with its target ip (the one set on the main NIC):

.. code-block:: text

  127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
  ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
  10.10.0.1   management1

This will allow us to bootstrap the management configuration.

Generate now an ssh key for current management1 host, and do not set a
passphrase (leave empty when asked and press enter):

.. code-block:: text

  ssh-keygen -t ed25519

Then spread this key on the current host so that management1 can ssh on itself
passwordless (you will be asked current root password to establish this first
ssh connection):

.. code-block:: text

  ssh-copy-id management1

Now, ensure you can ssh without password now:

.. code-block:: text

  ssh management1

It is time to configure the inventory to match cluster needs.

Configure inventory
===================

Check example inventory
-----------------------

An inventory example is provided in
/etc/bluebanquise/resources/examples/simple_cluster/ and will be used
as a base for this documentation.

This example match the cluster exposed previously.

Copy it to use it as your new inventory starting point:

.. code-block:: bash

  cp -a /etc/bluebanquise/resources/examples/simple_cluster/inventory /etc/bluebanquise/inventory

.. warning::
  Ansible will read **ALL** files in the inventory. **NEVER do a backup of a file
  here!**
  Backup in another location, outside of /etc/bluebanquise/inventory.

Review groups
-------------

In BlueBanquise, there are 3 main types of groups, apart of user's custom groups.

Use command ansible-inventory to display current groups in the inventory:

.. code-block:: text

  [root@management1 ~]# ansible-inventory --graph
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
  [root@management1 ~]#

In this example inventory, you can see **mg_** groups, and **equipment_** groups.
*rack_1* group is a user's custom group and is not important for the stack to
operate properly.

**mg_** groups are called master groups (or main groups), and define global
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
/etc/bluebanquise/inventory/ folder.

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
  More network features and configurations are available, see the nic_nmcli role
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
*ice1-1* and *interconnect-1*.

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

One note about *services_ip*: it is used if services are spread over multiple
managements, or in case of High Availability with virtual IPs. Ansible is not
able to gather this information alone from playbooks (it could, but this would
end up with a way too much complex stack), and so we have to provide it manually.
You can also set here an IP address from another subnet if your system has
network routing.

Now check content of the second network, interconnect-1 in file
*group_vars/all/general_settings/network.yml* . As this is **not** an
administration network, its configuration is easy.

That is all for basic networking. General network parameters are set in
*group_vars/all/general_settings/network.yml* file, and nodes parameters are
defined in the node’s files.
Nodes *network_interfaces* are linked to logical networks.

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

Right now, only *os* and *bluebanquise* are set. This means two or three
(depending of the operating system) repositories will be added to nodes, and
they will bind to repository_ip in ice1-1.yml .

See the repositories_client role part of the documentation for advanced
configurations.

Note also that if you wish to define different repositories per equipment, you
can easily use variable precedence mechanism seen in the Ansible tutorial to
define repositories variable in each equipment group, or even for each node.

NFS
^^^

File *group_vars/all/general_settings/nfs.yml* allows to set NFS shared folders
inside the cluster. Comments in the file should be enough to understand this
file.

General
^^^^^^^

File *group_vars/all/general_settings/general.yml* configure few main parameters:

* Time zone (very important, should match the one of your current management server)

Do not bother right now about the other parameters.

And that is all for general configuration. Finally, let’s check the equipment
default parameters.

Review equipment default parameters
-----------------------------------

Last part, and probably the most complicated, are equipment default parameters.

Remember Ansible precedence mechanism. All variables in group_vars/all/ have
less priority, while variables in group_vars/* have a higher priority.

The idea here is the following: group_vars/all/equipment_all/ folder contains
equipment default parameters for all nodes. Here authentication, and
equipment_profile. You have to tune these parameters to match your exact
"global" need, and then copy (if needed) part of these files into dedicated
group_vars folder for each equipment group, and tune them according to these
equipment specific parameters.

.. note::
  You can copy the whole equipment_profile.yml content from equipment_all to
  equipment_X folders, **or better**, create a new file in equipment_X and only
  set the parameters that are different from the global parameters.

For example, open file
/etc/bluebanquise/inventory/group_vars/all/equipment_all/equipment_profile.yml,
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

Open file group_vars/equipment_typeC/equipment_profile.yml and set
access_control to disabled.

Now check again:

.. code-block:: bash

  [root@]# ansible-inventory --host compute1 --yaml | grep ep_access_control
    ep_access_control: disabled
  [root@]#

Same apply for all equipment_profile parameters. You define a global set of
parameters in equipment_all, which act as a global/default set, and then copy
(all or a part of them) and tune this set for each equipment group if needed.

.. warning::
  **IMPORTANT**: equipment_profile variables and authentication variables are
  not standard. It is **STRICTLY FORBIDDEN** to tune them outside default
  (group_vars/all/equipment_all/equipment_profile.yml) or an equipment group
  (group_vars/equipment_*). For example, you cannot create a custom group and
  define some equipment_profile parameters for this group. If you really need to
  do that, add more equipment groups and tune this way. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.

Equipment profile
^^^^^^^^^^^^^^^^^

Equipment profiles are variables dedicated to groups of nodes equipment. These
variables cover most of the hardware, operating system, PXE needs, etc. of the
related nodes.

Except for operating system and partitioning, default values should match for
a simple cluster with standard hardware.

Lets review them:

PXE
"""

* **ep_ipxe_driver**
   * Possible values:
      * default
      * snp
      * snponly
   * Notes:
     See https://ipxe.org/appnote/buildtargets.
     Most of servers should accept default driver, but snp or snponly can be required on some (with many NICs for example).
* **ep_ipxe_platform**
   * Possible values:
      * pcbios
      * efi
   * Notes:
     This is the BIOS firmware type.
     Should be detected automatically, but some roles need to force it.
* **ep_ipxe_embed**
   * Possible values:
      * standard
      * dhcpretry
      * noshell
   * Notes:
     standard is ok for most cases. dhcpretry is to be used on networks where
     link on switch may take some time to go up. In dhcpretry mode, the iPXE rom
     will indefinitely try to get an ip from the dhcp.
     noshell is similar to standard, but without shell in case of issues. This
     allows "exit" EFI boot, for specific devices (like Nvidia DGX).

* **ep_preserve_efi_first_boot_device**
   * Possible values:
      * true
      * false
   * Notes:
     Try to force grub to restore EFI boot order during OS deployment. Allows to
     keep PXE first for example.

* **ep_console**
   * Notes:
     Custom value: the server console to be used. For example: console=tty0 console=ttyS1,115200n8

* **ep_kernel_parameters**
   * Notes:
     Custom value: additional kernel parameters to be added on kernel line.

* **ep_access_control**
   * Possible values:
      * enforcing
      * permissive
      * disabled
   * Notes:
     Activate or not the access control (SELinux, etc.).

* **ep_firewall**
   * Possible values:
      * true
      * false
   * Notes:
     Activate or not the firewall (firewalld, etc.).

* **ep_partitioning**
   * Notes:
     Custom value: contains the partitioning multiple lines to be used. It is
     expected here native distribution syntax. For example, for RHEL/CentOS, use
     plain kickstart partitioning syntax (allows full custom partitioning).

* **ep_autoinstall_pre_script**
   * Notes:
     To add a multiple lines %pre script in the auto deployment file (kickstart,
     autoyast, preseed, etc.)

* **ep_autoinstall_post_script**
   * Notes:
     To add a multiple lines %post script in the auto deployment file (kickstart,
     autoyast, preseed, etc.)

* **ep_operating_system**
   * **distribution**
      * Notes:
        Custom value: set the distribution to be used here. This will be
        directly related to the repository used. Standard values are: centos,
        redhat, debian, ubuntu, opensuse, etc.
   * **distribution_major_version**
      * Notes:
        Custom value: set the distribution major version number or string.
   * **distribution_version**
      * Notes:
        Custom and optional value: set the distribution minor/custom version to
        be used. This will force repositories and PXE to use a minor version
        instead of relying on a major.
   * **repositories_environment**
      * Notes:
        Custom and optional value: set a production environment, to prepend all
        paths to be used (see repositories_client role documentation). For
        example: production, staging, test, etc.

* **ep_equipment_type**
   * Possible values:
      * server
      * any other custom values but not "server"
   * Notes:
     If server, then PXE files will be generated by the pxe_stack role. If not,
     then value can be custom (and no PXE files will be generated).

* **ep_configuration**
   * keyboard_layout**
      * Possible values:
         * us
         * fr
         * etc.
      * Notes:
        Set the keyboard layout.
   * system_language**
      * Possible values:
         * en_US.UTF-8
         * etc.
      * Notes:
        Set the system locals. It is strongly recommended to keep en_US.UTF-8.

* **ep_hardware**
   * Notes:
     Multiple fields to define system architecture. Some addon roles (like slurm)
     may rely on these values.

* **ep_equipment_authentication**
   * **user**
      * Notes:
        Custom value: set the BMC, storage bay controller, switch, etc. user.
   * **password**
      * Notes:
        Custom value: set the BMC, storage bay controller, switch, etc. password.

Authentication
^^^^^^^^^^^^^^

Authentication file allows to define default root password for all nodes, and
default public ssh keys lists.

To generate an sha512 password, use the following command (python >3.3):

.. code-block:: text

  python -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'

We need to ensure our management1 node ssh public key is set here.

Get the content of /root/.ssh/id_ed25519.pub and add it in this file. At the same
time, **remove the ssh key provided here as example**.

It is possible to do it automatically using the following command:

.. code-block:: text

  # Copy public key of the mgmt to the inventory
  /usr/bin/sed -i -e "s#- ssh-rsa.*#- $(cat /root/.ssh/id_ed25519.pub)#" \
    /etc/bluebanquise/inventory/group_vars/all/equipment_all/authentication.yml

.. warning::
  If you update the managements ssh keys, do not forget to update this file.

Review groups parameters
------------------------

Last step is to check and review example of equipment_profile tuning in each of
the group_vars/equipment_XXXXXX folders. Adapt them to your needs.

If you prefer, you can copy the whole
group_vars/all/equipment_all/equipment_profile.yml file into these folders, or
simply adjust the parameters you wish to change from default.

Once done, configuration is ready.

Remember that a data model is available in resources/data_model.md on the
BlueBanquise github.

-------------

It is time to deploy configuration on management1.
