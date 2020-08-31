Access control
--------------

Description
^^^^^^^^^^^

This role ensure the node current status comply with
ep_access_control variable.

Instructions
^^^^^^^^^^^^

None

Input
^^^^^

**hostvars[inventory_hostname]**

* ep_access_control

Output
^^^^^^

Set SELinux, AppArmor, etc status.

To be added
^^^^^^^^^^^

Check if no packages are needed when enforcing after a selinux --disabled
kickstart.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
