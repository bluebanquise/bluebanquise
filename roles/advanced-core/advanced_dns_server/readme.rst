Advanced DNS server
-------------------

Description
^^^^^^^^^^^

This role provides an advanced dns server based on bind, and is expected to
provide more and more features.

Instructions
^^^^^^^^^^^^

This DNS role will automatically add all networks of the cluster, assuming their
variable **is_in_dns** is set to true:

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

It will generate 5 files:

* /etc/named.conf that contains main configuration, and that will try to bind to all networks defined on the host it is deployed on, using **services_ip.dns_ip** variable ip of the network.
* /var/named/forward that contains forward resolution of hosts
* /var/named/forward.soa included in /var/named/forward
* /var/named/reverse that contains reverse resolution of hosts
* /var/named/reverse.soa included in /var/named/reverse

To configure forwarding and integrate this dns server into an existing IT
configuration, use file *group_vars/all/general_settings/external.yml*.
It is possible to add here an external dns to bind to for this internal dns, as
a relay.

.. code-block:: yaml

  external_dns:
    dns_server:  <<<<<<<<<<
      - 208.67.222.222

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* domain_name
* network[item]
   * .services_ip.dns_ip
   * .subnet
   * .prefix
* network_interfaces
   * .ip4

**hostvars[host]**

* network_interfaces
   * .ip4
   * .mac

Optional inventory vars:

**hostvars[inventory_hostname]**

* dns_master
* dns_slaves
* external_dns.dns_server

**hostvars[hosts]**

* alias
* bmc
   * .ip4
   * .mac
   * .name

Output
^^^^^^

Packages installed:

* bind dns server

Files generated:

* /etc/named.conf
* /var/named/forward
* /var/named/reverse
* /var/named/forward.soa
* /var/named/reverse.soa

Changelog
^^^^^^^^^

* 1.1.2: Moved role to advanced core. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.1.0: Added DNS slaves support. Bruno Travouillon <devel@travouillon.fr>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
