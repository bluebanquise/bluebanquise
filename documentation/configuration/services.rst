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


.. toctree::
   :maxdepth: 2
   :caption: Services:

   services/dhcp