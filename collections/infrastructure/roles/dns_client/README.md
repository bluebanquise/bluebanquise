# DNS client

## Description

This role configures the DNS servers and the search domain used by the host.

On current distributions, `/etc/resolv.conf` is managed by a network tool, and any direct edit would be overwritten. The role therefore never edits `/etc/resolv.conf`, but configures the tools managing it, depending on which ones are installed on the host:

* **systemd-resolved** (Ubuntu, etc.): the role writes `/etc/systemd/resolved.conf.d/bluebanquise.conf` (`DNS=` and `Domains=`), then restarts systemd-resolved.
* **NetworkManager** (RedHat family, etc.): the role writes `/etc/NetworkManager/conf.d/90-bluebanquise-dns.conf`, using NetworkManager global DNS configuration, then reloads NetworkManager. Note that global DNS configuration overrides the DNS settings of all NetworkManager connections.

If both are installed, both are configured. If none is installed, the role displays a warning and configures nothing.

This role can be used with or without the `nic` role.

## Instructions

### DNS servers

DNS servers are, in this order:

1. `dns_client_servers` if set, else the DNS services of the host main network: `dns4` services (or `dns`, deprecated) of the network of the first host interface connected to a management network (`net-` prefix), else its `services_ip`.
2. Then `dns_client_external_servers`, if set.

For example, with the following network, the host uses `10.10.0.2` and `10.10.0.3`:

```yaml
networks:
  net-admin:
    subnet: 10.10.0.0
    prefix: 16
    services:
      dns4:
        - ip4: 10.10.0.2
          hostname: mg1-dns
        - ip4: 10.10.0.3
          hostname: mg2-dns
```

If no DNS server is found, no configuration is written.

### Search domain

The search domain is `dns_client_domain_name`, else the global `bb_domain_name`, else `cluster.local`.

### Force servers to use

It is possible to force DNS servers, instead of the ones of the host network:

```yaml
dns_client_servers:
  - 10.10.0.2
  - 10.10.0.3
```

### Add external servers

It is possible to add external DNS servers, placed after the cluster ones in resolution order:

```yaml
dns_client_external_servers:
  - 8.8.8.8
  - 8.8.4.4
```

### Upgrade from previous versions

Previous versions of this role wrote `/etc/resolv.conf` directly, or the `DNS=` line of `/etc/systemd/resolved.conf` on Ubuntu. This `DNS=` line is removed by the role, as servers are now set in the dedicated `/etc/systemd/resolved.conf.d/bluebanquise.conf` file.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_client_domain_name` | `bb_domain_name`, else `cluster.local` | Search domain. |
| `dns_client_servers` | `[]` | DNS servers to use, instead of the DNS services of the host network. |
| `dns_client_external_servers` | `[]` | DNS servers added after the cluster ones. |
| `dns_client_start_services` | `bb_start_services`, else `true` | Restart systemd-resolved / reload NetworkManager on configuration change. |
