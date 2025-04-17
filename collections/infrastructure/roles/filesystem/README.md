# Filesystem

## Description

This role provides simply provides an interface to `**filesystem** Ansible module <https://docs.ansible.com/ansible/latest/collections/community/general/filesystem_module.html>`_ .

## Instructions

Set needed filesystems using a list:

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

See `**filesystem** Ansible module page <https://docs.ansible.com/ansible/latest/collections/community/general/filesystem_module.html>`_
for the full list of available parameters.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.1.1: Fix empty list. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
