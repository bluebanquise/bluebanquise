# Node Health Checker

## Description

This role install and configure NHC.

To find more information on NHC or grab latest release, refer to the [NHC
project](https://github.com/mej/nhc) on GitHub.

## Instructions

### General usage

To set checks, define the variable **nhc_checks** and provide all checks with
check name as key and arguments of this check as value. For example:

```yaml
  nhc_checks:
    check_hw_mem_free: 1mb
    check_fs_mount_rw: -f /scratch
    ...
```

If you need to define the same check with several parameters, provide a list of
arguments:

```yaml
  nhc_checks:
    check_hw_mem_free: 1mb
    check_fs_mount_rw:
      - -f /scratch
      - -f /home
    ...
```

### Advanced usage

It is possible to force copy of multiple nhc files (custom checks, scripts,
etc) by setting variable *nhc_files* as a list of file names and content that
should be copied to */etc/nhc/* on the target host. This allows to define your
own **nhc.conf** file, without the default templating.

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
    - name: my_custom_check.nhc
      content: |
        * || SOMEVAR="value"
        * || check_something
        *.foo || another_check 1 2 3
```

You can require installation of additional custom packages (for example
smartmontools, dmidecode, etc), by providing a list named
**nhc_custom_packages_to_install**. This can be useful when using custom nhc
checks.

## Changelog

* 1.1.0: Template nhc_files. Bruno Travouillon <devel@travouillon.fr>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
