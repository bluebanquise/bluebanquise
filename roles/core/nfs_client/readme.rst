NFS client
----------

Description
^^^^^^^^^^^

This role provides an automatic nfs client that mount targets and create local
directories if needed.

Instructions
^^^^^^^^^^^^

All configuration is done in *group_vars/all/general_settings/nfs.yml*.

See the **nfs_server** role instructions for more details.

Simply note that paths that should be mounted will be automatically created by
this role if they do not exist.

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* nfs[item]
   * .mount
   * .export
   * .server
   * .clients_groups
   * .mount_arguments

Optional inventory vars:

**hostvars[inventory_hostname]**

* nfs[item]
   * .take_over_network

Output
^^^^^^

Create missing folders and mount nfs on them.

Packages installed:

* nfs client utils

Changelog
^^^^^^^^^

* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
