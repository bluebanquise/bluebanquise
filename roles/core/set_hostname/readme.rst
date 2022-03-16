Set Hostname
-------------------

Description
^^^^^^^^^^^

This role simply set a node hostname.

Instructions
^^^^^^^^^^^^

It is possible to ask for hostname used to be FQDN, by setting variable
**set_hostname_fqdn** variable to *true*. If set to *true*, variable 
**domain_name** must also be defined in the inventory.

Input
^^^^^

Optional inventory vars:

**hostvars[inventory_hostname]**

* set_hostname_fqdn
* domain_name

Changelog
^^^^^^^^^

* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Add fully qualified domain name capability. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
