# Interconnect

## Description

These settings install and starts all needed drivers for interconnect networks (InfiniBand/OFED, etc.).

These settings cover client (driver, libs) and subnet manager installation when needed.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

To trigger an interconnect setup, set `interconnect_stack` to the desired stack:

```yaml
interconnect_stack: ofed
```

Currently supported interconnect stacks:

* `ofed`

### OFED

#### Client setup

Set `interconnect_ofed_client: true` to install the InfiniBand client driver and libraries (RHEL package group `@Infiniband Support`, `rdma-core` and tools on other distributions). The `rdma-ndd` daemon, which publishes the host name as InfiniBand node description, is started automatically by udev when an RDMA device is present.

By default, these settings set memlock soft and hard rlimits to unlimited via pam_limits. Override with:

```yaml
interconnect_ofed_memlock_soft: 'unlimited'
interconnect_ofed_memlock_hard: 'unlimited'
```

#### Subnet manager setup

When InfiniBand switches are unmanaged, a subnet manager daemon must be deployed on at least one host. Multiple daemons can be deployed in a failover configuration.

Set `interconnect_ofed_subnet_manager: true` to install and configure OpenSM:

```yaml
interconnect_ofed_subnet_manager: true
```

Optionally set a priority level (range `0`-`15`, default `0`) for failover. When multiple managers share the same priority, the active one is elected by InfiniBand GUID:

```yaml
interconnect_ofed_subnet_manager_priority: 8
```

By default, OpenSM runs on the distribution default ports: the first port on RHEL and Suse, all ports on
Debian and Ubuntu. To select ports, list their port GUIDs (as displayed by `ibstat -p`):

```yaml
interconnect_ofed_subnet_manager_guids:
  - 0x0002c9030002fce9
```

Settings are written in each distribution native files, and OpenSM is restarted when they change:

* RHEL and Suse: `PRIORITY` and `GUIDS` in `/etc/sysconfig/opensm`.
* Debian and Ubuntu: `sm_priority` in `/etc/opensm/opensm.conf`, `PORTS` in `/etc/default/opensm`.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `interconnect_stack` | not set | Interconnect stack to deploy: `ofed`. Nothing is done if not set. |
| `interconnect_ofed_client` | `false` | Install InfiniBand client packages and set memlock limits. |
| `interconnect_ofed_memlock_soft` | `unlimited` | Soft memlock limit of all users. |
| `interconnect_ofed_memlock_hard` | `unlimited` | Hard memlock limit of all users. |
| `interconnect_ofed_subnet_manager` | `false` | Install and start OpenSM subnet manager. |
| `interconnect_ofed_subnet_manager_priority` | `0` | OpenSM priority, from 0 to 15. |
| `interconnect_ofed_subnet_manager_guids` | `[]` | Port GUIDs to run OpenSM on. Empty: distribution default. |
| `interconnect_enable_services` | `bb_enable_services`, else `true` | Enable OpenSM service. |
| `interconnect_start_services` | `bb_start_services`, else `true` | Start OpenSM service, and restart it on settings changes. |
