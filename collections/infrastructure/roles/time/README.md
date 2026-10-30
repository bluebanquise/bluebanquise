# Time server

## Description

These settings provide a time server/client based on Chrony.
## Instructions

### Server or client

Set `time_profile` to `server` or `client` at invocation:

```yaml
- role: bluebanquise.infrastructure.time
  vars:
    time_profile: server   # or: client
```

### Network configuration

These settings read NTP server endpoints from the `ntp4` (or legacy `ntp`) key under `services` in the management network definition:

```yaml
networks:
  net-admin:
    subnet: 10.10.0.0
    prefix: 16
    services:
      ntp4:
        - hostname: mgt1
          ip4: 10.10.0.1
```

Or using the all-in-one shorthand:

```yaml
networks:
  net-admin:
    subnet: 10.10.0.0
    prefix: 16
    services_ip: 10.10.0.1
```

`services:ntp4` takes precedence over `services_ip` when both are defined.

### Manual tests

In case of a need, to force time synchronization on client side, use:

```
chronyc -a makestep
```

In case you need to test the server without using local configuration, use:

```
chronyd -q 'server my_ntp_server_hostname_or_ip iburst'
```

### Time zone

By default, this will use the `time_time_zone` or `bb_time_zone` variables to get time zone to be 
set on the target system. Default is `Europe/Brussels`. Please set this value according
to your cluster localization.

Note that variable `time_time_zone` will precedence global variable `bb_time_zone` if set.

### External time servers and pools

It is possible to configure external time sources for clients or servers
using dedicated variables:

```yaml
time_external_pools:
  - pool.ntp.org
time_external_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org
```

**pools** and **servers** are mutually exclusive. If you define both, these settings
will default to **pools** to write the Chrony configuration.

Note that by defining these external resources, this will not add binding to local servers.

It is possible to not install any time server but
simply bind clients to an external pool/server using this method.

### Allowed networks

By default, these settings will scan target host inventory network_interfaces list, and allow access to all networks connected to the host.

It is possible to allow more networks by using the `time_additional_networks_allowed` list. Allowed networks must be provided as `subnet/prefix` format:

```yaml
time_additional_networks_allowed:
  - 10.10.0.0/16
  - 172.16.1.0/24
```

### chronyd options

`time_chronyd_options` sets chronyd launch options, in `/etc/sysconfig/chronyd` (`OPTIONS`) on RHEL and Suse, or
`/etc/default/chrony` (`DAEMON_OPTS`) on Debian and Ubuntu. For example, to enable chronyd seccomp filter:

```yaml
time_chronyd_options: "-F 2"
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `time_profile` | (required) | `server` or `client`. |
| `time_external_pools` | `[]` | External pools to use instead of internal servers. |
| `time_external_servers` | `[]` | External servers to use instead of internal servers (if no pool). |
| `time_additional_networks_allowed` | `[]` | Additional networks allowed to query the server (`subnet/prefix`). |
| `time_time_zone` | `bb_time_zone`, else `Europe/Brussels` | Time zone. |
| `time_chronyd_options` | not set | chronyd launch options. |
| `time_chrony_custom_conf_path` | not set | Override chrony configuration file path. |
| `time_firewall_services_to_add` | `[ntp]` | Firewall services to open. |
| `time_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone. |
| `time_enable_services` | `bb_enable_services`, else `true` | Enable chrony service. |
| `time_start_services` | `bb_start_services`, else `true` | Start chrony service, and restart it on configuration changes. |

