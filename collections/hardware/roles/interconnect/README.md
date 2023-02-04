# Interconnect

## Description

This role install and start all needed drivers for interconnects networks (Mellanox, etc.).

The role covers client (driver, libs) and subnet manager installation when needed.

## Instructions

To trigger an interconnect setup, simply set `interconnect_stack` variable to the
desired stack to be deployed.
Currently supported interconnect stacks are:

* ofed

### OFED

To install client driver and libs, set `interconnect_ofed_client` to `true` at role invocation vars.

To install subnet manager daemon, set `interconnect_ofed_subnet_manager` to `true` at role
invocation vars.

By default, role will set memlock soft and hard rlimits to unlimited, via pam module.

It is possible to define other values than unlimited by setting the following variables:

```yaml
interconnect_ofed_memlock_soft: 'unlimited'
interconnect_ofed_memlock_hard: 'unlimited'
```

## To be done

Need to add support for Ubuntu and OpenSuse if exist.

## Changelog

* 1.2.1: Replace package list by a group. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Merge ofed and ofed_sm roles. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add tunables to set soft/hard memlock limits.
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
