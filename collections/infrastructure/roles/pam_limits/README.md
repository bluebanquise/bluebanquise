# Pam_limits

## Description

Allows to set custom pam limits (ulimit) on the system.

## Instructions

These settings handle all arguments listed in the
[Ansible pam_limits module](https://docs.ansible.com/ansible/latest/collections/community/general/pam_limits_module.html).

Example:

```yaml
pam_limits:
  - domain: joe
    limit_type: soft
    limit_item: nofile
    value: 64000
  - domain: smith
    limit_type: hard
    limit_item: fsize
    value: 1000000
    use_max: true
  - domain: james
    limit_type: '-'
    limit_item: memlock
    value: unlimited
    comment: unlimited memory lock for james
```
