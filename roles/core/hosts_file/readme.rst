Hosts file
----------

Description
^^^^^^^^^^^

This role provides a basic /etc/hosts files.

Instructions
^^^^^^^^^^^^

This role will gather all hosts from the inventory, and add them, using all their known internal network connections ip, into */etc/hosts* file.

System administrator can reduce the scope of this gathering using **hosts_file.range** variable in */etc/bluebanquise/inventory/group_vars/all/general_settings/general.yml*.
Setting **range** to *all* will use all Ansible inventory hosts, while setting **range** to *iceberg* will reduce the gathering to the current host iceberg.

.. code-block:: yaml

  hosts_file:  <<<<<<<<
    range: all # can be all (all hosts) or iceberg (iceberg only)

Another feature is available in this hosts role. In case of multiple icebergs, system administrator may need to define a global network, shared by all nodes of a specific group. This is especially needed in HPC for computational nodes to communicates through an interconnect network.

If using such global network, it is possible to ask this role to define **direct** hosts resolutions of a specific Ansible group to be not on their regular management network, but be set directly on the global network (mostly used in combinaison with slurm and mpi stacks).

To do so, uncomment and edit variable **global_network_settings** in file */etc/bluebanquise/inventory/group_vars/all/general_settings/network.yml*. Note that the role will ignore this variable if it is commented, and will try to use it if not commented.

.. code-block:: yaml

  global_network_settings:  <<<<<<<<
    global_network: interconnect-1  # Define the global network, must exist in networks files
    global_network_group: mg_computes  # Define which group of nodes should use global_network direct resolution

Last point, external hosts defined in *group_vars/all/general_settings/external.yml* at variable **external_hosts** will be automatically added in the */etc/hosts* file.

Changelog
^^^^^^^^^

* 1.0.4: Rewrite whole macro, add BMC alias. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Accelerated mode. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Added role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
