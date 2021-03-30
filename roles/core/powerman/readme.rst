Powerman
--------

Description
^^^^^^^^^^^

This role provides powerman, to manage nodes power via ipmi (BMC).

Instructions
^^^^^^^^^^^^

To power on node, use:

.. code-block:: text

  powerman --on bar,foo[7,9-10]

Refer to: https://linux.die.net/man/1/powerman

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* icebergs_system

**hostvars[hosts]**

* ep_equipment_authentication.user
* ep_equipment_authentication.password
* bmc
   * .name
   * .ip4

Output
^^^^^^

Packages installed:

* powerman
* freeipmi

Files generated:

* /etc/powerman/powerman.conf

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
