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

There is a split between boot images and packages repositories. Boot images
include the installer system which starts the deployment after PXE boot, while
packages repositories include the software that will be installed on the
systems.

Boot images repositories structure follows a specific pattern and includes the
minor release version in the path:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/centos/7.6/x86_64/os/

Packages repositories structure follows a specific pattern, which defaults to
the major release version in the path:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/centos/7/x86_64/os/

System administrator should create these directories manually, and put boot
images and packages inside.

Note: we recommend to use the same directory path to later sync the Errata
published by upstream operating system vendor.

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

* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Regrouped all distribs into a main file. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
