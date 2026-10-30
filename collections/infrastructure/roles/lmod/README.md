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

These paths are appended to `MODULEPATH` by `/etc/profile.d/modules_extra_path.sh`, for all users (sh and bash login shells), without duplicates in nested shells. The file is removed when `lmod_path` is empty.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `lmod_path` | `[]` | Extra module search paths, appended to `MODULEPATH` of all users (`/etc/profile.d/modules_extra_path.sh`, removed when empty). |
