Time server
-----------

Description
^^^^^^^^^^^

This role provides a time server/client based on Chrony.

Instructions
^^^^^^^^^^^^

This role will react differently if in multi icebergs mode or not.

By default, in non multiple icebergs, server will be the time source reference.
If using multiple icebergs hierarchy, then server can be a time reference if at
top of the icebergs hierarchy, or simply a time relay with an higher stratum,
if not a top server. This stratum calculation is done using **iceberg_level**
variable defined in **/etc/bluebanquise/inventory/cluster/icebergs/icebergX**
files.

It is possible to configure external time sources for clients or servers in
*/etc/bluebanquise/inventory/group_vars/all/general_settings/external.yml*:

.. code-block:: yaml

  external_time:  <<<<<<<<
    time_server:
      pool: # List of possible time pools
        - pool.ntp.org
      server: # List of possible time servers
        - 0.pool.ntp.org
        - 1.pool.ntp.org
    time_client:
      pool:
      server:

If **time_server** is defined, the pool or server will be added in the server
configuration. If **time_client** is defined, the pool or server will be added
in the client configuration. It is possible to not install any time server but
simply bind to an external pool/server using this file.

**pool** and **servers** are mutually exclusive. If you define both, the role
will default to **pool** to write the Chrony configuration.

In case of a need, to force time synchronization on client side, use:

.. code-block:: bash

  chronyc -a makestep

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* network_interfaces[item]
* networks[item].prefix

Optional inventory vars:

**hostvars[inventory_hostname]**

* external_time
* external_pool
* time_chronyd_options

Output
^^^^^^

* /etc/chrony.conf file
* chrony package
* time zone set from inventory

To be done
^^^^^^^^^^

Icebergs with stratum levels.

Changelog
^^^^^^^^^

* 1.1.0: Set sysconfig OPTIONS for chronyd. Bruno Travouillon <devel@travouillon.fr>
* 1.0.4: Add iburst to allow faster boot time recovery, update macro. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
