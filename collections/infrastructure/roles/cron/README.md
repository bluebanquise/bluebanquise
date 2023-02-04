# cron

## Description

This role simply act as a wrapper to cron Ansible module.

## Instructions

Set needed cron on node/group by defining cron list based on cron module parameters. Example:

```yaml
cron:
  - name: "check dirs"
    minute: "0"
    hour: "5,2"
    job: "ls -alh > /dev/null"
  - name: yum autoupdate
    weekday: "2"
    minute: "0"
    hour: "12"
    user: root
    job: "YUMINTERACTIVE=0 /usr/sbin/yum-autoupdate"
    cron_file: ansible_yum-autoupdate
```

See `**cron** Ansible module page <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/cron_module.html>`_
for the full list of available parameters.

## Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
