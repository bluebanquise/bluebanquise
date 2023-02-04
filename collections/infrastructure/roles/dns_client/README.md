# DNS client

## Description

This role provides a basic `/etc/resolv.conf` file.

## Instructions

It is possible to add here external DNS servers for clients.

```yaml
dns_client_external_server:
  - 8.8.8.8
  - 8.8.4.4
```
Note that this/these external(s) dns will be placed after the cluster internal dns in resolution order.

Note also that on most recent distributions, editing `/etc/resolv.conf` file is not recommended, as the file will be managed by network daemon (NetworkManager, etc.).

## Changelog

* 1.2.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.4: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.3: Added support of multiple DNS servers. Bruno Travouillon <devel@travouillon.fr>
* 1.0.2: Added variable for role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
