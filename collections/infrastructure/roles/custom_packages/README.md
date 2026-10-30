# Custom Packages

## Description

These settings allow installing custom packages on target systems that are not managed by other BlueBanquise roles.
It is useful for keeping all OS package customizations synced with BlueBanquise without needing extra deployment steps.

## Instructions

These settings work by matching Ansible group names against the keys of the `custom_packages_by_group` dictionary.
For each key that matches one of the host's groups, the corresponding list of packages is installed.
A host member of several listed groups gets the packages of all these groups (one installation per group).

It is recommended to define `custom_packages_by_group` in a single file under the `all` group
(e.g. `/var/lib/bluebanquise/inventory/group_vars/all/custom_packages.yml`)
so all customizations are visible in one place.

Example:

```yaml
custom_packages_by_group:
  fn_compute:
    - openmpi
  fn_login:
    - vim
    - '@Development Tools'
  hw_gpu_server:
    - htop
```

Note that package groups, like `@Development Tools` above, are only supported on RedHat family systems (dnf).

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `custom_packages_by_group` | `{}` | Dictionary of Ansible group names, each with the list of packages to install on hosts of this group. |
