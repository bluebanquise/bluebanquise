Repositories server
-------------------

Description
^^^^^^^^^^^

This role simply configures repositories server (only install and start web
server).

Instructions
^^^^^^^^^^^^

This role simply install an http server. Repositories files manipulations have
to be done manually by system administrator. Refer to main documentation.

There might be a split between boot images and packages repositories. Boot images
include the installer system which starts the deployment after PXE boot, while
packages repositories include the software that will be installed on the
systems.

Packages repositories structure follows a specific pattern (depending of OS 
distributionand), and includes the minor or major release version in the path.

Example for a minor based environment:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
      /var/www/html/repositories/centos/8.3/x86_64/os/

Example for a major based environment:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/centos/8/x86_64/os/

System administrator should create these directories manually, and put boot
images and packages inside, according to main documentation requirements.

Then, repositories that will be setup on clients are stored by default in
*/etc/bluebanquise/inventory/group_vars/all/general_settings/repositories.yml*.

Keep in mind that it is possible to precede this file in equipment_profiles
groups, and so put a repository file in for example
*/etc/bluebanquise/inventory/group_vars/equipment_supermicro_sandy_compute*
that will be considered by these nodes over the default one. This can be useful
to define different repositories for different equipment.

Input
^^^^^

None

Output
^^^^^^

Http server packages installed.

Changelog
^^^^^^^^^

* 1.1.0: Update role to new vars gathering method. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Regrouped all distribs into a main file. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
