========
Services
========

Set services endpoint
=====================

We need to define our services endpoint on the net-1 network.
This endpoint is the IP address to be targeted by clients on the network to reach critical services (dns server, time server, etc).
The stack allows to define different IPs or hostnames for each kind of service,
but a magic key exists and allows to define all of them at once with the same value: ``services_ip``
This is enough for our basic cluster.

Edit ``group_vars/all/networks.yml`` and add the key under net-1 network:

.. code-block:: yaml

  networks:
    net-1:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1



----------------

Networks are set as a dict (not a list).

The order doesnt matter, but naming follows a specific rule:
each network starting with prefix ``net-`` is considered an administration network, other networks are considered simple networks.
Admininstration networks are used to deploy systems (PXE, DHCP, etc.) and to handle all vital services (DNS, NTP, etc.). Note that 
most roles take into account if a network is an administration network or not.

For each network, the following parameters are available:

- **prefix**: (mandatory) define the prefix of the network.
- **subnet**: (mandatory) define the subnet of the network.
- **gateway**: define the ip4 gateway of the network if exists.
- **dhcp_server**: add this network (and all linked hosts) to the dhcp server (default True).
- **dns_server**: add this network (and all linked hosts) to the dns server (default True).
- **shared_network**: name of the shared network if exists.
- **services_ip**: allows to define all services ip of the network in once, using a single ip for all (meaning a single management hosts for this network).

Example:

.. code-block:: yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0
      dhcp_server: true
      gateway: 10.10.0.1
      services_ip: 10.10.0.1
    interconnect:
      prefix: 16
      subnet: 10.20.0.0

- **services**: allows to define services ip of the network with more capabilities. Each known service takes an hostname and an ip.
  This can be used for example when services are distributed over multiple management hosts, or when services are using floating virtual ip.

Example:

.. code-block:: yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0
      services:
        dns:
          - ip4: 10.10.0.2
            hostname: mg2-dns4
          - ip4: 8.8.8.8
            hostname: google-public-dns
        pxe:
          - ip4: 10.10.0.1
            hostname: mg1-pxe
        ntp:
          - ip4: 10.10.0.4
            hostname: mg4-time
    interconnect:
      prefix: 16
      subnet: 10.20.0.0

.. note::
  `4` or `6` at end of some keys are related to ipv4 or ipv6, but the ipv6 support is for now limited (if needed, please open a feature request).




.. toctree::
   :maxdepth: 2
   :caption: Services:

   services/dhcp



   