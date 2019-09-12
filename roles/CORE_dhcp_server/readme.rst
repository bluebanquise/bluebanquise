DHCP server
-----------

Description
^^^^^^^^^^^

This role provides a standard dhcp server combined with the iPXE roms of BlueBanquise.

Instructions
^^^^^^^^^^^^

Dhcp will only take into account networks from the current iceberg, and with naming related to administration network (by default iceX-Y).

Also, ensure dhcp is set to tru for your network.

It is possible to combine networks into shared-networks when multiple subnets are on the same NIC.
To do so, add a variable in the network definition.

For example to add ice1-1 and ice1-2 into the same shared network, define them this way:

Ice1-1:

.. code-block:: yaml

  networks:
    ice1-1:
      subnet: 10.10.0.0
      prefix: 16
      shared_network: wolf
      ...

And ice1-2:

.. code-block:: yaml

  networks:
    ice1-2:
      subnet: 10.30.0.0
      prefix: 16
      shared_network: wolf
      ...

shared_network variable is optional and is simply ignored if not set.

Changelog
^^^^^^^^^

* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. oxedions <oxedions@gmail.com>
