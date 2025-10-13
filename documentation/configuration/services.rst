========
Services
========

Services are daemons that run on management nodes and provide key services to other nodes, like DHCP server, DNS server, NTP server, HTTP server, etc.
These services can be either listening entities (a DNS server is listening on the network), either active pull/push entities (Prometheus is pulling data from nodes to monitor them).

Some of these services need to be deployed on the management nodes, and also have a client part that needs to be deployed on other nodes.

When a service needs to listen on a ip (endpoint), this ip or hostname is set in the networks settings, so that both server and clients can bind to the same configuration.

Services endpoints
==================

The service endpoint is the ip or hostname both server and clients will refer to in their configuration.

For example, if the NTP server endpoint is 10.10.0.7, then NTP server will be configured to listen on this specific ip, while NTP clients will try to reach the NTP server on 10.10.0.7.

There are 2 ways to define endpoints for services in the stack.
Either all services share the same ip, either services are split over multiple ips (multiple management nodes or using virtual ip).
Or both can be shared, like most services using a shared enpoint, and some specific one is using a different ip.

Single endpoint
---------------

If all services are using the same ip, which is often the case for small clusters with a single management server,
then the ``services_ip`` key can be used under the admininstration network:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1

In that case, all services will bind to this ip, and all clients will look for services on this ip.

Multiple endpoints
------------------

If you need to split services over multiple ips or hostnames, it is possible to define them under the ``services`` key.
You will need to refer to each service dedicated documentation to know the exact variables names to use.

For example, for the NTP server, if you need server so listen on 10.10.0.6 and clients to try to reach server on this ip, define it this way:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services:
        ntp:
          - ip4: 10.10.0.6

You can also define an hostname instead of an ipv4:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services:
        ntp:
          - hostname: my-ntp-server
            ip4: 10.10.0.6

In that case, the hostname will be used by clients to reach the server, but server will still have the ip4 in case it is needed for its configuration.

.. warning::

  The DNS service is an exception, as it will ignore hostname and always use the ip4.

Mixed endpoints
---------------

If you wish to have all services bind to the same ip4, but also wish to have some specific service(s) bind to a dedicated endpoint, you can define both
``services`` and ``services_ip``. In that case, ``services`` will precedence ``services_ip`` when defined.

Example:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1
      services:
        ntp:
          - hostname: my-ntp-server
            ip4: 10.10.0.6
          - hostname: google-public-dns
            ip4: 8.8.8.8
            
In this example, all services will bind to 10.10.0.1, except the ntp server that will bind to 10.10.0.6,
and clients will use the DNS from google (this assume that in this configuration we do not deployed an internal DNS).

Services configuration
======================

You will find bellow the detailed configuration available for each service of the stack.

.. toctree::
   :maxdepth: 1
   :caption: Services:

   services/repositories
   services/dhcp
