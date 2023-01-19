# Update & Reboot

## Description

This role simply allows to update all packages on system and then reboot
to ensure system is fully upgraded, including kernel running.
Can be useful to be run after `repositories_client` role from CORE in a playbook.
The role will wait for host to come back after reboot, allowing playbook to
continue to execute after system is rebooted.

## Instructions

By default, the role will do nothing.

To trigger packages update, you need to set `update_reboot_upgrade_packages` to
`true`.

To Trigger reboot, you need to set `update_reboot_reboot` to `true`.

It is also possible to ajust the reboot timeout value, for very slow systems,
using variable `update_reboot_reboot_timeout`. By default, this variable is set
to `600`, which means `600s -> 600/60=10 minutes`.

## Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
