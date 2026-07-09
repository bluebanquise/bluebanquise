# Custom Packages

## Description

These settings allow installing custom packages on target systems that are not managed by other BlueBanquise roles.
It is useful for keeping all OS package customizations synced with BlueBanquise without needing extra deployment steps.

## Instructions

These settings work by matching Ansible group names against the keys of the `custom_packages` dictionary.
For each key that matches one of the host's groups, the corresponding list of packages is installed.

It is recommended to define `custom_packages` in a single file under the `all` group
(e.g. `$HOME/bluebanquise/inventory/group_vars/all/addons/custom_packages.yml`)
so all customizations are visible in one place.

Example:

```yaml
custom_packages:
  fn_compute:
    - openmpi
  fn_login:
    - vim
    - '@Development Tools'
  hw_gpu_server:
    - htop
```
