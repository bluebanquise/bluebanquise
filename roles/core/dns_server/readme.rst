DNS server
----------

Description
^^^^^^^^^^^

This role provides a basic DNS server based on bind.

Instructions
^^^^^^^^^^^^

By default, this DNS role will automatically add all networks of the cluster,
assuming their variable **is_in_dns** is set to true:

.. code-block:: yaml

  networks:
    ice1-1:
      subnet: 10.11.0.0
      prefix: 16
      netmask: 255.255.0.0
      broadcast: 10.11.255.255
      is_in_dhcp: true
      is_in_dns: true  <<<<<<<<<<
      services_ip:
        dns_ip: 10.11.0.1

It will generate 3 files:

* /etc/named.conf that contains main configuration, and that will try to bind
  to all networks defined on the host it is deployed on, using
  **services_ip.dns_ip** variable ip of the network.
* /var/named/forward that contains forward resolution of hosts
* /var/named/reverse that contains reverse resolution of hosts

You can change this behaviour and use custom forward and reverse files by
setting the parameter **dns_server_zone_files** to **static** in your
inventory:

.. code-block:: yaml

  dns_server_zone_files: static

With static, it is possible to install tailor made zone files in
roles/core/dns_server/files/{forward,reverse}. The role will copy these files
to the /var/named/ directory on the master DNS. This allows to add any record
type (CNAME, SRV, TXT, etc.) or define your zone files with an external tool.
FIXME DRAFT: need a documentation of the mandatory entries (hostname, hostname-net).

External hosts defined in *group_vars/all/general_settings/external.yml* in
variable **external_hosts** will be automatically added to the DNS
configuration.

To configure forwarding and intergrate this DNS server into an existing IT
configuration, use file *group_vars/all/general_settings/external.yml*. It is
possible to add here an external DNS to bind to for this internal DNS, as a
relay.

.. code-block:: yaml

  external_dns:
    dns_server:  <<<<<<<<<<
      - 208.67.222.222

Changelog
^^^^^^^^^

* 1.1.0: Added DNS slaves support. Bruno Travouillon <devel@travouillon.fr>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
