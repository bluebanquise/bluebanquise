# Access control

## Description

These settings ensure the host current access control status complies with
the `os_access_control` variable. This means SELinux on RedHat family systems,
and AppArmor on Ubuntu, Debian, and Suse family systems.

## Instructions

Set either `access_control_os_access_control` for standalone usage, or `os_access_control` when used in a BlueBanquise stack context (set at the equipment profile group level). Note that `os_access_control` takes precedence over `access_control_os_access_control`.

### RedHat (SELinux)

Accepted values:

* `enforcing`
* `permissive` or `complain` (both map to SELinux permissive mode)
* `disabled`

### Ubuntu / Debian / Suse (AppArmor)

Accepted values:

* `enforcing` — AppArmor service started, all profiles set to enforce mode
* `permissive` or `complain` — AppArmor service started, all profiles set to complain mode
* `disabled` — AppArmor service stopped and disabled
