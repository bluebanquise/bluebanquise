Repositories server
-------------------

Description
^^^^^^^^^^^

This role simply configure repositories server (only install and start web server).

Instructions
^^^^^^^^^^^^

This role simply install an http server. Repositories files manupulations have to be done manually by system administrator.

Note that repositories structure follows a specific pattern:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +---+   |               |
                        +-----------+     |   |      +--------+
                                    |     |   |      |
                                    v     v   v      v
       /var/www/html/repositories/centos/7.6/x86_64/os

System administrator should create these directories manually, and put packages inside.

Then, repositories that will be setup on clients are stored by default in */etc/ansible/inventory/group_vars/all/general_settings/repositories.yml*.

Keep in mind that it is possible to precedence this file in equipment_profiles groupes, and so put a repository file in for example */etc/ansible/inventory/group_vars/equipment_supermicro_sandy_compute* that will be considered by these nodes over the default one. This can be useful to define diferent repositories for diferent equipments.


Changelog
^^^^^^^^^

* 1.0.2: Regrouped all distribs into a main file. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
