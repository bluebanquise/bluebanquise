SSH slave
---------

Description
^^^^^^^^^^^

This role configure the ssh client authorized public key.

Instructions
^^^^^^^^^^^^

This role will ensure remote hosts is having currently defined ssh authorized public keys in their */root/.ssh/authorized_keys* file.

These keys are set in file */etc/bluebanquise/inventory/group_vars/all/all_equipments/authentication.yml*.

Keep in mind that this file can be precedenced with equipment_profiles groups or iceberg groups.

Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
