NIC with nmcli
--------------

Description
^^^^^^^^^^^

This role configure network interfaces to provide desired ip, prefix, gateway, etc.
The role also cover routes definitions on interfaces.

This role provides all features availables in the main nmcli module.
Please refer to `nmcli module documentation <https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html>`_ .

.. warning:
  This role needs **latest** (2.2.0) nmcli.py module.

Instructions
^^^^^^^^^^^^

Stack specific behaviors
""""""""""""""""""""""""

While all of the nmcli module options are supported,
some provides more integrated features:

* **conn_name**: is equal to **interface**, but has higher precedence over
  **interface** if both are set.
* **ifname**: is equal to **physical_device**, but has higher precedence over
  **ifname** if both are set.
* **type**: is set to *ethernet* by default if not set.
* **ip4**: can be set using a simple ipv4, then role will use
  **networks[item.network]['prefix4']** or default to
  **networks[item.network]['prefix']** to complete address. You can force
  address with prefix if string *'/'* is present.
* **ip4_manual**: allows to pass additional list of ip/prefix to role.
* **mtu**: has higher precedence over **networks[item.network]['mtu']** if
  both are set.
* **gw4**: has higher precedence over **networks[item.network]['.gateway4']**
  if set which has higher precedence over **networks[item.network]['.gateway']**
  if set. Note that gw4 is cannot be set at the same time than never_default4
  (mutually exclusives).
* **routes4**: is a list, that defines routes to be set on the interface. See
  examples bellow. Has higher precedence over
  **networks[item.network]['.routes4']** if set.
* **route_metric4**: is to set general metric for gateway or routes (if not set
  on route level) for this interface. Has higher precedence over
  **networks[item.network]['.route_metric4']** if set.
* **never_default4**: is related to ipv4.never-default nmcli parameter
  (DEFROUTE). Has higher precedence over
  **networks[item.network]['.never_default4']** if set.

Basic ipv4
""""""""""

.. code-block:: yaml

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1
      network: ice1-1

Force gateway and MTU
"""""""""""""""""""""

.. code-block:: yaml

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1
      network: ice1-1
      gw4: 10.10.2.1
      mtu: 9000

Multiple ip
"""""""""""

In multiple ip modes, you need to set the prefix yourself:

.. code-block:: yaml

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1
      ip4_manual: 
        - 10.10.0.2/16
        - 10.10.0.3/16
      network: ice1-1

Note: you can use ``ip4_manual`` without ``ip4`` only if 
the corresponding interface is not to be used as main resolution interface
or main interface (which means another interface with an ip4 and linked to 
a management network is set above in the *network_interfaces* list).

Bond
""""

.. code-block:: yaml

  network_interfaces:
    - interface: bond0
      ip4: 10.10.0.1
      network: ice1-1
      type: bond
    - interface: eth0
      type: bond-slave
      master: bond0
    - interface: eth1
      type: bond-slave
      master: bond0

.. warning::
  In BlueBanquise, as the roles are relying on network_interfaces list order,
  never place bond-slave above the bond master (here bond0 definition must be
  set above eth0 and eth1).

Vlan
""""

.. code-block:: yaml

  - interface: eth2.100
    type: vlan
    vlanid: 100
    vlandev: eth2
    ip4: 10.100.0.1
    network: net-100

Refer to `nmcli module documentation <https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html>`_
for more options.

Routes
""""""

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
        - 10.12.0.0/24 10.10.0.2 300

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
                - 10.12.0.0/24 10.10.0.2 300

.. note:
  In route4 list, each element of the list is a tuple with the network
  destination in first position, gateway in second position and optionally
  the metric in third position.

Apply changes
"""""""""""""

By default, if interfaces are down, the role will have them up, and at the same 
time set their configuration.

However, in some cases, users might need to force some updates (for example if 
you wish to set routes on the main interface, etc).

To achieve that, two variables are at disposal:

* ``nic_nmcli_reload_connections``: this variable will trigger a handler that will ask NetworkManager to reload its configuration.
* ``nic_nmcli_force_nic_restart``: this variable will trigger a a task that will manually down and up interfaces. To be used with care.

Changelog
^^^^^^^^^

* 1.5.0: Add ip4_manual entry. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Add DNS4 and DNS4_SEARCH vars logic. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Rewrite logic to prevent crash and ease code reading. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Add routes4, route_metric4, never_default4 and zone. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Add routes support on NIC. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Rewamp full role to handle all nmcli module features. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Adding Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
