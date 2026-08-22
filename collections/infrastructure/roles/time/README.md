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
