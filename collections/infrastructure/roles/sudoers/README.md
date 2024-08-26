# Sudoers

## Description

This role allows to set sudoers users or groups.
It acts as a wrapper around the https://docs.ansible.com/ansible/latest/collections/community/general/sudoers_module.html module.

## Instructions

Set needed sudoers using a list. `name` key is mandatory. See the full list at https://docs.ansible.com/ansible/latest/collections/community/general/sudoers_module.html for available parameters.

```yaml
sudoers:
  # Set 'manu' user as sudoer with passwordless rights and being able to run any commands as sudoer
  - name: manu
    user: manu
    nopassword: true
    commands: ALL
  # Set 'techs' group users as sudoer with passwordless rights and only being able to execute backup command
  - name: techs_group
    group: techs
    commands: /usr/local/bin/backup
```

## Changelog

* 1.3.0: Use community module. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.1: Fix bug when using list of sudo users as a single name. Code provided by @sgaosdgr. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Allow to create dedicated files for some users. Code from @sgaosdgr. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Updated role to install sudo package. Neil Munday <neil@mundayweb.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
