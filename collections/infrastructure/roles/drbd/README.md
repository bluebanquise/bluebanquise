# DRBD

## Description

This role deploys a basic DRBD 9 (Distributed Replicated Block Device) cluster, to replicate storage between two hosts.
It is intended to be combined with a high availability role (`pcs`).

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

### Requirements

The role configures DRBD 9 (the configuration uses `auto-promote`, a DRBD 9 feature). The DRBD 9 kernel module and tools are not provided by all distributions:

* **RHEL 9/10:** packages `kmod-drbd9x` and `drbd9x-utils` are provided by the [ELRepo](https://elrepo.org) repository. Add it before running the role:

```
dnf -y install https://www.elrepo.org/elrepo-release-9.el9.elrepo.noarch.rpm    # RHEL 9
dnf -y install https://www.elrepo.org/elrepo-release-10.el10.elrepo.noarch.rpm  # RHEL 10
```

* **Ubuntu/Debian:** the mainline kernel only provides DRBD 8.4, which is not supported by the role. The role installs `drbd-dkms` (DRBD 9 module), provided by the [LINBIT DRBD9 Stack PPA](https://launchpad.net/~linbit/+archive/ubuntu/linbit-drbd9-stack) for Ubuntu 22.04 and 24.04. At the time of writing, no public DRBD 9 packages exist for Ubuntu 26.04 and Debian 13 (use LINBIT customer repositories, or build DRBD from sources).
* **OpenSuse Leap:** DRBD 9 is provided by the distribution (`drbd-kmp-default`).

### Resources

Define resources using the `drbd_resources` list. Each resource is shared between the hosts listed in its `nodes` dictionary (two hosts, as more than two nodes require DRBD 9 node ids, not supported by the role).
The first host of `nodes` is the default primary host of the resource: the role promotes the resource to primary on this host, then creates its filesystem and mounts it there.

The first time a resource is created, its data is inconsistent on both hosts: the role then forces its promotion on the default primary host, which starts the initial synchronization to the other host.

Each host must be part of the play, as each one prepares its own local disk.

Minimal example with two resources:

```yaml
drbd_resources:
  - name: resource0                     # Name of the shared resource
    nodes:                              # Hosts sharing this resource, and ip used for replication
      mgt1: 10.10.4.1                   # Default primary host
      mgt2: 10.10.4.2                   # Secondary host
    metadisk: internal                  # Optional, internal by default
    disk: /dev/mapper/drbdpool-drbdata1 # Local disk to be used as physical device
    device: /dev/drbd1                  # Virtual disk exposed on hosts
    port: 7789                          # Optional, resource TCP port, default: 7789

  - name: resource1                     # Name of the shared resource
    nodes:                              # Hosts sharing this resource, and ip used for replication
      mgt1: 10.10.4.1                   # Default primary host
      mgt2: 10.10.4.2                   # Secondary host
    metadisk: internal                  # Optional, internal by default
    disk: /dev/mapper/drbdpool-drbdata2 # Local disk to be used as physical device
    device: /dev/drbd2                  # Virtual disk exposed on hosts
    port: 7790                          # Optional, resource TCP port, default: 7789
```

Full example with partitioning, LVM and automatic mount:

```yaml
drbd_resources:
  - name: resource0                     # Name of the shared resource
    nodes:                              # Hosts sharing this resource, and ip used for replication
      mgt1: 10.10.4.1                   # Default primary host
      mgt2: 10.10.4.2                   # Secondary host
    metadisk: internal                  # Optional, internal by default
    disk: /dev/mapper/drbdpool-drbdata1 # Local disk to be used as physical device
    device: /dev/drbd1                  # Virtual disk exposed on hosts
    port: 7789                          # Optional, resource TCP port, default: 7789
    filesystem:                         # Optional, filesystem created on the DRBD device
      fstype: xfs
    mount:                              # Optional, mount on the default primary host (noauto)
      source: /dev/drbd1
      path: /mnt/mydrbd1
      fstype: xfs
      state: mounted
    logical_volumes:                    # Optional, LVM volume created on each host as local disk
      vg: drbdpool
      lv: drbdata1
      size: 50%VG
      partition: /dev/sdc1
      state: present
    partitioning:                       # Optional, partition created on each host for LVM
      device: /dev/sdc
      number: 1
      state: present
      align: optimal
      label: gpt
      part_type: primary
      part_start: 0%
      part_end: 100%

  - name: resource1                     # Name of the shared resource
    nodes:                              # Hosts sharing this resource, and ip used for replication
      mgt1: 10.10.4.1                   # Default primary host
      mgt2: 10.10.4.2                   # Secondary host
    metadisk: internal                  # Optional, internal by default
    disk: /dev/mapper/drbdpool-drbdata2 # Local disk to be used as physical device
    device: /dev/drbd2                  # Virtual disk exposed on hosts
    port: 7790                          # Optional, resource TCP port, default: 7789
    filesystem:
      fstype: xfs
    mount:
      source: /dev/drbd2
      path: /mnt/mydrbd2
      fstype: xfs
      state: mounted
    logical_volumes:
      vg: drbdpool
      lv: drbdata2
      size: 50%VG
      partition: /dev/sdc1
      state: present
    partitioning:
      device: /dev/sdc
      number: 1
      state: present
      align: optimal
      label: gpt
      part_type: primary
      part_start: 0%
      part_end: 100%
```

### Monitoring

Once the cluster is running, resource status can be monitored with:

```
drbdadm status
drbdmon
```

Example output:

```
[root@mycluster ~]# drbdadm status
resource0 role:Primary
  disk:UpToDate
  mgt2 role:Secondary
    peer-disk:UpToDate

resource1 role:Primary
  disk:UpToDate
  mgt2 role:Secondary
    peer-disk:UpToDate
```

### Removing a resource

To delete a resource configuration (**this will destroy all data on the DRBD device**):

```
drbdadm down resource0
drbdadm invalidate resource0
drbdadm wipe-md resource0
rm -f /etc/drbd.d/resource0.res
rm -f /etc/drbd.d/global_common.conf
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `drbd_resources` | `[]` | List of DRBD resources, see above. |

Resource keys: `name`, `nodes`, `disk`, `device` (required), `port` (default `7789`), `metadisk` (default `internal`), `partitioning`, `logical_volumes`, `filesystem`, `mount` (optional).

## References

- [DRBD 9 user guide](https://linbit.com/drbd-user-guide/drbd-guide-9_0-en/)
