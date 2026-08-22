# nfs

- [NFS](#nfs)
  * [Description](#description)
  * [Instructions](#instructions)
    + [Define host role](#define-host-role)
    + [Define shared resources](#define-shared-resources)
    + [Advanced usage](#advanced-usage)
      - [Configuration tuning](#configuration-tuning)
      - [Manipulate mounts state](#manipulate-mounts-state)
      - [SELinux](#selinux)

## Description

These settings setup NFS server and/or NFS client on target host.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

* Server part will install needed packages, configure exports, and start services.
* Client part will install needed packages, create needed folders, and mount exported FS from network.

NFS is a more "friendly" way to use NFS compared to the basic **mount** settings.

## Instructions

### Define host role

You need to specify the host profile (server or client) when applying these settings. By default, these settings do nothing on a target host if no profile is specified.

If playbook target host is expected to be a server, add `server` value into `nfs_profile` list inside the playbook's vars or inside target host's vars:

```yaml
nfs_profile:
  - server
```

If host is expected to be a client, add client only into the list:

```yaml
nfs_profile:
  - client
```

If host is expected to be both server and client, which can happen, add both in the list:

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
    - role: bluebanquise.infrastructure.nfs
      tags: nfs
      vars:
        nfs_profile:
          - server
```

### Define shared resources

To use these settings, create a file in main inventory, that contains a description
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
    network: net-admin
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
| mount_options       | Arguments for the client (`mount`). If no specified, will be `rw,fsc,nfsvers=3,bg,nosuid,nodev` |
| server_group        | Group whose members will configure NFS as server. Useful for when using `server` parameter as virtual IP |
| subnet              | Force a specific subnet to be used instead of the one defined in the associated network. For example: `10.10.0.0/24` |

Please refer to https://linux.die.net/man/5/nfs for detail on export and mount parameters available.

Also read and refer to  https://www.admin-magazine.com/HPC/Articles/Useful-NFS-Options-for-Tuning-and-Management for fine tuning.

Finally, note that paths that should be mounted will be automatically created by
these settings if they do not exist.

### Advanced usage

#### Configuration tuning

These settings can fine tune NFS server and client, based on https://man7.org/linux/man-pages/man5/nfs.conf.5.html file parameters. Note that only recent Linux distributions can take advantage of this feature (Ubuntu 22.04+, RHEL 7.9+, 8, 9, Debian 13+).

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

It is possible to manipulate mount state using `nfs_client_directories_state`
variable. Default is `mounted`. Refer to the [mount module documentation](https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html#parameter-state)
for other possible values. This value can be important if using these settings in a chroot environment.

#### SELinux

By default, on SELinux capable and activated systems, these settings will
enable 2 sebooleans, one for /home support and one for httpd support.
To change this behavior, simply update `nfs_client_sebooleans` variable
which is a list of sebooleans to activate.

Default value:

```yaml
nfs_client_sebooleans:
  - use_nfs_home_dirs
  - httpd_use_nfs
```
