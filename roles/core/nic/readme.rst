NIC
---

Description
^^^^^^^^^^^

This role configure network interfaces to provide desired ip, prefix, gateway, etc.

Instructions
^^^^^^^^^^^^

This role provide network configuration based on system files (ifcfg files for RHEL/Centos systems).

User need to restart network or interfaces one by one for changes to take effect after role execution.

Network interfaces configurations are done at host level:

.. code-block:: yaml

  network_interfaces:
    - interface: enp0s3        # Interface name on system
      ip4: 10.11.0.1           # ip v4 to be set
      mac: 08:00:27:de:42:22   # MAC address of this NIC
      network: ice1-1          # Logical network connected to

By default, connections are of type ethernet. It is possible to specify connection type, for example infiniband:

.. code-block:: yaml

  network_interfaces:
    - interface: ib0
      ip4: 10.20.0.1
      network: interconnect-1
      type: infiniband

To configure an LACP bonding, specify slave interfaces, and then create the bond, using bond-slave type and bond type:

.. code-block:: yaml

  network_interfaces:
    - interface: eth0
      type: bond-slave
      master: bond0
    - interface: eth1
      type: bond-slave
      master: bond0
    - interface: bond0
      type: bond
      vlan: false
      bond_options: "mode=4 xmit_hash_policy=layer3+4 miimon=100 lacp_rate=1"
      ip4: 10.100.0.1
      network: ice1-1

To configure a vlan, simply set vlan to true:

.. code-block:: yaml

  network_interfaces:
    - interface: vlan100
      vlan: true
      vlan_id: 100
      physical_device: eth2
      ip4: 10.100.0.1
      network: net-100

A full example with vlan over bond would be:

.. code-block:: yaml

  network_interfaces:
    - interface: eth3
      network: lk1
      ip4: 172.16.0.2
    - interface: bond0
      type: bond
      bond_options: "mode=4 xmit_hash_policy=layer3+4 miimon=100 lacp_rate=1"
      network: ice1-1
      ip4: 172.21.2.102
    - interface: bond0.100
      type: vlan
      network: ice1-2
      ip4: 10.100.0.1
      vlan: true
      vlan_id: 100
      physical_device: bond0
    - interface: bond0.1
      type: vlan
      network: ice1-3
      ip4: 10.1.0.1
      vlan: true
      vlan_id: 1
      physical_device: bond0
    - interface: enp136s0f0
      type: bond-slave
      master: bond0
    - interface: enp136s0f1
      type: bond-slave
      master: bond0

It is also possible to configure multiple ip per interface, using:

.. code-block:: yaml

  network_interfaces:
    - interface: eth3
      network: lk1
      ip4_multi:
        - 172.16.0.2/16
        - 172.16.0.3/16
        - 192.168.1.117/24

MTU and/or Gateway can be set in the network file, and will be applyed to NIC linked to this network.

.. code-block:: yaml

  networks:
    ice1-1:
      subnet: 10.10.0.0
      prefix: 16
      netmask: 255.255.0.0
      broadcast: 10.10.255.255
      dhcp_unknown_range: 10.10.254.1 10.10.254.254
      gateway: 10.10.2.1     <<<<<<<<<<
      mtu: 9000              <<<<<<<<<<
      is_in_dhcp: true
      is_in_dns: true
      services_ip:
        pxe_ip: 10.10.0.1
        dns_ip: 10.10.0.1
        repository_ip: 10.10.0.1
        authentication_ip: 10.10.0.1
        time_ip: 10.10.0.1
        log_ip: 10.10.0.1


To be done
^^^^^^^^^^

Add Ubuntu and Opensuse compatibility if asked for.

Changelog
^^^^^^^^^

* 1.0.3: Update readme. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Fix VLAN and BOND. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
