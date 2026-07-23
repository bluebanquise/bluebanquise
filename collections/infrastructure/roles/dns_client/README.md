# DNS client

## Description

These settings provide a basic `/etc/resolv.conf` file.

Please note that on most recent distributions, you should avoid editing this file (and so using these settings) and rely on the network daemon (NetworkManager or systemd-networkd).

## Instructions

`server` values are automatically set. By default, this will use current host network_interfaces list, and look for any dns server associated in the networks definition.

`search` value is defined by `dns_client_domain_name` or `bb_domain_name`. If none is set, default is `cluster.local`.
Note that `dns_client_domain_name` takes precedence over the global variable `bb_domain_name`.

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
Note that external DNS servers are placed after the cluster-internal DNS in resolution order.
