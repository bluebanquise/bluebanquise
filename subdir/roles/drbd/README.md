# DRBD

## Description

This role deploy a basic DRBD cluster to share storage between multiple nodes.
Main target is to be combined with high availability role.

Note: This role is for now considered experimental and should be used with 
care in production environment.

## Instructions

To allow role to find needed packages, you need to add elrepo repositories on 
all the nodes:

```
dnf -y install https://www.elrepo.org/elrepo-release-8.el8.elrepo.noarch.rpm
```

Then define resources to be used by creating a file in the inventory with the 
following content, tuned according to your needs:

```
drbd_resources:
  - name: resource0        # Name of the shared resource
    nodes:                 # List of nodes that share this resource, and ip to be used
      ha1: 10.10.0.1
      ha2: 10.10.0.2
    metadisk: internal     # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/sdb1        # Local disk to be used as physical device
    device: /dev/drbd1     # Virtual disk exposed on hosts
```

It is also possible to ask role to use filesystem Ansible module to 
manage FS (if not used, i.e. no Primary active):

```
drbd_resources:
  - name: resource1        # Name of the shared resource
    nodes:                 # List of nodes that share this resource, and ip to be used
      ha1: 10.10.0.1
      ha2: 10.10.0.2
    metadisk: internal     # See https://manpages.debian.org/unstable/drbd-utils/drbd.conf-8.3.5.en.html, internal by default
    disk: /dev/sdb1        # Local disk to be used as physical device
    device: /dev/drbd1     # Virtual disk exposed on hosts
  - name: resource2
    nodes:
      ha1: 10.10.0.1
      ha2: 10.10.0.2
    metadisk: internal
    disk: /dev/sdb2
    device: /dev/drbd2
    filesystem:
      fstype: ext4
      opts: -O mmp -E mmp_update_interval=5
```
    
Once cluster is running, resources status can be monitored using the following two commands:

```
drbdadm status
drbdmon
```

## Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
