NIC with nmcli
--------------

Description
^^^^^^^^^^^

This role configure network interfaces to provide desired ip, prefix, gateway, etc.

This role is still under work, as nmcli is not supported in RHEL 8 for now, and that this role need to handle much more features.

Instructions
^^^^^^^^^^^^

NA

To be done
^^^^^^^^^^

Add more features, as nmcli Ansible module can do much more.

* VLANs
* LACP/Bond
* Non network linked NIC
* Multi IP

Changelog
^^^^^^^^^

* 1.0.2: Adding Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
