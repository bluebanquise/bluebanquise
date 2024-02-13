# Time server

## Description

This role provides a time server/client based on Chrony.

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 1 (Networks)
* Section 2 (Hosts definition)

## Instructions

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

By default, role will use the `time_time_zone` variable to get time zone to be 
set on the target system. Default is `Europe/Brussels`. Please set this value according
to your cluster localization.

Note that stack global `bb_time_zone` will precedence `time_time_zone` if set.

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

**pools** and **servers** are mutually exclusive. If you define both, the role
will default to **pools** to write the Chrony configuration.

Not that by defining these external resources, role will not add binding to local servers.

It is possible to not install any time server but
simply bind clients to an external pool/server using this method.

### Allowed networks

By default, the role will scan target host inventory network_interfaces list, and allow access to all networks connected to the host.

It is possible to allow more networks by using the `time_additional_networks_allowed` list. Allowed networks must be provided as `subnet/prefix` format:

```yaml
time_additional_networks_allowed:
  - 10.10.0.0/16
  - 172.16.1.0/24
```

### Icebergs

This role will react differently if in BlueBanquise stack multi icebergs mode or not.

By default, in non multiple icebergs, server will be the time source reference.
If using multiple icebergs hierarchy, then server can be a time reference if at
top of the icebergs hierarchy, or simply a time relay with an higher stratum,
if not a top server. This stratum calculation is done using **iceberg_level**
variable.

## Changelog

* 1.4.0: Allow services and services_ip together. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.2: Fix services entries. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Rename systemd service to chrony for Ubuntu. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.3.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Add custom configuration path. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Set sysconfig OPTIONS for chronyd. Bruno Travouillon <devel@travouillon.fr>
* 1.0.4: Add iburst to allow faster boot time recovery, update macro. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
