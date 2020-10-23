NIC with nmcli
--------------

Description
^^^^^^^^^^^

This role configure network interfaces to provide desired ip, prefix, gateway, etc.

This role is still under work, as nmcli is not supported in RHEL 8 for now, and that this role need to handle much more features.

Instructions
^^^^^^^^^^^^

Basic:

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1
      network: ice1-1

Basic + force gateway + force MTU:

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1
      network: ice1-1
      gw4: 10.10.2.1
      mtu: 9000

Alias / Multiple ip per NIC:

Need to specify interface name (ifname)

  - interface: eth0
    ip4: 10.10.0.1
    network: ice1-1
  - interface: eth0:0
    ip4: 172.16.0.1
    network: ice1-2
    ifname: eth0
  - interface: eth0:1
    ip4: 192.168.0.1
    network: network3
    ifname: eth0

Bond:

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

Vlan:

- interface: vlan100
  type: vlan
  vlan_id: 100
  ifname: eth2
  ip4: 10.100.0.1
  network: net-100


Refer to https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html.
Available options are:
* name -> conn_name
* ifname


NA

To be done
^^^^^^^^^^

Add more features, as nmcli Ansible module can do much more.

* VLANs
* LACP/Bond
* Non network linked NIC
* Multi IP

Changelog
^^^^^^^^^

* 1.0.2: Adding Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
