DNS server
----------

Description
^^^^^^^^^^^

This role provides a basic dns server based on bind.

Warning: this dns server is designed to be used as a single dns for the whole
cluster. If you need multiple dns servers in the same cluster, or replication,
please use the advanced dns server role instead.

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
* /var/named/forward.soa included by /var/named/forward
* /var/named/reverse that contains reverse resolution of hosts
* /var/named/reverse.soa included by /var/named/reverse

To configure forwarding and integrate this dns server into an existing IT
configuration, use file *group_vars/all/general_settings/external.yml*.
It is possible to add here an external dns to bind to for this internal dns, as
a relay.

.. code-block:: yaml

  external_dns:
    dns_server:  <<<<<<<<<<
      - 208.67.222.222

To optionally override the IP addresses returned by certain host you define *group_vars/all/general_settings/dns_override.yml* with the following content for example:

.. code-block:: yaml

  dns_overrides:
    0.uk.pool.ntp.org: 10.11.0.1

In this example, DNS look-ups for *0.uk.pool.ntp.org* will return *10.11.0.1*.

This will cause */var/named/override* to be generated.

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

* external_dns.dns_server

**hostvars[hosts]**

* alias
* bmc
   * .ip4
   * .mac
   * .name

* dns_overrides

Output
^^^^^^

Packages installed:

* bind dns server

Files generated:

* /etc/named.conf
* /var/named/forward
* /var/named/reverse
* /var/named/forward.soa
* /var/named/override
* /var/named/reverse.soa

Changelog
^^^^^^^^^

* 1.3.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Change role to use new layout and override feature for issue #608. Neil Munday <neil@mundayweb.com>
* 1.2.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Improve role performances. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Added SOA. Bruno Travouillon <devel@travouillon.fr>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
