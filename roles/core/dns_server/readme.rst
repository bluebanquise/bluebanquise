DNS server
----------

Description
^^^^^^^^^^^

This role provides a basic dns server based on bind.

Instructions
^^^^^^^^^^^^

This DNS role will automatically add all networks of the cluster, assuming their variable **is_in_dns** is set to true:

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

* /etc/named.conf that contains main configuration, and that will try to bind to all networks defined on the host it is deployed on, using **services_ip.dns_ip** variable ip of the network.
* /var/named/forward that contains forward resolution of hosts
* /var/named/reverse that contains reverse resolution of hosts

External hosts defined in *group_vars/all/general_settings/external.yml* at variable **external_hosts** will be automatically added in the dns configuration.

To configure forwarding and intergrate this dns server into an existing IT configuration, use file *group_vars/all/general_settings/external.yml*.
It is possible to add here an external dns to bind to for this internal dns, as a relay.

.. code-block:: yaml

  external_dns:
    dns_server:  <<<<<<<<<<
      - 208.67.222.222

Changelog
^^^^^^^^^

* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
