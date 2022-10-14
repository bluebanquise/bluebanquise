# DHCP server

## Description

This role provides a standard and simple dhcp server combined with the iPXE roms of BlueBanquise.
It should be enough for most networks.

## Instructions

### Basic usage

This role provides basic features for network relying on MAC, opt61, opt82, match (advanced options combination), or range of unknown hosts.

In single iceberg configuration, which is default, role will only consider networks with naming related to administration network: by default *net-Y*.
In case of multiple icebergs configuration, the role will consider networks with iceberg naming convention: by default *netX-Y*.

For a network to be included in the dhcp,
the variable `dhcp_server` must be set to **true** in the related network configuration (note that if key do not exist, default is **true**). Refer to main Bluebanquise documentation, inventory structure, for more details, or/and see bellow example.

Note also that dhcp role will use the `dhcp_unknown_range` if exist in network configuration. It defines the range of the subnet, for unregistered hosts.
This Can be useful for temporary connections (laptops, etc) or to detect if an
hardware is missing in the inventory.

By default, this role will try to use as much defined network settings as available.

Example of network configuration, very minimal dhcp server with range of ip dynamically allocated:

```yaml
  networks:
    net-1:
      subnet: 10.11.0.0
      prefix: 16
      dhcp_server: true                                # Must be set to true for dhcp_server role to integrate this network
      dhcp_unknown_range: 10.11.254.1 10.11.254.254    # Is optional
```

Example of network configuration, very basic dhcp server, with all services bind to a single management node:

```yaml
  networks:
    net-1:
      subnet: 10.11.0.0
      prefix: 16
      dhcp_server: true                                # Must be set to true for dhcp_server role to integrate this network
      dhcp_unknown_range: 10.11.254.1 10.11.254.254    # Is optional
      services_ip: 10.10.0.1                           # All services are running on 10.10.0.1
```

Example of network configuration, advanced dhcp server:

```yaml
  networks:
    net-1:
      subnet: 10.11.0.0
      prefix: 16
      dhcp_server: true                                # Must be set to true for dhcp_server role to integrate this network
      dhcp_unknown_range: 10.11.254.1 10.11.254.254    # Is optional
      gateway4:                                        # Is optional
        - hostname: gw1
          ip: 10.11.2.1
      services:
        dns4:                                          # Is optional
          - ip: 8.8.8.8
          - ip: 8.8.4.4
        ntp4:                                          # Is optional
          - hostname: time-a-g.nist.gov
            ip: 129.6.15.28 
        pxe4:                                          # Is optional, needed for pxe
          - hostname: mg1
            ip: 10.11.0.1
```

Finally, note that the following parameters can be set in the inventory, to
override default ones:

* `dhcp_server_default_lease_time` (default to 600) to set default lease time
* `dhcp_server_max_lease_time` (default to 7200) to set max lease time
* `dhcp_server_ipxe_driver` to set ipxe default EFI driver (see main BlueBanquise documentation, equipment profiles variables)
* `dhcp_server_ipxe_embed` to set ipxe default embed script (see main BlueBanquise documentation, equipment profiles variables)

Consider increasing the default leases values once your network is production ready.

### Advanced usage




## Changelog

* 1.5.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.0: Add capability to choose ipxe ROM. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Update role to work with OpenSuSE. Neil Munday <neil@mundayweb.com>
* 1.1.2: Prevent unsorted ranges. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.7: Set defaults leases. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.4: Added support of multiple DNS servers. Bruno Travouillon <devel@travouillon.fr>
* 1.0.3: Simplify standard dhcp, create advanced dhcp for complex configurations. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
