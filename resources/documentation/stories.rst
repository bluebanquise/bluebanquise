=======
Stories
=======

This part contains few stories to help you face common tasks / issues seen
while using the stack.

Management and main configuration
=================================

Versioning the inventory
------------------------

It is a good practice to version the whole /etc/bluebanquise/inventory/
folder, to keep track of all changes made, and be able to revert in case of
issues.

It may even be better to use an external git platform (gitlab,
etc.) to backup the whole configuration, and be able to push changes from the
cluster to this platform.

.. warning::
  Never use a public repository (like github) to store your inventory, as it
  contains sensitive data about your infrastructure.

To create a basic git repository, assuming you already have an existing
configuration in /etc/bluebanquise/inventory/, do:

.. code-block:: text

  cd /etc/bluebanquise/inventory/
  git init
  git add --all
  git commit --author="my_name <my_name@my_mail.org>" -m "First commit"

It is now possible to commit new changes after each configuration change.

You can find a lot on the web about correct git repository usage, creating
branches, etc.

Few useful commands:

* `git log`: display recent logs of the current repository
* `git reset --soft HEAD~1`: undo the last commit

.. note::
  If used, it may be also a good idea to version the
  /etc/bluebanquise/playbooks/ and /etc/bluebanquise/roles/custom/ folders.

Adding a new repository
-----------------------

To add a new repository, simply create its root folder (if not
existing), using the distribution to be used, the major distribution version
associated, and the architecture:

.. code-block:: text

  mkdir /var/www/html/repositories/centos/8/x86_64/

Then create your new repository folder:

.. code-block:: text

  mkdir /var/www/html/repositories/centos/8/x86_64/my_repo

And add it to your global repositories, into file
/etc/bluebanquise/inventory/group_vars/all/general_settings/repositories.yml or
if this repository is only associated with a specific equipment group, add it
into the repositories.yml associated with the equipment_profile associated, for
example in file
/etc/bluebanquise/inventory/group_vars/equipment_X/repositories.yml .

If needed, it is also possible to define minor version based repositories. To
do so, simply replace the major version by the minor version, and use the
`ep_operating_system.distribution_version` variable to force usage of a minor
distribution version for the equipment groups associated with this new
repository.

.. code-block:: text

  mkdir /var/www/html/repositories/centos/8.2/x86_64/

.. code-block:: text

  [root@management1 ~]# cat /etc/bluebanquise/inventory/group_vars/equipment_X/equipment_profile.yml | grep distribution
    distribution: centos
    distribution_major_version: 8
    distribution_version: 8.2
  [root@management1 ~]#

It is also possible to add an environment associated to a repository. To do so,
add the environment name after the *repositories* folder. Assuming here we wish
to create a new *production* repository:

.. code-block:: text

  mkdir /var/www/html/repositories/production/centos/8.2/x86_64/

  .. code-block:: text

    [root@management1 ~]# cat /etc/bluebanquise/inventory/group_vars/equipment_X/equipment_profile.yml | grep -E 'distribution|environment'
      distribution: centos
      distribution_major_version: 8
      repositories_environment: production
    [root@management1 ~]#

.. _update-management-nodes-configuration:

Update management nodes configuration
-------------------------------------

After each change in the inventory, it is needed to update the management nodes
configuration (and sometime even all nodes configurations if the change has a
wide impact).

To update the main configuration, simply re-run your management playbook.
However, few tips:

1. Do a dry run first before running a playbook on a management node.

To do so, use the `--check --diff` arguments with the `ansible-playbook`
command.

For example:

.. code-block:: text

  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --diff --check

2. If you have multiple managements nodes, update them one after the other, using
the `--limit` argument, specifying the nodes each time. This can be combined
with the dry run seen in 1.

For example:

.. code-block:: text

  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --limit management1
  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --limit management2
  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --limit management3

Nodes
=====

.. _adding-a-new-node:

Adding a new node
-----------------

To add a new node, go into the /etc/bluebanquise/inventory/cluster/nodes folder.

Then here, find the file related to the master group of the new node. If you
need to create a new master group, refer to the related story bellow.

Open the file, and find the equipment_profile related to this node. If you
need to create a new equipment_profile group, refer to the related story bellow.

Now, simply add the node under the equipment_profile group, under *hosts*:

.. code-block:: yaml

  mg_computes:
    children:
      equipment_typeC:
        hosts:
          c001:  <<<< my new node

You may also wish to add some network to the node. To do so, add a
network_interfaces list this way.

.. code-block:: yaml

  mg_computes:
    children:
      equipment_typeC:
        hosts:
          c001:
            bmc:                        # This instruction defines an attached BMC
              name: bmanagement1        # This is the hostname of the BMC
              ip4: 10.10.3.1            # This is the ipv4 of the BMC
              mac: 08:00:27:dc:f8:f6    # This is the MAC hardware address of the BMC (for DHCP)
              network: ice1-1           # This is the logical network this interface is connected to. Logical networks will be seen later.
            network_interfaces:         # This is an instruction, to define bellow all host's NIC (Network Interface Controllers)
              - interface: enp0s3       # This is the NIC name ('ip a' command to get NIC list)
                ip4: 10.10.3.1          # This is the expected ipv4 for this NIC
                mac: 08:00:27:dc:f8:f5  # This is the NIC MAC address, for the DHCP
                network: ice1-1         # This is the logical network this NIC is linked to
              - interface: ib0          # This is another NIC, not in the dhcp so no MAC is provided
                ip4: 10.20.3.1
                network: interconnect-1

Then use the ansible-inventory command to check that the new host is listed on
the configuration and seen by Ansible:

.. code-block:: text

  [root@management1 ~]# ansible-inventory --graph
  @all:
    |--@mg_computes:
    |  |--@equipment_typeC:
    |  |  |--c001
    |--@mg_logins:
    |  |--@equipment_typeL:
    |  |  |--login1
    |--@mg_managements:
    |  |--@equipment_typeM:
    |  |  |--management1
    |--@ungrouped:
  [root@management1 ~]#

Now, since we added a new node, replay the playbooks on management nodes (see
:ref:`update-management-nodes-configuration`) and if you are using the
hosts_file role on all the cluster nodes, also replay their playbook, maybe
limiting the execution to the needed roles, using tags. For example:

.. code-block:: text

  ansible-playbook /etc/bluebanquise/playbooks/computes.yml -t hosts_file

Adding a new range of nodes
---------------------------

You may need to add a new range of nodes. You can do it manually, adding them
one by one, or simply use a small bash script to generate the content you need.

We assume here you need to generate a new range of c[1-4] of nodes, with ip
on range 10.10.3.[1-4]. Same kind of ranges for their BMC and interconnect.

Create a file /root/gen.sh with the following content:

.. code-block:: bash

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

You should now have a file named *computes.yml* inside your current folder with
the desired content. Refer :ref:`adding-a-new-node` and
:ref:`update-management-nodes-configuration` stories seen above on how now
update the cluster configuration.

Adding a new master group
-------------------------

You may need to create a new master group, for a new kind of range of equipment.

The stack is fully dynamic regarding groups. The only thing you need is to
create a new file with the master group name inside of
/etc/bluebanquise/inventory/cluster/nodes/

For example, if you wish to create a new group "switches", create file
/etc/bluebanquise/inventory/cluster/nodes/switches.yml and add the following
content in the file:

.. code-block:: yaml

  mg_switches:
    children:

The master group is now created.

Note that master groups must always be prefixed by the string *mg_* to be
detected by the stack. It is also possible for advanced users to change this
prefix pattern in the general_settings part.

Adding a new equipment_profile group
------------------------------------

To create a new equipment profile, create its associated folder. We will assume
here that you wish to create equipment profile equipment_X:

.. code-block:: text

  mkdir /etc/bluebanquise/inventory/group_vars/equipment_X

Then, if this equipment need to be different than the generic equipment_profile
configuration (/etc/bluebanquise/inventory/group_vars/all/equipment_all/),
create new files into /etc/bluebanquise/inventory/group_vars/equipment_X and use
Ansible precedence mechanism to set your settings.

You can refer to the example inventories in resources/examples/ to see more of
these files.

You can now add nodes into this equipment profile. See :ref:`adding-a-new-node`.

Adding a custom group
---------------------

You can add custom groups in the stack (for your own convenience). To do so, go
into folder /etc/bluebanquise/inventory/cluster/groups/ .
Here, create a new file, called for example *mygroup*, with the following
content:

.. code-block:: text

  [my_group]
  c[001:004]
  login1

  [my_group:vars]
  color=yellow

You ca now see that the group was created, using `ansible-inventory --graph`
command.

Also note that all variables defined here (this is not a YAML file, so we use
and = to define variables here) are provided to members of `my_group`.

Replacing/Updating a node
-------------------------

When a node fail, you may need to replace it. This means updating its MAC
address and provision/deploy it again.

To do so, edit the file that contains the node, for example
/etc/bluebanquise/inventory/cluster/nodes/computes.yml and simply update the MAC
address.

Then update the dhcp configuration on the management node:

.. code-block:: text

  ansible-playbook /etc/bluebanquise/playbooks/managements.yml -t dhcp_server

The service should already have restarted since an Ansible handler do it when
some configuration files are updated.

Now ensure you can ping the BMC of the new node (if BMC there is).

Ask for a new deployment using bootset (see :ref:`deploying-nodes`).

.. _deploying-nodes:

Deploying nodes
---------------

To deploy or redeploy a node, use the bootset tool. We will assume here we need
to deploy node c001.

First check bootset status of the node:

.. code-block:: text

  [root@management1 ]# bootset -n c001 -s
  [INFO] Loading /etc/bluebanquise/pxe/nodes_parameters.yml
  [INFO] Loading /etc/bluebanquise/pxe/pxe_parameters.yml
  Diskfull: c001
  [root@management1 ]#

Node is set to boot on disk (or maybe nothing if this is the first time node is
used).

As for an os deployment, using:

.. code-block:: text

  bootset -n c001 -b osdploy

.. note::

  bootset accept nodeset ranges, or clustershell groups.

And check again:

.. code-block:: text

  [root@management1 ]# bootset -n c001 -s
  [INFO] Loading /etc/bluebanquise/pxe/nodes_parameters.yml
  [INFO] Loading /etc/bluebanquise/pxe/pxe_parameters.yml
  Next boot deployment: c001
  [root@management1 ]#

Now boot/reboot the target node, and have it boot over PXE.

You can check the process on the node screen/console, but also by monitoring
logs and the bootset tool.

In a first shell, launch:

.. code-block:: text

  journalctl -u dhcpd -u atftpd -f

This will monitor the dhcp and the tftp servers (first couple to dialog with the deploying node).

In a second shell launch:

.. code-block:: text

  tail -f /var/log/httpd/*

This will monitor all the http (apache2) requests: the iPXE chain, and the
kernel/initrd and packages download.

In a last shell, launch:

.. code-block:: text

  watch -n 10 bootset -n c001 -q -s

You will now be able to follow the whole deployment process, steps by steps.

Apply or update nodes configuration
-----------------------------------

To be done.

Changing equipment_profile group of some nodes
----------------------------------------------

To be done.

Manage multiple distribution versions
-------------------------------------

Allows to boot group of nodes with different distributions versions (major or
minor), and use different kernel on each group.

To be done.

Roles and playbooks
===================

Create a custom role
--------------------

To be done.

Security
========

Update root password
--------------------

To be done.

Use vault to enhance inventory security
---------------------------------------

To be done.

Externalize Ansible
-------------------

To be done.
