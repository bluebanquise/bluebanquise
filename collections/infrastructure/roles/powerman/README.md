# Powerman

## Description

This role installs and configures [powerman](https://github.com/chaos/powerman), to manage hosts power through
their BMC, using IPMI (`ipmipower` from FreeIPMI).

Supported distributions: RHEL 9/10 (powerman is provided by EPEL), Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

All hosts of the inventory (or of `powerman_restrict_to_group`, else `bb_restrict_to_group`) having a BMC
(`bmc` with a `name`, see the data model) and IPMI credentials in `hw_board_authentication` are added to
`/etc/powerman/powerman.conf`:

```yaml
hw_board_authentication:
  - protocol: IPMI
    user: ADMIN
    password: ADMIN
```

Hosts sharing the same credentials are managed by the same `ipmipower` device. As the file contains BMC
passwords, it is only readable by root and the powerman daemon group (`daemon`, or `powerman` on Suse).

To power on hosts, use:

```
powerman --on c[001-004]
```

Refer to `man powerman` for other actions (`--off`, `--cycle`, `--query`...).

### Force IPMI 2.0 driver

Set `powerman_enable_ipmi_lan_2_0` to `true` to use the IPMI 2.0 (`LAN_2_0`) driver.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `powerman_packages_to_install` | `[freeipmi, powerman]` | Packages to install. |
| `powerman_enable_ipmi_lan_2_0` | `false` | Use the IPMI 2.0 driver. |
| `powerman_restrict_to_group` | `bb_restrict_to_group`, else `all` | Group of hosts to manage. |
| `powerman_enable_services` | `bb_enable_services`, else `true` | Enable powerman service. |
| `powerman_start_services` | `bb_start_services`, else `true` | Start powerman service, and restart it on configuration changes. |

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.4.0: Simplify role code. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.2: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Fix defaults path. Pierre Gay <pierre.gay@u-bordeaux.fr>, Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>
* 1.3.0: add optional variable powerman_enable_ipmi_lan_2_0. Pierre Gay <pierre.gay@u-bordeaux.fr>, Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>
* 1.2.1: Fix error when ep_host_authentication does not contain IPMI credentials. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.2.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Fix bluebanquise-filters package name. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Implement support for externaly defined BMC. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
