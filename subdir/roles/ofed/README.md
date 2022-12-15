# OFED

## Description

This role install and start all needed for OFED based interconnects (Mellanox, etc.).

The role cover client (driver, libs) and subnet manager installation.

## Instructions

This role is currently only for CentOS/RHEL.

To install client part, set `ofed_client` to `true` at role invocation vars.

To install subnet manager part, set `ofed_subnet_manager` to `true` at role
invocation vars.

## To be done

Need to add support for Ubuntu and OpenSuse if exist.

## Changelog

* 1.2.1: Replace package list by a group. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Merge ofed and ofed_sm roles. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add tunables to set soft/hard memlock limits.
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
