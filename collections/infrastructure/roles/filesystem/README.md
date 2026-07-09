# Filesystem

## Description

These settings provide an interface to the [community.general.filesystem](https://docs.ansible.com/ansible/latest/collections/community/general/filesystem_module.html) Ansible module.

## Instructions

Define filesystems to create using the `filesystem` list:

```yaml
filesystem:
  - fstype: ext2
    dev: /dev/sdb1
  - fstype: ext4
    dev: /dev/sdb1
    opts: -cc
  - dev: /dev/sde1
    state: absent
```

See the [community.general.filesystem module documentation](https://docs.ansible.com/ansible/latest/collections/community/general/filesystem_module.html)
for the full list of available parameters.
