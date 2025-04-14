# DNS client

## Description

This role provides a basic `/etc/resolv.conf` file.

Please note that on most recent distributions, you should avoid editing this file (and so using this role) and rely on the network daemon (NetworkManager or systemd-networkd).

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

Note also that on most recent distributions, editing `/etc/resolv.conf` file is not recommended, as the file will be managed by network daemon (NetworkManager, etc.).

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

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
