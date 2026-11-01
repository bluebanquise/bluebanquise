# ClusterShell

## Description

This role optionally installs ClusterShell, and sets up ClusterShell groups based on Ansible inventory groups.
It can be used in combination with other BlueBanquise stack tools, like `bluebanquise-bootset` or `bluebanquise-power`, to target hosts by group (for example `@fn_compute`).

## Instructions

By default, the role does not install ClusterShell, since ClusterShell is already a base
requirement for the BlueBanquise stack. However, if for any reason you wish the role to install it
using the system native package manager, set `clustershell_install_from_package` to `true`.
On RedHat family systems, the package is provided by the EPEL repository.

Each Ansible group is written as a ClusterShell group, using the nodeset format (for example
`fn_compute: c[001-128]`), in `/etc/clustershell/groups.d/local.cfg`.

Once the role has been deployed, check groups using:

```
nodeset -LL
```

### Python virtual environments

ClusterShell installed in a Python virtual environment reads its configuration from
`<venv>/etc/clustershell`, with a higher priority than `/etc/clustershell`. Groups written only in
`/etc/clustershell` are then not visible from this virtual environment.

BlueBanquise tools run from the `bluebanquise-venv` virtual environment (`/usr/lib/bluebanquise/venv`).
When this virtual environment is installed on the host, the role also writes groups in its
configuration, so BlueBanquise tools can use them.

For another virtual environment, set `clustershell_prefix_path` to its path: the configuration is
then written in `<clustershell_prefix_path>/etc/clustershell` instead of `/etc/clustershell`.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `clustershell_install_from_package` | `false` | Install ClusterShell using the system package manager. |
| `clustershell_prefix_path` | `""` | Prefix of the ClusterShell configuration path (`<prefix>/etc/clustershell`), for a custom virtual environment. |

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs below are only kept for archive.**

* 1.4.0: Unnecessary leading comma in Clustershell template. Leo Magdanello <lmagdanello40@gmail.com>
* 1.3.0: Add optional variable clustershell_prefix_path. Pierre Gay <pierre.gay@u-bordeaux.fr>, Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>
* 1.2.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Prevent dummy user to be included. Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com> 
