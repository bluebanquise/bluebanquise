# Powerman

## Description

This role provides powerman, to manage nodes power via ipmi (BMC).

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 2 (Hosts definition)
* Section 3.2 (Equipment Groups)

## Instructions

To power on node, use:

```
powerman --on bar,foo[7,9-10]
```

Refer to: https://linux.die.net/man/1/powerman

### Force IPMI 2.0 driver

Set the following variable to `true`. Default is `false`.

``` yml
powerman_enable_ipmi_lan_2_0: true
```

## Input

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* icebergs_system

**hostvars[hosts]**

* ep_equipment_authentication.user
* ep_equipment_authentication.password
* bmc
   * .name
   * .ip4

## Output

Packages installed:

* powerman
* freeipmi

Files generated:

* /etc/powerman/powerman.conf

## Changelog

* 1.3.1: Fix defaults path. Pierre Gay <pierre.gay@u-bordeaux.fr>, Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>
* 1.3.0: add optional variable powerman_enable_ipmi_lan_2_0. Pierre Gay <pierre.gay@u-bordeaux.fr>, Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>
* 1.2.1: Fix error when ep_host_authentication does not contain IPMI credentials. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.2.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Fix bluebanquise-filters package name. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Implement support for externaly defined BMC. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
