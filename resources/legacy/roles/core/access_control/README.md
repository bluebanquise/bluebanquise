# Access control

## Description

This role ensure the node current status comply with
ep_access_control variable. This means SELinux status on RHEL systems.

Note that for now, this role does not cover any other system (Ubuntu's AppArmor, etc).

## Instructions

Set either `access_control_ep_access_control` for standalone usage, or `ep_access_control` when in BlueBanquise stack context (variables for equipment profile group related to host usage). Note that `ep_access_control` precedence `access_control_ep_access_control`.

For RHEL systems, accepted values are:

* `enforcing`
* `permissive`
* `disabled`

## Changelog

* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
