DHCP server
-----------

Description
^^^^^^^^^^^

This role provides a standard dhcp server combined with the iPXE roms of BlueBanquise.

Instructions
^^^^^^^^^^^^

Dhcp will only take into account networks from the current iceberg, and with naming related to administration network (by default iceX-Y).

Also, ensure dhcp is set to true for your network.

Changelog
^^^^^^^^^

* 1.0.3: Simplify standard dhcp, create advanced dhcp for complex configurations. oxedions <oxedions@gmail.com>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. oxedions <oxedions@gmail.com>
