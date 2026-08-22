# DHCP server

## Description

These settings provide a standard and simple dhcp server combined with the iPXE roms of BlueBanquise.
It should be enough for most networks.
## Instructions

### Basic usage

These settings provide basic features for network relying on MAC, opt61, opt82, match (advanced options combination), or range of unknown hosts.

All `net-*` networks are included in the DHCP configuration by default. To exclude a network from the DHCP server, set `dhcp_server: false` in the network configuration.

These settings will use `dhcp_unknown_range` if defined in the network configuration. It defines the range of IP addresses dynamically allocated to unregistered hosts, which is useful for temporary connections (laptops, etc.) or to detect hardware missing from the inventory.

By default, these settings will use as much of the defined network settings as available.

Example of network configuration, minimal DHCP server with a range of dynamically allocated IPs:

```yaml
  networks:
    net-1:
      subnet: 10.11.0.0
      prefix: 16
      dhcp_unknown_range: 10.11.254.1 - 10.11.254.254    # Optional
```

Example of network configuration, basic DHCP server with all services bound to a single management host:

```yaml
  networks:
    net-1:
      subnet: 10.11.0.0
      prefix: 16
      dhcp_unknown_range: 10.11.254.1 - 10.11.254.254    # Optional
      services_ip: 10.10.0.1                           # All services running on 10.10.0.1
```

Example of network configuration, full DHCP server with explicit per-service addresses:

```yaml
  networks:
    net-1:
      subnet: 10.11.0.0
      prefix: 16
      dhcp_unknown_range: 10.11.254.1 - 10.11.254.254    # Optional
      gateway4:                                        # Optional
        - hostname: gw1
          ip4: 10.11.2.1
      services:
        dns4:                                          # Optional
          - ip4: 8.8.8.8
          - ip4: 8.8.4.4
        ntp4:                                          # Optional
          - hostname: time-a-g.nist.gov
            ip4: 129.6.15.28
        pxe4:                                          # Optional, required for PXE and HTTP boot
          - hostname: mg1
            ip4: 10.11.0.1
```

Note that if both `services` and `services_ip` are set, `services` takes precedence over `services_ip`.

Finally, note that the following parameters can be set in the inventory, to
override default ones:

* `dhcp_server_default_lease_time` (default to 600) to set default lease time
* `dhcp_server_max_lease_time` (default to 7200) to set max lease time
* `dhcp_server_ipxe_driver` to set ipxe default EFI driver (see main BlueBanquise documentation, equipment profiles variables)
* `dhcp_server_ipxe_embed` to set ipxe default embed script (see main BlueBanquise documentation, equipment profiles variables)

Consider increasing the default leases values once your network is production ready.

### Advanced usage

#### HTTP boot (UEFI HTTP)

When `pxe4` (or `services_ip`) is defined for a network, these settings automatically generates HTTP boot support for that subnet. Clients that send `HTTPClient` in option 60 receive an HTTP URL using the subnet's PXE server address instead of a TFTP filename.

The boot URLs follow the pattern:
- x86_64: `http://<next-server>/pxe/x86_64/<embed>_<driver>ipxe.efi`
- arm64: `http://<next-server>/pxe/arm64/<embed>_<driver>ipxe.efi`

No additional configuration is required beyond defining `pxe4` in the network's `services` block. EFI and HTTP boot clients on the same subnet are handled correctly — these settings exclude HTTP boot clients from the EFI class so each client type receives the appropriate file.

For hosts that need a fully custom boot filename (e.g. a specific HTTP URL or an alternate ROM), use `hw_pxe_filename` in the host's hardware group variables. This takes precedence over all class-level and subnet-level settings.

#### Add global options

It is possible to include as many global settings as desired using the `dhcp_server_global_settings` list.

For example:

```yaml
dhcp_server_global_settings:
  - ping-check false
```

Note: do not include the `;` at the end, it is automatically added by these settings.

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

Note: do not include the `;` at the end, it is automatically added by these settings.

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

#### Add dhcp host specific parameters and options

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
        network: net-1
```

#### Hosts equipment profile level iPXE rom

By default, all hosts will use global `dhcp_server_ipxe_driver` and `dhcp_server_ipxe_embed`
settings.

However, note that these settings will read `hw_ipxe_driver` and `hw_ipxe_embed` equipment profile variables, and precedence global settings for hosts that have these values set.

Also, if user whish to use a custom rom, it is possible to define `hw_pxe_filename` which precedence everything for the target hosts. This can be a relative path for tftp protocol (ex: `x86_64/myrom.efi`) or an http path for HTTP protocol (ex: `http://10.10.0.1/x86_64/myrom.efi`).

This allows for example to have an heterogenous cluster, with a group of hosts booting on *snponly* driver, while others boot on *default* one.
