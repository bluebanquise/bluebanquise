==============
Access control
==============

It is possible to configure Access control (SELinux status on RHEL systems,
and AppArmor on Ubuntu systems) using the associated ``os_`` variable ``os_access_control``.

It is also possible to set ``access_control_os_access_control`` for standalone usage. Note that ``os_access_control`` precedence ``access_control_os_access_control``.

For RHEL systems, accepted values are:

* ``enforcing``
* ``permissive``
* ``disabled``

For Ubuntu systems, accepted values are:

* ``enforcing``
* ``disabled``
