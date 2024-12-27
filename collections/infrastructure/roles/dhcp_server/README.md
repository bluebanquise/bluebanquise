# DHCP server

## Description

This role provides a standard and simple dhcp server combined with the iPXE roms of BlueBanquise.
It should be enough for most networks.

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 1 (Networks)
* Section 2 (Hosts definition)
* Section 3.1 (Function Groups)
* Section 3.2 (Hardware Groups)

## Instructions

### Basic usage

This role provides basic features for network relying on MAC, opt61, opt82, match (advanced options combination), or range of unknown hosts.

In single iceberg configuration, which is default, role will only consider networks with naming related to administration network: by default *net-Y*.
In case of multiple icebergs configuration, the role will consider networks with iceberg naming convention: by default *netX-Y*.

For a network to be included in the dhcp,
the variable `dhcp_server` must be set to **true** in the related network configuration (note that if key do not exist, default is **true**). Refer to main Bluebanquise documentation, inventory structure, for more details, or/and see bellow example.

Note also that dhcp role will use the `dhcp_unknown_range` if exist in network configuration. It defines the range of the subnet, for unregistered hosts.
This can be useful for temporary connections (laptops, etc) or to detect if an
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

Note that if both `services` and `services_ip` are set, `services` precedence `services_ip`.

Finally, note that the following parameters can be set in the inventory, to
override default ones:

* `dhcp_server_default_lease_time` (default to 600) to set default lease time
* `dhcp_server_max_lease_time` (default to 7200) to set max lease time
* `dhcp_server_ipxe_driver` to set ipxe default EFI driver (see main BlueBanquise documentation, equipment profiles variables)
* `dhcp_server_ipxe_embed` to set ipxe default embed script (see main BlueBanquise documentation, equipment profiles variables)

Consider increasing the default leases values once your network is production ready.

### Advanced usage

#### Add global options

It is possible to include as many global settings as desired using the `dhcp_server_global_settings` list.

For example:

```yaml
dhcp_server_global_settings:
  - ping-check false
```

Note: do not include the `;` at the end, it is automatically added by the role.

#### Add options per subnet

It is possible to include as many per subnet settings as desired using the `dhcp_server_subnet_settings` defined under the logical network in `networks` dict.

For example:

```yaml
  networks:
    net-1:
      subnet: 10.11.0.0
      prefix: 16
      dhcp_server: true
      dhcp_server_subnet_settings:
        - deny unknown-clients
```

Note: do not include the `;` at the end, it is automatically added by the role.

#### Multiple entries

It is possible to have multiple entries for an host interface in the
configuration.

For example, set a mac address and a dhcp_client_identifier this way:

```yaml
hosts:
  c001:
    network_interfaces:
      - interface: eth0
        ip4: 10.10.3.1
        mac: 08:00:27:36:c0:ac
        dhcp_client_identifier: 00:40:1c
        network: net-1
```

This will create one entry related to mac address and one to dhcp client
identifier.

#### Shared networks

It is possible to combine networks into shared-networks when multiple subnets
are on the same NIC, or when using opt82/option_match parameter.
To do so, add a dedicated optional `shared_network` key in the network definition.

Networks of the same shared network must have the same `shared_network` value, 
which is the name of this share.

For example to add net-1 and net-2 into the same shared network, define them
this way:

```yaml
  networks:
    net-1:
      subnet: 10.10.0.0
      prefix: 16
      shared_network: wolf
    net-2:
      subnet: 10.30.0.0
      prefix: 16
      shared_network: wolf
```

`shared_network` variable is optional and is simply ignored if not set.

#### opt 61 and opt 82

It is possible to use advanced dhcp features to identify an host. The following
parameters are available, for the host and its BMC:

- `mac`: identify based on MAC address. Same than standard dhcp server.
- `dhcp_client_identifier`: identify based on a pattern (string, etc) to recognize an host. Also known as option 61.
- `host_identifier`: identify based on an option (agent.circuit-id, agent.remote-id, etc) to recognize an host. Also known as option 82.
- `match`: identify based on multiple options in combination to recognize an host. Also known as option 82 with hack.

If using `match`, because this features is using a specific 'hack' in the dhcp
server, you **must** define this host in a shared network, even if this shared
network contains a single network (see this very well made page for more
information: http://www.miquels.cistron.nl/isc-dhcpd/).

#### Add dhcp node specific parameters and options

It is possible to add specific dhcp settings to an host interface, which can be
useful in some specific cases.
This is achieved adding a list named `dhcp_server_settings` inside the host's NIC definition.

For example:

```yaml
hosts:
  c001:
    network_interfaces:
      - interface: eth0
        ip4: 10.10.3.1
        dhcp_client_identifier: 00:40:1c
        dhcp_server_settings:
          - option pxelinux.magic code 208 = string
          - option pxelinux.configfile code 209 = text
        network: ice1-1
```

#### Hosts equipment profile level iPXE rom

By default, all hosts will use global `dhcp_server_ipxe_driver` and `dhcp_server_ipxe_embed`
settings.

However, note that the role will read `hw_ipxe_driver` and `hw_ipxe_embed` equipment profile variables, and precedence global settings for hosts that have these values set.

Also, if user whish to use a custom rom, it is possible to define `hw_pxe_filename` which precedence everything for the target hosts. This can be a relative path for tftp protocol (ex: `x86_64/myrom.efi`) or an http path for HTTP protocol (ex: `http://10.10.0.1/x86_64/myrom.efi`).

This allows for example to have an heterogenous cluster, with a group of hosts booting on *snponly* driver, while others boot on *default* one.

## Changelog

* 1.7.1: Fix global logic. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.7.0: Allow services and services_ip together. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.3: Fix double character for ipxe rom. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.2: Fix missing pxe variables. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.1: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.0: Added subnet custom settings. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.1: Fix ip and host orders. Benoit Leveugle <benoit.leveugle@gmail.com>
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
