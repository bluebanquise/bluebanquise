# Node Health Checker

## Description

These settings install and configure NHC.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16, provided an NHC package
is available in the configured repositories. By default the role installs `lbnl-nhc`, the package built by the
[NHC project](https://github.com/mej/nhc) (RPM in its GitHub releases). Set `nhc_packages_to_install` to use
another package, for example `nhc-ohpc` from OpenHPC.

## Instructions

### General usage

To set checks, define the variable **nhc_checks** and provide all checks with
check name as key and arguments of this check as value. For example:

```yaml
  nhc_checks:
    check_hw_mem_free: 1mb
    check_fs_mount_rw: -f /scratch
    # ...
```

If you need to define the same check with several parameters, provide a list of
arguments:

```yaml
  nhc_checks:
    check_hw_mem_free: 1mb
    check_fs_mount_rw:
      - -f /scratch
      - -f /home
    # ...
```

### Resources manager

To explicitly set the resources manager (e.g. SLURM, PBS, etc), set the
variable **nhc_resources_manager**:

```yaml
nhc_resources_manager: SLURM
```

If not set, NHC will auto-detect the resources manager.

### Advanced usage

It is possible to force copy of multiple nhc files (custom checks, scripts,
etc) by setting variable *nhc_files* as a list of file names (relative to */etc/nhc/*) and content.
This allows to define your own **nhc.conf** file, without the default templating.
Note that NHC only reads *nhc.conf*, and loads checks functions from *scripts/\*.nhc* files.

For example:

```yaml
  nhc_files:
    - name: nhc.conf
      content: |
        * || export TS=1
        * || export DEBUG=0
        * || export DF_FLAGS="-Tk"
        * || export DFI_FLAGS="-Ti"
        * || check_ps_service -u root -S sshd
        ...
    - name: scripts/my_checks.nhc
      content: |
        function check_my_custom_thing() {
          [[ -e /tmp/ok ]] && return 0
          die 1 "/tmp/ok is missing"
        }
```

You can require installation of additional custom packages (for example
smartmontools, dmidecode, etc), by providing a list named
**nhc_custom_packages_to_install**. This can be useful when using custom nhc
checks.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `nhc_packages_to_install` | `[lbnl-nhc]` | NHC packages. |
| `nhc_custom_packages_to_install` | `[]` | Additional packages needed by checks. |
| `nhc_checks` | `{}` | Checks and their arguments, written to `nhc.conf`. |
| `nhc_resources_manager` | not set (auto-detected) | Resources manager (`SLURM`, `PBS`...). |
| `nhc_files` | `[]` | Files (`name` relative to `/etc/nhc`, `content`) copied as is. |
