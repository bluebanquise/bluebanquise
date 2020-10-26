Routes
------

Description
^^^^^^^^^^^

This role set static routes and default route using nmcli tool.

Instructions
^^^^^^^^^^^^

You can define routes at two levels:

* In networks.yml, inside a network. For example:

.. code-block:: yaml

  networks:

    ice1-1:
      subnet: 10.10.0.0
      prefix: 16
      netmask: 255.255.0.0
      broadcast: 10.10.255.255
      routes4:
        - 10.11.0.0/24 10.10.0.2
        - 10.12.0.0/24 10.10.0.2

* Or under host definition, so in hostvars:

.. code-block:: yaml

      hosts:
        management1:
          network_interfaces:
            - interface: enp0s8
              ip4: 10.10.0.1
              mac: 08:00:27:36:c0:ac
              network: ice1-1
              routes4:
                - 10.11.0.0/24 10.10.0.2
                - 10.12.0.0/24 10.10.0.2

.. note::
  Note that to define a default route/gateway, use *0.0.0.0/0* as route to be defined.

To remove a route later (here *10.12.0.0/24 10.10.0.2* on *enp0s8*), use the nmcli command this way:

.. code-block:: text

  nmcli connection show enp0s8 | grep ipv4.routes
  nmcli connection modify enp0s8 -ipv4.routes "10.12.0.0/24 10.10.0.2"

To be done
^^^^^^^^^^

Would be nice to detect if a change is needed... But difficult.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
