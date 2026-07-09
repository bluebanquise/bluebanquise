# Cron

## Description

These settings simply acts as a wrapper to the cron Ansible module.

## Instructions

Set needed cron jobs on a host or group by defining `cron_jobs` as a list based on cron module parameters. Example:

```yaml
cron_jobs:
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

See the [cron Ansible module page](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/cron_module.html) for the full list of available parameters.
