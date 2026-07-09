# modprobe

## Description

These settings provide an interface to the [modprobe Ansible module](https://docs.ansible.com/ansible/latest/collections/community/general/modprobe_module.html) for loading and unloading kernel modules.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Set needed modules using the `modprobe` list in your inventory:

```yaml
modprobe:
  - name: 8021q
    state: present
  - name: dummy
    state: present
    params: 'numdummies=2'
```

See the [modprobe module documentation](https://docs.ansible.com/ansible/latest/collections/community/general/modprobe_module.html) for the full list of available parameters.
