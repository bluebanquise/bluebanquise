Conman
------

Description
^^^^^^^^^^^

This role provides a conman daemon that logs ipmi serial consoles.

Instructions
^^^^^^^^^^^^

To login into a console, use:

.. code-block:: bash

  conman mynode

To exit, simply press **&** then **.** .

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* icebergs_system

**hostvars[hosts]**

* ep_equipment_type (triggers if == "server")
* ep_equipment_authentication.user
* ep_equipment_authentication.password
* bmc
   * .ip4

Output
^^^^^^

Packages installed:

* conman
* ipmitool

Files generated:

* /etc/conman.conf

Changelog
^^^^^^^^^

* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Tested on ubuntu 18.04 and validated. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
