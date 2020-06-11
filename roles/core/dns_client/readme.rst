DNS client
----------

Description
^^^^^^^^^^^

This role provides a basic /etc/resolv.conf file.

Instructions
^^^^^^^^^^^^


It is possible to add here external DNS servers for clients.
Configuration is made in *group_vars/all/general_settings/external.yml*:

.. code-block:: yaml

  external_dns:
    dns_client:  <<<<<<<<<<
      - 208.67.220.220

Note that this/these external(s) dns will be placed after the cluster internal dns in resolution order.


Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* domain_name
* network[item]
   * .services_ip.dns_ip

Optional inventory vars:

**hostvars[inventory_hostname]**

* external_dns.dns_client

Output
^^^^^^

Files generated:

* /etc/resolv.conf

Changelog
^^^^^^^^^

* 1.0.4: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.3: Added support of multiple DNS servers. Bruno Travouillon <devel@travouillon.fr>
* 1.0.2: Added variable for role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
