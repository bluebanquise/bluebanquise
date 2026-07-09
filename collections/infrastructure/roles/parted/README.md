# Parted

## Description

These settings provide an interface to the [parted Ansible module](https://docs.ansible.com/ansible/latest/collections/community/general/parted_module.html).

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

See the [parted Ansible module page](https://docs.ansible.com/ansible/latest/collections/community/general/parted_module.html)
for the full list of available parameters.
