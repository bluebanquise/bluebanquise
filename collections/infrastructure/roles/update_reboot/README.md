# Update & Reboot

## Description

These settings simply allows to update all packages on system and then reboot
to ensure system is fully upgraded, including kernel running.
Can be useful to be run after the `repositories` role in a playbook.
These settings will wait for host to come back after reboot, allowing playbook to
continue to execute after system is rebooted.

## Instructions

By default, these settings will do nothing.

To trigger packages update, you need to set `update_reboot_upgrade_packages` to
`true`.

To reboot hosts after the update, set `update_reboot_reboot` to `true`. Hosts are only rebooted when packages were
updated (nothing is done if all packages were already up to date).

It is also possible to adjust the reboot timeout value, for very slow systems,
using variable `update_reboot_reboot_timeout`. By default, this variable is set
to `600`, which means `600s -> 600/60 = 10 minutes`.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `update_reboot_upgrade_packages` | `false` | Upgrade all packages. |
| `update_reboot_reboot` | `false` | Reboot hosts when packages were upgraded. |
| `update_reboot_reboot_timeout` | `600` | Reboot timeout, in seconds. |
