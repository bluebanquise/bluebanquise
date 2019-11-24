Advanced DHCP server
--------------------

Description
^^^^^^^^^^^

This role provides an advanced dhcp server combined with the iPXE roms of BlueBanquise.
Features like shared_network, opt82, opt61 or snp/snponly roms are provided here for very specific configurations or needs.

Instructions
^^^^^^^^^^^^

Please read first documentation of the standard dhcp server role. Advanced dhcp server provides sames features than standard dhcp server role, but with more options.

Dhcp will only take into account networks from the current iceberg, and with naming related to administration network (by default iceX-Y).

Also, ensure dhcp is set to true for your network.

**Shared network**
""""""""""""""""""

It is possible to combine networks into shared-networks when multiple subnets are on the same NIC, or when using opt82/option_match parameter.
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

**opt 61 and opt 82**
"""""""""""""""""""""

It is possible to use advanced dhcp features to identify an host. The following parameters are available, for the host and its BMC. Note that only one of these must be set for an host/BMC at the same time:

- mac: identify based on MAC address. Same than standard dhcp server.
- dhcp_client_identifier: identify based on a patern (string, etc) to recognise an host. Also known as option 61.
- host_identifier: identify based on an option (agent.circuit-id, agent.remote-id, etc) to recognise an host. Also known as option 82.
- option_match: identify based on multiple options in combinaison to recognise an host. Also known as option 82 with hack.

If using option_match, because this features is using a specific 'hack' in the dhcp server, you **must** define this host in a shared network, even if this shared network contains a single network (see this very well made page for more information: http://www.miquels.cistron.nl/isc-dhcpd/).

Changelog
^^^^^^^^^

* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
