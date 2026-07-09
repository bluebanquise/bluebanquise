# Sudoers

## Description

These settings allow setting sudoers users or groups.
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
  
If logging is needed, define `sudoers_logging` to `true`.  
