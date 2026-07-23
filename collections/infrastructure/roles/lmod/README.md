# lmod

## Description

These settings install the Lmod tool (https://lmod.readthedocs.io/) and optionally sets custom module paths.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Note that Lmod is available on the EPEL repository on RHEL-based systems.

If custom module paths are needed, define `lmod_path` as a list in the inventory:

```yaml
lmod_path:
  - /etc/modulefiles
  - /soft/modules
```

These paths will be added to `/etc/profile.d/modules_extra_path.sh` and made available to all users.

## Variables

| Variable   | Description                      | Type | Required |
|:-----------|:---------------------------------|:-----|:--------:|
| lmod_path  | List of extra module search paths | list |    no    |

## Output

Packages installed:

* Lmod

Files generated:

* /etc/profile.d/modules_extra_path.sh (optional, only when `lmod_path` is defined)
