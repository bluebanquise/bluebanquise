========
Services
========

Services are the daemons that make a cluster work as a whole: DHCP and DNS so that hosts find their
address and each other, an HTTP server and a PXE stack so that they can be installed through the
network, a time server so that they all agree on the clock, a log server, a monitoring stack, and
more.

These services usually run on management hosts. Some of them listening for clients (a DNS server
waits for requests), others actively reaching hosts (Prometheus collects metrics from them). Many
also have a client side, configured on the other hosts by the same role or by a companion role.

To keep servers and clients consistent, the address a service listens on (its *endpoint*) is
declared once, in the networks definition, and read by both sides. The second part of this page
explains how.

Here is the detailed configuration available for each service of the stack.

.. toctree::
   :maxdepth: 1
   :caption: Services:

   services/bluebanquise_supervision
   services/conman
   services/dhcp_server
   services/dns_server
   services/drbd
   services/grafana
   services/haproxy
   services/http_proxy
   services/http_server
   services/keepalived
   services/loki
   services/mariadb
   services/podman
   services/prometheus
   services/pxe_stack
   services/rsyslog
   services/time

Services endpoints
==================

A service endpoint is the IP address (or hostname) that both the server and its clients refer to.
If, for example, the NTP endpoint is ``10.10.0.7``, the NTP server listens on this address, and every
NTP client is configured to reach its server there. Declaring it once, in the networks definition,
guarantees both sides always agree.

There are three ways to declare endpoints, from the simplest to the most flexible.

Single endpoint
---------------

On a small cluster with a single management host, all services usually share the same address.
In that case, simply set the ``services_ip`` key on the management network:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1

All services listen on ``10.10.0.1``, and all clients look for them there. This is all most clusters need.

Multiple endpoints
------------------

On larger clusters, services are often spread over several management hosts, or published on
virtual IPs for high availability. Each service then gets its own entry under the ``services`` key
of the network.

Service keys end with ``4`` for IPv4 endpoints, to leave room for IPv6 ones later:

.. list-table::
   :header-rows: 1

   * - Key
     - Service
   * - ``dns4``
     - DNS server (``dns_server``, ``dns_client``)
   * - ``ntp4``
     - Time server (``time``)
   * - ``pxe4``
     - PXE and HTTP deployment server (``dhcp_server``, ``pxe_stack``)
   * - ``log4``
     - Log server (``rsyslog``)
   * - ``repositories4``
     - Packages repositories server (``repositories``)

.. note::

  Keys without the ``4`` suffix (``dns``, ``ntp``, ``pxe``, ``log``, ``repositories``) are the former
  names. They are deprecated, but roles still accept them, so existing inventories keep working.

Each entry is a list, so a service can have several endpoints (two DNS servers, for example). For
instance, to make the NTP server listen on ``10.10.0.6``, and NTP clients reach it there:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services:
        ntp4:
          - ip4: 10.10.0.6

An endpoint can also carry a hostname:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services:
        ntp4:
          - hostname: my-ntp-server
            ip4: 10.10.0.6

Clients then use the hostname to reach the server, while the server keeps using the IP address for
its own configuration.

.. warning::

  The DNS service is an exception: clients need an IP address to reach their DNS server (they
  cannot resolve a name before having one!), so ``hostname`` is ignored for ``dns4`` and the
  ``ip4`` value is always used.

Mixed endpoints
---------------

Both keys can be combined: ``services_ip`` gives a default address to all services, and
``services`` overrides it for the services listed there.

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1
      services:
        ntp4:
          - hostname: my-ntp-server
            ip4: 10.10.0.6
        dns4:
          - ip4: 8.8.8.8

Here, all services use ``10.10.0.1``, except the NTP service, served from ``10.10.0.6``, and DNS:
clients use an external DNS server, ``8.8.8.8`` (in this example, we chose not to deploy an internal
DNS server).

Services configuration
======================

A few settings are shared by all roles managing a service.

Start and enable services
-------------------------

As seen in :doc:`general_settings`, two global variables, ``bb_start_services`` and
``bb_enable_services``, tell roles whether to start services, and whether to enable them at boot.
Both default to ``true``.

Each role also has its own ``<role>_start_services`` and ``<role>_enable_services`` variables, which
take precedence over the global ones. For example, to start the DHCP server even though other
services are kept stopped:

.. code-block:: yaml

  bb_start_services: false
  dhcp_server_start_services: true

This is mostly useful for high availability clusters, where a cluster manager, not systemd, decides
where services run (see :doc:`../scalability/high_availability`).

.. note::

  All service related tasks carry the ``service`` tag. Running a playbook with
  ``--skip-tags service`` configures everything without touching any running daemon, which is handy
  to prepare a host, or when working in containers.

Firewall
--------

When ``os_firewall`` is ``true`` (the default), each role opens the ports or firewalld services it
needs, in the zone defined by ``<role>_firewall_zone``, else ``bb_services_firewall_zone``, else
``public``. These tasks carry the ``firewall`` tag.

If firewalld is not installed or not running yet, roles stop with a message explaining what to do:
install firewalld (the ``firewall`` role does it), or set ``os_firewall: false``.
