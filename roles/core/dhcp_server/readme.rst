DHCP server
-----------

Description
^^^^^^^^^^^

This role provides a standard and simple dhcp server combined with the iPXE roms of BlueBanquise.
It should be enough for most networks.

Please use advanced version if you need advanced features like shared-networks,
opt61/82 match, or need to force iPXE roms to be used, or use advanced iPXE driver.

Instructions
^^^^^^^^^^^^

This role provides basic features for network relying on MAC only (or range of unknown hosts).

The role will only take into account networks from the current iceberg,
and with naming related to administration network (by default iceX-Y).
In single iceberg configuration, i.e. default, it will consider ice1-Y networks.

For a network to be included in the dhcp,
the variable **is_in_dhcp** must be set to true in the related network configuration.

Note also that dhcp role will use the following optional parameters if they exist in network:

* dhcp_unknown_range: define the range of the subnet, for unregistered hosts.
  Can be useful for temporary connections (laptops, etc) or to detect if an
  hardware is missing in the inventory.
* gateway: define router in the subnet, and so gateway provided by the dhcp server.

Resulting example network could be:

.. code-block:: yaml

  networks:
    ice1-1:
      subnet: 10.11.0.0
      prefix: 16
      netmask: 255.255.0.0
      broadcast: 10.11.255.255
      dhcp_unknown_range: 10.11.254.1 10.11.254.254  # Is optional
      gateway: 10.11.2.1                             # Is optional
      is_in_dhcp: true                               # Must be set to true for dhcp role to integrate this network
      is_in_dns: true
      services_ip:
        pxe_ip: 10.11.0.1                            # Will be used by dhcp for next server
        dns_ip: 10.11.0.1                            # Will be used by dhcp for dns server
        repository_ip: 10.11.0.1
        authentication_ip: 10.11.0.1
        time_ip: 10.11.0.1                           # Will be used by dhcp for time server
        log_ip: 10.11.0.1

Finally, note that the following parameters can be set in the inventory (group_vars/all/general_settings/network.yml):

* default_lease_time
* max_lease_time

Consider increasing the default values once your network is production ready.

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* icebergs_system
* domain_name
* network[item]
   * .is_in_dhcp (triggers if == "true")
   * .subnet
   * .netmask
   * .broadcast
   * .services_ip.pxe_ip
   * .services_ip.dns_ip
   * .services_ip.time_ip

**hostvars[hosts]**

* network_interfaces
   * .ip4
   * .mac

Optional inventory vars:

**hostvars[inventory_hostname]**

* dhcp_server_default_lease_time
* dhcp_server_max_lease_time

* network[item]
   * .dhcp_unknown_range
   * .gateway

**hostvars[hosts]**

* bmc
   * .ip4
   * .mac
   * .name

Output
^^^^^^

Packages installed:

* dhcp server

Files generated:

* /etc/dhcp/dhcpd.conf
* /etc/dhcp/dhcpd.networks.conf
* /etc/dhcp/dhcpd.{{ network }}.conf

Changelog
^^^^^^^^^

* 1.0.7: Set defaults leases. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.4: Added support of multiple DNS servers. Bruno Travouillon <devel@travouillon.fr>
* 1.0.3: Simplify standard dhcp, create advanced dhcp for complex configurations. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
