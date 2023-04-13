# DRBD

## Description

This role deploy a basic DRBD (Distributed Replicated Block Device) cluster to share storage between multiple nodes.
Main target is to be combined with high availability role.

The role has been tested in a production cluster to create two resources in DRBD (resource0 and resource1)

Tested on : 
```
OS: AlmaLinux 8.7 (Stone Smilodon)
Kernel: 4.18.0-425.19.2.el8_7.x86_64
drbd90-utils-9.23.1-1.el8.elrepo.x86_64
kmod-drbd90-9.1.13-1.el8_7.elrepo.x86_64
ansible [core 2.11.12]
python version = 3.6.8
jinja version = 3.0.3
```

## Instructions

To allow role to find needed packages, you need to add elrepo repositories on 
all the nodes:

```
dnf -y install https://www.elrepo.org/elrepo-release-8.el8.elrepo.noarch.rpm
```

Then define resources to be used by creating a file in the inventory with the 
following content, tuned according to your needs:

**Note**: that by default the primary resource node is the one defined first in the ``drbd_resources.nodes`` list

```
drbd_resources:
  - name: resource0                     # Name of the shared resource
    nodes:                              # List of nodes that share this resource, and ip to be used
      bee-meta1: 10.10.4.1              # Name of the default primary resource
      bee-meta2: 10.10.4.2              # Name of the default secondary resource
    metadisk: internal                  # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/mapper/drbdpool-drbdata1 # Local disk to be used as physical device
    device: /dev/drbd1                  # Virtual disk exposed on hosts
    port: 7789                          # Resource TCP port, default: 7789
    
  - name: resource1                     # Name of the shared resource
    nodes:                              # List of nodes that share this resource, and ip to be used
      bee-meta1: 10.10.4.1              # Name of the default primary resource
      bee-meta2: 10.10.4.2              # Name of the default secondary resource
    metadisk: internal                  # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/mapper/drbdpool-drbdata2 # Local disk to be used as physical device
    device: /dev/drbd2                  # Virtual disk exposed on hosts
    port: 7790                          # Resource TCP port, default: 7789    
```

You can use partioning, LVM creation and automatic mounting of DRBD filesystem:

```
drbd_resources:
  - name: resource0                     # Name of the shared resource
    nodes:                              # List of nodes that share this resource, and ip to be used
      bee-meta1: 10.10.4.1              # Name of the default primary resource
      bee-meta2: 10.10.4.2              # Name of the default secondary resource
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
    partitionning:
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
      bee-meta1: 10.10.4.1              # Name of the default primary resource
      bee-meta2: 10.10.4.2              # Name of the default secondary resource
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
    partitionning:
      device: /dev/sdc
      number: 1
      state: present
      align: optimal
      label: gpt
      part_type: primary
      part_start: 0%
      part_end: 100%
```
    
Once cluster is running, resources status can be monitored using the following two commands:

```
drbdadm status
drbdmon
```

Example:
```
[root@mycluster ~]# drbdadm status
resource0 role:Primary
  disk:UpToDate
  bee-meta2 role:Secondary
    peer-disk:UpToDate

resource1 role:Primary
  disk:UpToDate
  bee-meta2 role:Secondary
    peer-disk:UpToDate
```




To delete the configuration (**will delete all data on the DRBD devices**)
run the following commands :

```
drbdadm down resource0;drbdadm invalidate resource0;drbdadm wipe-md resource0 && rm -f /etc/drbd.d/resource0.res
drbdadm down resource1;drbdadm invalidate resource1;drbdadm wipe-md resource1 && rm -f /etc/drbd.d/resource1.res
rm -f /etc/drbd.d/global_common.conf
```

## Documentations

https://computingforgeeks.com/install-and-configure-drbd-on-centos-rhel/
https://linbit.com/drbd-user-guide/drbd-guide-9_0-en/#p-apps

## Changelog

* 1.0.1: Role improvements. Hamid Merzouki <hamid.merzouki@naverlabs.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
