# Singularity

## Description

Install and configure [SingularityCE](https://sylabs.io/singularity/) (or SingularityPRO): generate
`/etc/singularity/singularity.conf` and the `/etc/singularity/init` script sourced before launching a container
(it cleans the environment, and logs container runs to syslog).

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Pre-requisites

SingularityCE is not provided by distributions repositories. Sylabs publishes RPM and DEB packages with each
[release on GitHub](https://github.com/sylabs/singularity/releases): download them, and add them to a local repository
of the management host (see the **repositories** role), or build them from sources (`rpmbuild -tb singularity-ce-<version>.tar.gz`).

For SingularityPRO, Sylabs provides a private repository after purchase: set `singularity_packages_to_install`
accordingly.

Note that Apptainer (the Linux Foundation fork of Singularity, available in EPEL) uses another configuration file
(`/etc/apptainer/apptainer.conf`) and is not managed by this role.

## Usage

Playbook example:

```yaml
---
- name: Singularity
  hosts: fn_compute
  roles:
    - role: bluebanquise.infrastructure.singularity
```

Main `singularity.conf` settings are exposed as variables (see below). Values are written as is in the file:
quote `"yes"` and `"no"` values, so that YAML does not convert them to booleans.

To add bind paths (mounted in all containers):

```yaml
singularity_bind_path:
  - /etc/localtime
  - /etc/hosts
  - /scratch
```

Set `singularity_manage_conf_file` or `singularity_manage_init_file` to `false` to keep the files installed by the package.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `singularity_packages_to_install` | `[singularity-ce]` | Packages to install. |
| `singularity_manage_conf_file` | `true` | Generate `singularity.conf`. |
| `singularity_manage_init_file` | `true` | Generate `init`. |
| `singularity_allow_setuid` | `"yes"` | `allow setuid`. |
| `singularity_allow_pid_ns` | `"yes"` | `allow pid ns`. |
| `singularity_config_passwd` / `_group` / `_resolv_conf` | `"yes"` | `config passwd`, `config group`, `config resolv_conf`. |
| `singularity_mount_proc` / `_sys` / `_dev` / `_devpts` / `_home` / `_tmp` | `"yes"` | `mount proc`, `mount sys`, etc. |
| `singularity_mount_hostfs` | `"no"` | `mount hostfs`. |
| `singularity_mount_slave` | `"yes"` | `mount slave`. |
| `singularity_bind_path` | `[/etc/localtime, /etc/hosts]` | `bind path` entries. |
| `singularity_user_bind_control` | `"yes"` | `user bind control`. |
| `singularity_enable_fusemount` | `"yes"` | `enable fusemount`. |
| `singularity_enable_overlay` | `"try"` | `enable overlay`. |
| `singularity_enable_underlay` | `"yes"` | `enable underlay`. |
| `singularity_init_log_tag` | `singularity` | Syslog tag of container runs. |
| `singularity_init_log_message` | see `defaults/main.yml` | Syslog message of container runs. |

## ChangeLog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.0.2: Update FQDN. strus38
* 1.0.1: Update package name to singularity-ce. strus38
* 1.0.0: Initial version. strus38
