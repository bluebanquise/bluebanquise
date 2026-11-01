# DHCP server

## Description

This role provides a DHCP server, based on ISC Kea, combined with the iPXE roms of BlueBanquise.
It should be enough for most networks.

## Instructions

### Basic usage

The role serves all management networks (`net-*`) having a `subnet` and a `prefix`. To exclude a network from the DHCP server, set `dhcp_server: false` in the network configuration.

Each host interface (and BMC) connected to a served network gets a reservation of its `ip4`, using its `mac` address (see below for other identifiers). Interfaces without `ip4` are ignored.

The role uses `dhcp_unknown_range` if defined in the network configuration. It defines the range of IP addresses dynamically allocated to unregistered hosts, which is useful for temporary connections (laptops, etc.) or to detect hardware missing from the inventory.

By default, the role uses as much of the defined network settings as available.

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
    services_ip: 10.11.0.1                           # All services running on 10.11.0.1
```

Example of network configuration, full DHCP server with explicit per-service addresses:

```yaml
networks:
  net-1:
    subnet: 10.11.0.0
    prefix: 16
    dhcp_unknown_range: 10.11.254.1 - 10.11.254.254    # Optional
    gateway4: 10.11.2.1                              # Optional
    services:
      dns4:                                          # Optional
        - ip4: 10.11.0.1
        - ip4: 10.11.0.2
      ntp4:                                          # Optional
        - ip4: 10.11.0.1
      pxe4:                                          # Optional, required for PXE and HTTP boot
        - ip4: 10.11.0.1
          hostname: mg1
```

Notes:

* If both `services` and `services_ip` are set, `services` takes precedence over `services_ip`, service per service.
* Service keys without the `4` suffix (`dns`, `ntp`, `pxe`) are also accepted, but `dns4`, `ntp4` and `pxe4` are preferred.
* DHCP options only accept IP addresses: the `ip4` of each service entry is used, entries with only a `hostname` are ignored.
* `gateway4` can be a single IP address, or a list of entries with an `ip4` key. The deprecated `gateway` key is also accepted.

Clients receive as domain search list `dhcp_server_domain_name`, else the global `bb_domain_name`, else `cluster.local`.

Consider increasing the default lease times once your network is production ready.

The generated configuration is checked with `kea-dhcp4 -t` before being installed: an invalid configuration makes the role fail, and the DHCP server keeps running with its previous configuration.

### PXE and HTTP boot

When `pxe4` (or `services_ip`) is defined for a network, the role sends to booting hosts of this network the iPXE rom to load, depending on their architecture:

* Legacy BIOS PXE: `x86_64/dhcpretry_undionly.kpxe` (TFTP)
* x86_64 UEFI PXE: `x86_64/dhcpretry_snponly_ipxe.efi` (TFTP)
* arm64 UEFI PXE: `arm64/dhcpretry_snponly_ipxe.efi` (TFTP)
* x86_64 UEFI HTTP boot: `http://<pxe4 ip>/pxe/x86_64/dhcpretry_snponly_ipxe.efi`
* arm64 UEFI HTTP boot: `http://<pxe4 ip>/pxe/arm64/dhcpretry_snponly_ipxe.efi`

UEFI HTTP boot clients are identified by `HTTPClient` in their vendor class (option 60) and their architecture (option 93, `0x0010` for x86_64 and `0x0013` for arm64). Their URL uses the PXE server of their own network.

File names above use default settings. They are set for all hosts using:

* `dhcp_server_ipxe_driver`: `snponly` (default), `snp`, or any other value for the iPXE default drivers (no driver part in the file name, like `dhcpretry_ipxe.efi`).
* `dhcp_server_ipxe_embed`: `dhcpretry` (default), `noshell`, `allretry`, or any other value for the standard embedded script (`standard_snponly_ipxe.efi`).

### Client identifier matching

By default, the role makes Kea identify clients leases by their MAC address only, ignoring their DHCP client identifier (option 61).

This is needed for PXE deployments, as firmware/iPXE and the operating system send different client identifiers for the same network interface. For example iPXE sends a `01:<mac>` client identifier, while dracut/NetworkManager on recent distributions (RHEL 10, Ubuntu 26.04, etc.) send an RFC 4361 identifier (IAID and DUID).
If Kea tracks leases by client identifier, it considers them as two different clients: the lease obtained by iPXE conflicts with the reservation requested by the installer, and the installer fails to get an IP address (`ALLOC_ENGINE_V4_DISCOVER_ADDRESS_CONFLICT` in Kea logs).

To make Kea track leases using client identifiers (Kea default behavior), set `dhcp_server_match_client_id` to `true`. It can also be set per network, using the `dhcp_match_client_id` network key, which takes precedence over the global setting. For example, DHCP over InfiniBand (IPoIB) requires client identifiers:

```yaml
networks:
  net-ib:
    subnet: 10.20.0.0
    prefix: 16
    dhcp_match_client_id: true
```

Note: this setting only changes how leases are tracked. Host reservations are always looked up using the identifier defined in the inventory (see below).

### Hosts identifiers

A reservation uses a single identifier, the first one defined on the host interface (or BMC):

* `mac`: MAC address (recommended).
* `dhcp_client_identifier`: DHCP client identifier (option 61).
* `host_identifier`: relay agent circuit id (option 82).

For example:

```yaml
hosts:
  c001:
    network_interfaces:
      - interface: eth0
        ip4: 10.10.3.1
        dhcp_client_identifier: 01:08:00:27:36:c0:ac
        network: net-1
```

### Shared networks

It is possible to combine networks into shared networks, when multiple subnets
are on the same physical network.
To do so, add the optional `shared_network` key in the network definition.

Networks of the same shared network must have the same `shared_network` value,
which is the name of this shared network.

For example, to add net-1 and net-2 into the same shared network, define them
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

### Logs

Kea logs go to the service output (journal). Set `dhcp_server_log_severity` to `DEBUG` to get detailed logs, for example to understand why a host does not get an address. Note that `DEBUG` is very verbose, and should not be kept in production.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `dhcp_server_lease_file` | `kea-leases4.csv` | Lease database file name, in `/var/lib/kea/`. |
| `dhcp_server_default_lease_time` | `600` | Default lease time, in seconds. |
| `dhcp_server_max_lease_time` | `7200` | Maximum lease time, in seconds. |
| `dhcp_server_ipxe_driver` | `snponly` | iPXE rom driver: `snponly`, `snp`, or default drivers. |
| `dhcp_server_ipxe_embed` | `dhcpretry` | iPXE rom embedded script: `dhcpretry`, `noshell`, `allretry`, or standard. |
| `dhcp_server_domain_name` | `bb_domain_name`, else `cluster.local` | Domain search list sent to clients. |
| `dhcp_server_listen_interfaces` | `["*"]` | Interfaces the DHCP server listens on. |
| `dhcp_server_match_client_id` | `false` | Track leases using client identifiers (option 61) instead of MAC addresses only. |
| `dhcp_server_log_severity` | `INFO` | Kea log severity: `FATAL`, `ERROR`, `WARN`, `INFO` or `DEBUG`. |
| `dhcp_server_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only register hosts of this Ansible group. |
| `dhcp_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewalld zone to open the DHCP service in. |
| `dhcp_server_firewall_services_to_add` | `["dhcp"]` | Firewalld services to open. |
| `dhcp_server_enable_services` | `bb_enable_services`, else `true` | Enable the DHCP server at boot. |
| `dhcp_server_start_services` | `bb_start_services`, else `true` | Start the DHCP server, and restart it on configuration change. |

Networks keys used by the role, in addition to the core ones of `resources/data_model.md`:

| Key | Description |
|-----|-------------|
| `dhcp_server` | Set to `false` to exclude the network from the DHCP server. |
| `dhcp_unknown_range` | Range of IP addresses dynamically allocated to unknown hosts (`first - last`). |
| `dhcp_match_client_id` | Override `dhcp_server_match_client_id` for this network. |
| `shared_network` | Name of the shared network this network belongs to. |
