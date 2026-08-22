# DRBD

## Description

These settings deploy a basic DRBD (Distributed Replicated Block Device) cluster to share storage between multiple hosts.
It is intended to be combined with a high availability role.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

### Requirements

**RHEL 9/10:** DRBD packages are provided by the ELRepo repository. Add it before running these settings:

```
dnf -y install https://www.elrepo.org/elrepo-release-9.el9.elrepo.noarch.rpm
```

**Ubuntu/Debian/OpenSuse:** DRBD is included in the mainline kernel (since 4.x). No additional repository is required.

### Variables

Define resources using the `drbd_resources` list. By default the primary resource host is the one defined first in the `hosts` dict.

Minimal example with two resources:

```yaml
drbd_resources:
  - name: resource0                     # Name of the shared resource
    nodes:                              # List of nodes that share this resource, and ip to be used
      mgt1: 10.10.4.1                  # Name of the default primary resource
      mgt2: 10.10.4.2                  # Name of the default secondary resource
    metadisk: internal                  # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/mapper/drbdpool-drbdata1 # Local disk to be used as physical device
    device: /dev/drbd1                  # Virtual disk exposed on hosts
    port: 7789                          # Resource TCP port, default: 7789

  - name: resource1                     # Name of the shared resource
    nodes:                              # List of nodes that share this resource, and ip to be used
      mgt1: 10.10.4.1                  # Name of the default primary resource
      mgt2: 10.10.4.2                  # Name of the default secondary resource
    metadisk: internal                  # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/mapper/drbdpool-drbdata2 # Local disk to be used as physical device
    device: /dev/drbd2                  # Virtual disk exposed on hosts
    port: 7790                          # Resource TCP port, default: 7789
```

Full example with partitioning, LVM and automatic mount:

```yaml
drbd_resources:
  - name: resource0                     # Name of the shared resource
    nodes:                              # List of nodes that share this resource, and ip to be used
      mgt1: 10.10.4.1                  # Name of the default primary resource
      mgt2: 10.10.4.2                  # Name of the default secondary resource
    metadisk: internal                  # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/mapper/drbdpool-drbdata1 # Local disk to be used as physical device
    device: /dev/drbd1                  # Virtual disk exposed on hosts
    port: 7789                          # Resource TCP port, default: 7789
    filesystem:
      fstype: xfs
      device: /dev/drbd1
    mount:
      source: /dev/drbd1
      path: /mnt/mydrbd1
      fstype: xfs
      state: mounted
    logical_volumes:
      vg: drbdpool
      lv: drbdata1
      size: 50%VG
      pvs: /dev/sdc
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

  - name: resource1                     # Name of the shared resource
    nodes:                              # List of nodes that share this resource, and ip to be used
      mgt1: 10.10.4.1                  # Name of the default primary resource
      mgt2: 10.10.4.2                  # Name of the default secondary resource
    metadisk: internal                  # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/mapper/drbdpool-drbdata2 # Local disk to be used as physical device
    device: /dev/drbd2                  # Virtual disk exposed on hosts
    port: 7790                          # Resource TCP port, default: 7789
    filesystem:
      fstype: xfs
      device: /dev/drbd2
    mount:
      source: /dev/drbd2
      path: /mnt/mydrbd2
      fstype: xfs
      state: mounted
    logical_volumes:
      vg: drbdpool
      lv: drbdata2
      size: 50%VG
      pvs: /dev/sdc
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

## References

- https://linbit.com/drbd-user-guide/drbd-guide-9_0-en/
