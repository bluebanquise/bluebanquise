# Interconnect

## Description

This role install and start all needed drivers for interconnects networks (Mellanox, etc.).

The role covers client (driver, libs) and subnet manager installation when needed.

Role currently only supports RHEL distributions. If you need other distributions, please notify me via a feature request.

## Instructions

To trigger an interconnect setup, simply set `interconnect_stack` variable to the
desired stack to be deployed.
Currently supported interconnect stacks are:

* ofed

### OFED

#### Client setup

To install client driver and libs, set `interconnect_ofed_client` to `true` at role invocation vars.



By default, role will set memlock soft and hard rlimits to unlimited, via pam module.

It is possible to define other values than unlimited by setting the following variables:

```yaml
interconnect_ofed_memlock_soft: 'unlimited'
interconnect_ofed_memlock_hard: 'unlimited'
```

#### Manager setup
When the Infiniband switches are unmanaged, a manager daemon must be deployed. Moreover several manager daemons can optionaly be deployed in a failover configuration (only one must be active).
 
To install subnet manager daemon, set `interconnect_ofed_subnet_manager` to `true` at role
invocation vars or in the description of the node (where this daemon should run) in the inventory.

Optionnally add a priority level (default: 0, maximum value: 15) if a failover setup is required. If several manager daemons are configured with the same priority,  the active service will be elected based on the GUID of the infiniband interface.
```
interconnect_ofed_subnet_manager: true
interconnect_ofed_subnet_manager_priority: 8
```

## To be done

Need to add support for Ubuntu and OpenSuse if exist.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.2.3: Improve openSM deployment <Patrick.Begou@free.fr>
* 1.2.2: Fix bad variables names. Reported by @corentin-g. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.1: Replace package list by a group. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Merge ofed and ofed_sm roles. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add tunables to set soft/hard memlock limits.
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
