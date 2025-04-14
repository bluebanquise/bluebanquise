# NFS

- [NFS](#nfs)
  * [Description](#description)
  * [Instructions](#instructions)
    + [Define node role](#define-node-role)
    + [Define shared resources](#define-shared-resources)
    + [Advanced usage](#advanced-usage)
      - [Configuration tuning](#configuration-tuning)
      - [Manipulate mounts state](#manipulate-mounts-state)
      - [SELinux](#selinux)
  * [Changelog](#changelog)

## Description

This role setup NFS server and/or NFS client on target host.

* Server part will install needed packages, configure exports, and start services.
* Client part will install needed packages, create needed folders, and mount exported FS from network.

NFS role is a more "friendly" way to use NFS compared to basic **mount** role.

## Instructions

### Define node role

You need to specify node role, when applying this role on a target. By default, role will do nothing on a target node if no role is specified.

If playbook target node is expected to be a server, add `server` value into `nfs_profile` list inside the playbook's vars or inside target node's vars:

```yaml
nfs_profile:
  - server
```

If node is expected to be a client, add client only into the list:

```yaml
nfs_profile:
  - client
```

If node is expected to be both server and client, which can happen, add both in the list:

```yaml
nfs_profile:
  - server
  - client
```

For example, in the playbook:

```yaml
---
- name: managements playbook
  hosts: "mg_managements"
  roles:
    - role: bluebanquise.file_systems.nfs
      tags: nfs
      vars:
        nfs_profile:
          - server
```

### Define shared resources

To use the role, create a file in main inventory, that contains a description
of NFS exports and mounts, as a list under `nfs_shares` variable:

```yaml
nfs_shares:
  - export: /opt/software
    server: storage1
    mount: /opt/software
    clients_groups:
      - mg_computes
      - mg_logins
      - custom_group
    network: ice1-1
    export_options: ro,async
    mount_options: ro,nfsvers=4.2,bg
  - export: /data/home
    server: nfs2
    mount: /home
    clients_groups:
      - ep_computes_x1
    network: interconnect1
    export_options: rw,sync,root_squash
    mount_options: rw,nfsvers=4.2,bg,nosuid,nodev
```

A description of each parameter can be found in table bellow.

Mandatory values are:

| Key            | Description                                                |
| -------------- | ---------------------------------------------------------- |
| export         | Path to be exported from server and mounted from on client |
| server         | NFS server hostname or ip. On server side, used to detect if current host should export this path. On client side, used to identify server to mount from. Note that in case of PCS based HA, user should rely on native exportfs heartbeat resource, not /etc/exports file. |
| mount          | Path on which mount the FS on local client.                |
| clients_groups | Hosts groups that will mount this FS. Used to detect which client should mount which FS. |

Optional values are:

| Key                    | Description |
| ---------------------- | ----------- |
| network                | Network used to share this storage space. If not provided, server will export to all (`*`) and clients will mount using `server` value, not binding to any network |
| export_options      | Arguments for the server (`export`). If no specified, will be `rw,sync,root_squash` |
| mount_options       | Arguments for the client (`mount`). If no specified, will be `rw,fsc,nfsvers=4.2,bg,nosuid,nodev` |
| server_group        | Group whose members will configure NFS as server. Useful for when using `server` parameter as virtual IP |

Please refer to https://linux.die.net/man/5/nfs for detail on export and mount parameters available.

Also read and refer to  https://www.admin-magazine.com/HPC/Articles/Useful-NFS-Options-for-Tuning-and-Management for fine tuning.

Finally, note that paths that should be mounted will be automatically created by
this role if they do not exist.

### Advanced usage

#### Configuration tuning

This role can fine tune NFS server and client, based on https://man7.org/linux/man-pages/man5/nfs.conf.5.html file parameters. Note that only recent Linux distributions can take advantage of this feature (Ubuntu 22.04+, RHEL 7.9+, 8, 9).

To do so, add into your inventory NFS file (the same where you already defined `nfs_shares`) the `nfs_server_tuning` dict:

```yaml
nfs_server_tuning:
  nfsd:
    threads: 8
```

This will result for example to the following configuration:

```ini
[nfsd]
threads=8
```

To get all available parameters, simple cat your `/etc/nfs.conf` file, and use https://man7.org/linux/man-pages/man5/nfs.conf.5.html as a documentation.

It is for example higly recommended to increase threads value to an higher value in case of large number of clients. 32 threads is a good start, but if server is strong, you can
easily go to 64, 128 or even 256 threads if cluster is large.

#### Manipulate mounts state

It is possible to manipulate mount state using *nfs_client_directories_state*
variable. Default is **mounted**. Refer to `mount module documentation <https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html#parameter-state>`_
to get other possible values. This value can be important if using role in chroot environment.

#### SELinux

By default, on SELinux capable and activated systems, the role will
enable 2 sebooleans, one for /home support and one for httpd support.
To change this behavior, simply update `nfs_client_sebooleans` variable
which is a list of sebooleans to activate.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.5.0: Fix skipping host if using IP as server. Added parameter to run server in a group. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.4.4: Fix missing service for nfsv3 in RHEL firewall. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.3: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.2: Fix services names for Debian, Ubuntu and OpenSuse. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.1: Update to BB 2.0 format. Pierre Gay <pierre.gay@u-bordeaux.fr>, Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>
* 1.4.0: Merged client and server. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Added OpenSUSE 15 support. Neil Munday <neil@mundayweb.com>
* 1.1.0: Change the way sebooleans values are set to allow MI mechanism. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.4: Added new variable to allow all possible mount values in state parameter. Osmocl <osmocl@osmo.cl>
* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
