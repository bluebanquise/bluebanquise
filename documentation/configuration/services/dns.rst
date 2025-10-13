===
DNS
===

Current DNS server is based on Bind9 (also known as Named).

Enable DNS on a network
=======================

By default, DNS server will be activated on any management network, and integrate in its definition files all hosts from these networks.

If you wish to disable DNS on a specific management network (including indexing nodes for this network), use ``dns_server`` key, and set it to ``false``.

For example, on ``net-admin`` network, to disable DNS on this network:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      dns_server: false

Once activated on a network, the DNS server Ansible role will scan all nodes in the inventory, and if a node is connected via its ``network_interfaces`` to
the network, it will be added in the DNS definition files.

The role will make the DNS server listen on ``services_ip`` address of the network, or on any ip4 defined under ``dns`` key in ``services``, and allow queries on the whole related subnet/prefix:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      dns_server: true
      services_ip: 10.10.0.1

Or:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      dns_server: true
      services:
        dns:
          - ip4: 10.10.0.1

.. warning::

  Since it is a DNS, the ``hostname`` key is not accepted under ``dns``, this is a specific case.

You can add manually listen ip and queries allowed ranges using respectively ``dns_server_listen_on_ip4`` and ``dns_server_allow_query`` lists if needed.

For example:

.. code-block:: yaml

  dns_server_listen_on_ip4:
    - 10.21.1.3
  dns_server_allow_query:
    - 10.21.1.0/24

This can be useful if an interface is manually managed and not present in the Ansible inventory.

Configuration
=============

Domain name
-----------

By default, domain name used is ``cluster.local``.

If global variable ``bb_domain_name`` is set then this value is used.

It is possible to also define domaine name used by setting ``dns_server_domain_name`` value:

.. code-block:: yaml

  dns_server_domain_name: foobar.local

Note that ``dns_server_domain_name`` precedence ``bb_domain_name`` global variable if both are set.

Nodes
-----

The role will scan all hosts defined in the Ansible inventory, and by default will add an entry
for the node main network as direct record, and another record for each logical network node is connected to.

For example:

.. code-block:: yaml

  all:
    hosts:
      node001:
        network_interfaces:
          - interface: eth1
            ip4: 10.10.3.1
            mac: 08:00:27:0d:44:90
            network: net-admin
          - interface: ib0
            ip4: 10.20.3.1
            network: interconnect
            type: infiniband

Will generate the following forward records:

* node001 -> 10.10.3.1
* node001-net-admin -> 10.10.3.1
* node001-interconnect -> 10.20.3.1

.. note::

  See bellow on this page to disable this extended naming feature if needed.

The role also supports alias and will generate a forward record on them too.

.. code-block:: yaml

  all:
    hosts:
      node001:
        alias:
          - foo
          - bar
        network_interfaces:
          - interface: eth1
            ip4: 10.10.3.1
            mac: 08:00:27:0d:44:90
            network: net-admin
          - interface: eth0
            skip: true
          - interface: ib0
            ip4: 10.20.3.1
            network: interconnect
            type: infiniband

* node001 -> 10.10.3.1
* node001-net-admin -> 10.10.3.1
* node001-interconnect -> 10.20.3.1
* foo -> 10.10.3.1
* bar -> 10.10.3.1

Forward and recursion
---------------------

To configure forwarding and integrate this dns server into an existing IT
configuration, set variable ``dns_server_forwarders`` as a list of target forwarders.

.. code-block:: yaml

  dns_server_forwarders:
    - 8.8.8.8
    - 8.8.4.4

You can also enable recursion with the forwarders configuration using the following variable:

.. code-block:: yaml

  dns_server_recursion: yes

.. note::

  To understand difference between forwarding and recursion, please read this explanation found on the web (https://serverfault.com/questions/661821/what-s-the-difference-between-recursion-and-forwarding-in-bind):

  .. code-block:: text

    Forwarding: just passes the DNS query to another DNS server (e.g. your ISP's). Home routers use forwarding to pass DNS queries from your home network's clients to your ISP's DNS servers. For example, for foo.example.com, a forwarding DNS server would first check its cache (did it already ask this question before), and if the answer is not in its cache, it would ask its forwarder (your ISP's DNS server) for the answer, which would respond with either a cached response, or would perform recursion until it figured out the answer.

    Recursion: the DNS server receiving the query takes it upon itself to figure out the answer to that query by recursively querying authoritative DNS servers for that domain. For example, for foo.example.com, a recursor would first query the root servers for what DNS servers are responsible for the .com TLD, then it would ask those servers for example.com, then it would query the servers for example.com for foo.example.com, finally getting the answer to the original query.

Finaly, you can enable ``forward only`` option by setting ``dns_server_forward_only`` to true. Default is false.

.. note::

  An explanation to forward only found on the web (https://unix.stackexchange.com/questions/500871/dns-forward-only):

  .. code-block:: text

    The forward only option might not be the most intuitive name for its function. Essentially, this option prevents the name server from even attempting to contact another remote name server if the defined forwarders are down or not responding. When forward only has been specified, the name server still answers from its authoritative and cached data, but it relies entirely on its defined forwarders without ever trying any other name servers. The option does not mean that the name server should refuse to provide answers for its authoritative zones.
    Or, stated differently, if the option is not specified and a query is not for one of the server's authoritative zones and the query result is not already in cache, then the server first asks one of the forwarders. If the forwarders cannot be reached, then the server begins the name resolution process beginning at the root servers as usual.

Extended naming
---------------

User can enable or disable extended naming using the ``dns_server_enable_extended_names`` variable.
Default is true.

For example, for an host defined this way:

.. code-block:: yaml

  c001:
    alias:
      - foobar
    network_interfaces:
      - name: eth0
        ip4: 10.10.3.1
        network: net-admin
      - name: eth1
        ip4: 10.20.3.1
        network: para
        alias: fuuuuu

If ``dns_server_enable_extended_names: true``, then the following content will be written by default into forward zone:

.. code-block:: text

  c001 IN A 10.10.3.1
  foobar IN A 10.10.3.1
  c001-net-admin IN A 10.10.3.1
  c001-para IN IN A 10.20.3.1
  fuuuuu IN A 10.20.3.1

While if ``dns_server_enable_extended_names: false``, then the following content will be written into forward zone:

.. code-block:: text

  c001 IN A 10.10.3.1
  foobar IN A 10.10.3.1

Override zone
-------------

To optionally override the IP addresses returned by certain host (``response-policy`` bind parameter) you can define ``dns_server_overrides`` variable, like the following content for example:

.. code-block:: yaml

  dns_server_overrides:
    0.uk.pool.ntp.org: 10.11.0.1

In this example, DNS look-ups for *0.uk.pool.ntp.org* will return *10.11.0.1*.

This will cause ``/var/named/override`` to be generated.

Forward only domains
--------------------

You can set forward only on domains using the ``dns_server_forward_only_domains`` list:

.. code-block:: yaml

  dns_server_forward_only_domains:
    - domain: storage_cluster1.local
      forwarder_ip: 10.10.5.10

Raw content
-----------

You can add additional raw content to named.conf file using the ``dns_server_raw_content`` key:

.. code-block:: yaml

  dns_server_raw_content: |  
    zone "localhost" {
      type primary;
      file "master/localhost-forward.db";
      notify no;
    };


If your content have to be added to options, uses the

.. code-block:: yaml

  dns_server_raw_options_content: |  
    also-notify port 5353;
