========
Firewall
========

BlueBanquise is using Firewalld firewall on every supported distributions.

Firewalld is a zones based firewall. The main firewall documentation can be found at https://firewalld.org/documentation/

In BlueBanquise, firewall configuration occurs mainly at 2 positions:

1. When the firewall role is executed. This will install, start and configure main settings of the firewall.
2. When a service related role (example dns_server) is applied on the system. The role will open the ports needed by the service in the firewall.

Main configuration
==================

Enable or disable firewall
--------------------------

Enable or disable the firewall service in the os group of the node:

.. code::yaml

  os_firewall: true

Networks and interfaces
-----------------------

Configuration is based on:

1. ``networks`` dictionary
2. Node ``network_interfaces``
3. ``firewall_zones`` dictionary

To add a network of the host to a zone, define the zone name in
``firewall.zone`` in the network. For example:

.. code::yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      firewall:
        zone: internal
    interconnect-1:
      subnet: 10.20.0.0
      prefix: 16
      firewall:
        zone: trusted

For each network interface of the host where the play runs, the
source address ``subnet/prefix`` will be binded to the zone defined in ``firewall.zone`` if
the network must be in the firewall. For example:

.. code::yaml

  mgt1:
    network_interfaces:
      - interface: enp0s3
        ip4: 10.10.0.1
        network: net-admin

Also, the interface will be added in the firewall zone.

Zones advanced configuration
----------------------------

To add or delete custom services that are not handled by any other role, define
the ``firewall_zones`` parameter as below:

.. code::yaml

  firewall_zones:
    - zone: internal           # <<< zone name
      services_enabled:        # <<< list of service to enable
        - high-availability
        - prometheus
      services_disabled:       # <<< list of service to disable
        - cockpit

It is possible to add or delete custom ports and rich rules with the same
parameter:

.. code::yaml

  firewall_zones:
    - zone: internal           # <<< zone name
      ports_enabled:           # <<< list of ports to enable
        - 1234/tcp
      ports_disabled:          # <<< list of ports to disable
        - 5678/tcp
      rich_rules_enabled:      # <<< list of rich rules to enable
        - "rule family=ipv4 forward-port port=443 protocol=tcp to-port=8443"
      rich_rules_disabled:     # <<< list of rich rules to disable
        - 'rule service name="ftp" audit limit value="1/m" accept'
      icmp_block_inversion: yes
      masquerade: yes

Services configuration
======================

BlueBanquise ships with roles that already support some level of firewall
configuration by adding services to the default zone (public).

It is either possible to change this default zone, by setting ``bb_services_firewall_zone``
to the desired zone, for example:

.. code::yaml

  bb_services_firewall_zone: internal

Either, for each role, it is possible to override the default zone by setting
``${rolename}_firewall_zone`` in the inventory.

For example, if you want to add the services of the pxe_stack roles to the
internal zone, you must set the variable ``pxe_stack_firewall_zone: internal``.

Note that roles' dedicated variables will always precedence global ``bb_services_firewall_zone`` variable.
