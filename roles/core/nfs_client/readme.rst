NFS client
----------

Description
^^^^^^^^^^^

This role provides an automatic nfs client that mount targets and create local
directories if needed. It is a more "friendly" way to use NFS compared to 
basic **mount** role.

Instructions
^^^^^^^^^^^^

All configuration is done in *group_vars/all/general_settings/nfs.yml*.

See the **nfs_server** role instructions for more details.

Simply note that paths that should be mounted will be automatically created by
this role if they do not exist.

It is also possible to manipulate mount state using *nfs_client_directories_state*
variable. Default is **mounted**. Refer to `mount module documentation <https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html#parameter-state>`_
to get other possible values.

By default, on SELinux capable and activated systems, the role will 
enable 2 sebooleans, one for /home support and one for httpd support.
To change this behavior, simply update `nfs_client_sebooleans` variable 
which is a list of sebooleans to activate.

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

* 1.3.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Added OpenSUSE 15 support. Neil Munday <neil@mundayweb.com>
* 1.1.0: Change the way sebooleans values are set to allow MI mechanism. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.4: Added new variable to allow all possible mount values in state parameter. Osmocl <osmocl@osmo.cl>
* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
