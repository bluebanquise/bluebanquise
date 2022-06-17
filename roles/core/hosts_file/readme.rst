Hosts file
----------

Description
^^^^^^^^^^^

This role provides a basic /etc/hosts files.

**IMPORTANT** This role needs BlueBanquise bb_logic.yml file in Ansible inventory
to operate properly.

Instructions
^^^^^^^^^^^^

This role will gather all hosts from the inventory, and add them, using all
their known internal network connections ip, into */etc/hosts* file.

In case of multiple icebergs system, administrator can reduce the scope of hosts file
by setting ``bb_iceberg_hosts_range`` variable to ``iceberg`` value 
(default is ``all``). ``all`` will inject all Ansible inventory hosts into file,
while setting ``iceberg`` will reduce the gathering to the current iceberg's hosts.

.. code-block:: yaml

  bb_iceberg_hosts_range: all # can be all or iceberg. If not set, default to all.

Additional external hosts can be defined using ``hosts_file_external_hosts`` dict:

.. code-block:: yaml

  hosts_file_external_hosts:
    google_dns: 8.8.8.8

Input
^^^^^

This role is able to parse all BlueBanquise default hosts definition
syntax. Please refer to main documentation for details.

Examples:

.. code-block:: text

   [all]
   my_host ip=10.10.0.1

.. code-block:: yaml

   all:
     hosts:
       my_host:
         ip: 10.10.0.1

.. code-block:: yaml

   all:
     hosts:
       my_host:
         network_interfaces:
           - interface: eno1
             ip4: 10.10.0.1

.. code-block:: yaml

   all:
     hosts:
       my_host:
         network_interfaces:
           - interface: eno1
             ip4: 10.10.0.1/16

.. code-block:: yaml

   all:
     hosts:
       my_host:
         network_interfaces:
           - interface: eno1
             ip4: 10.10.0.1
             network: ice1-1

Changelog
^^^^^^^^^

* 2.0.0: Update role to BlueBanquise 2.0. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.8: Prevent unsorted ranges. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.7: Clean code. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.4: Rewrite whole macro, add BMC alias. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Accelerated mode. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Added role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
