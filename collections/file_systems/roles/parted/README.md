# Parted

## Description

This role provides simply provides an interface to `**parted** Ansible module <https://docs.ansible.com/ansible/latest/collections/community/general/parted_module.html>`_ .

## Instructions

Set needed partitions using a list:

```yaml
parted:
  # Create a new ext4 primary partition
  - device: /dev/sdb
    number: 1
    state: present
    fs_type: ext4
  # Remove partition number 1
  - device: /dev/sdb
    number: 1
    state: absent
  # Create a new primary partition for LVM
  - device: /dev/sdb
    number: 2
    flags: [ lvm ]
    state: present
    part_start: 1GiB
```

See `**parted** Ansible module page <https://docs.ansible.com/ansible/latest/collections/community/general/parted_module.html>`_
for the full list of available parameters.

## Changelog

* 1.1.1: Fix missing list. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
