Time server
-----------

Description
^^^^^^^^^^^

This role provides a time server/client based on Chrony.

Instructions
^^^^^^^^^^^^

This role will react diffrently if in multi icebergs mode or not.

By default, in non multiple icebergs, server will be the time source reference. If using multiple icebergs hierarchy, then server can be a time reference if at top of the icebergs hierarchy, or simply a time relay with an higher stratum, if not a top server. This stratum calculation is done using **iceberg_level** variable defined in **/etc/bluebanquise/inventory/cluster/icebergs/icebergX** files.

It is possible to use file */etc/bluebanquise/inventory/group_vars/all/general_settings/external.yml* to connect client or server to external time sources (server or pool or servers):

.. code-block:: yaml

  external_time:  <<<<<<<<
    time_server:
      server: # List of possible time servers
        - 0.fr.pool.ntp.org
      pool: # List of possible time pools
        - pool.ntp.org
    time_client:
      server:
      pool:

If set to **time_server**, server/pool will be added in the server configuration. Of set to **time_client**, these will be added in client configuration. It is possible for example to not install a time server and simply bind to an external server/pool using this file.

In case of a need, to force time synchronisation on client side, use:

.. code-block:: bash

  chronyc -a makestep

To be done
^^^^^^^^^^

Icebergs with stratums levels.

Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
