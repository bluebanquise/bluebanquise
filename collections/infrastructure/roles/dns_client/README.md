# DNS client

## Description

This role provides a basic `/etc/resolv.conf` file.

Please note that on most recent distributions, this file is managed by the network daemon (NetworkManager or systemd-networkd).
If an external DHCP server is providing DNS information, then NetworkManager may use this information to overwrite `/etc/resolv.conf`.

Use this role if at least one of these conditions are true:

* The target node does not have an interface configured by an external DHCP server.
* The target node has `dns=none` set in its `/etc/NetworkManager/NetworkManager.conf` file.

If the node interfaces with dynamic IP addresses are managed by a controlled DHCP server (such as one deployed by the dhcp_server role), then this role may be omitted.

## Instructions

`server` values are automatically set. By default, role will use current node network_interfaces list, and look for any dns server associated in the networks definition.

`search` value is defined by `dns_client_domain_name` or `bb_domain_name`. If none is set, default is `cluster.local`.
Note that `dns_client_domain_name` precedence global variable `bb_domain_name`.

### Force servers to use

It is possible to force DNS servers by specifying:

```yaml
dns_client_servers:
  - 2.2.2.2
  - 2.2.3.3
```

### Add external servers

It is possible to add here external DNS servers for clients.

```yaml
dns_client_external_servers:
  - 8.8.8.8
  - 8.8.4.4
```
Note that this/these external(s) dns will be placed after the cluster internal dns in resolution order.

## Changelog

* 1.3.4: Fix variable default value. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.3.3: Fix variable typo. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.2: Fix global logic. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: be able to set dns servers using a new variable <jean-pascal.mazzilli@gmail.com>
* 1.3.0: Allow services and services_ip together. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.1: fix nameserver. Alexandra Darrieutort <alexandra.darrieutort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.4: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.3: Added support of multiple DNS servers. Bruno Travouillon <devel@travouillon.fr>
* 1.0.2: Added variable for role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
