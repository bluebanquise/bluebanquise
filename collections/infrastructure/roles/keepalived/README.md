# keepalived

## Description

This role deploy a basic keepalived configuration to be used in high availability context with for example HAproxy.

Keepalived provides a floating ip address (virtual router), which can be used as a single reference for clients.

An interesting article can be found here to understand the concept: https://www.digitalocean.com/community/questions/navigating-high-availability-with-keepalived

## Instructions

Configuration is made by **vrrp_instances**. Each instance can be seen as a group of nodes sharing the same group of floating virtual ips with the same parameters.

Instances are listed under the `keepalived_vrrp_instances` list the following way:

```yaml
keepalived_vrrp_instances:
  - name: VI_1 # Optional, is automatically attributed if not set
    interface: enp0s3
    id: 101 # Optional, is automatically attributed if not set
    servers:
      - mg1 # First in the list is considered MASTER, with top priority
      - mg2 # Then others are BACKUP, with pritority ordered as in this list (mg1 > mg2 > mg3)
      - mg3
    auth_pass: "<replace me>"
    advert_int: 1 # Optional, advert interval default to 1s if not set
    virtual_ipaddress:
      - 10.10.0.3/16 brd 10.10.255.255 scope global
  - interface: enp0s8
    servers:
      - mg2
      - mg3
      - mg1
    auth_pass: "<replace me>"
    virtual_ipaddress:
      - 172.16.0.77/16 brd 172.16.255.255 scope global
```

Comments should be self explanatory. Keys not optional are mandatory.

This role aims to provide a simple way to define keepalived VIP. Loadbalancing is currently not supported by the role.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
