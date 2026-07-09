# Interconnect

## Description

These settings install and starts all needed drivers for interconnect networks (InfiniBand/OFED, etc.).

These settings cover client (driver, libs) and subnet manager installation when needed.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

Note: Ubuntu, Debian, and OpenSuse package names in `vars/` files are best-effort and should be verified against the target distribution repositories before use.

## Instructions

To trigger an interconnect setup, set `interconnect_stack` to the desired stack:

```yaml
interconnect_stack: ofed
```

Currently supported interconnect stacks:

* `ofed`

### OFED

#### Client setup

Set `interconnect_ofed_client: true` to install the InfiniBand client driver and libraries (RHEL package group `@Infiniband Support`) and configure `rdma-ndd`.

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

These settings automatically detects the first active InfiniBand device and configures OpenSM to use its GUID.
