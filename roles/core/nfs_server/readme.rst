NFS server
----------

Description
^^^^^^^^^^^

This role provides an automatic nfs server that export on good networks desired directories.

Instructions
^^^^^^^^^^^^

All configuration is done in *group_vars/all/general_settings/nfs.yml*:

.. code-block:: yaml

  nfs:
    softwares:                                    # Internal name of the nfs share
      mount: /opt/softwares                       # What path server should export
      export: /opt/softwares                      # Which path clients should mount this NFS (will be automatically created by client role)
      server: arngrim                             # The server that export this storage space
      clients_groups:                             # Group of hosts that will mount it. Can be an equipment group, or a main group (mg), or any other ansible group
        - mg_computes
        - mg_logins
      take_over_network: ice1-1                   # Network used to share this storage space
      export_arguments: ro,no_root_squash,async   # Arguments for the server (export)
      mount_arguments: ro,intr,nfsvers=4.2,bg     # Arguments for the client (mount)

This role will not modify default nfs server configuration (number of threads, nfs v4.2 force, etc).

Note that exported paths will not be created by the role. They must be created by the administrator before running this role.

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* nfs[item]
   * .mount
   * .export
   * .server
   * .clients_groups
   * .export_arguments

Optional inventory vars:

**hostvars[inventory_hostname]**

* nfs[item]
   * .take_over_network

Output
^^^^^^

Add exported folder into /etc/exports .

Packages installed:

* nfs server utils

Changelog
^^^^^^^^^

* 1.2.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.2: Add OpenSUSE support. Neil Munday <neil@mundayweb.com>
* 1.1.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.4: Added molecule tests. osmocl <osmocl@osmo.cl>
* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
