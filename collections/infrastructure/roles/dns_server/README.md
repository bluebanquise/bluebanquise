# DNS server

## Description

These settings provide a DNS server based on BIND (`bind` on RedHat/Suse, `bind9` on Debian/Ubuntu).

These settings generate the following files (paths vary by distribution):

* Main configuration file (`named.conf`) - includes listen addresses and options
* Options file (`named.conf.options`) - listens on all DNS service IPs of the cluster's networks
* Local zones file (`named.conf.local`) - declares forward and reverse zones
* Forward zone file (`forward.zone` + `forward.soa`) - A records for all hosts
* Reverse zone file (`<prefix>.rr.zone` + `<prefix>.rr.soa`) - PTR records, one file per IP prefix

## Instructions

### Domain name

By default, the domain name used is `cluster.local`.

If the global variable `bb_domain_name` is set, that value is used instead.

You can override both by setting `dns_server_domain_name`:

```yaml
dns_server_domain_name: foobar.local
```

`dns_server_domain_name` takes precedence over the global variable `bb_domain_name`.

### Networks

These settings automatically includes all `net-*` networks from the Ansible inventory whose `dns_server` key is set to `true` (or not set, since `true` is the default):

```yaml
networks:
  net-1:
    subnet: 10.11.0.0
    prefix: 16
    dns_server: true  # optional, true by default
    services:
      dns4:
        - ip4: 10.11.0.1
          hostname: mgt1
```

These settings listen on all IPs defined under `dns4` in services, and allows queries from the whole subnet/prefix.

> **Note:** Unlike other services, the DNS service ignores the `hostname` field under `dns4` and always uses `ip4` directly.

You can also manually add listen addresses and allowed query ranges:

```yaml
dns_server_listen_on_ip4:
  - 10.21.1.3
dns_server_allow_query:
  - 10.21.1.0/24
```

This is useful for interfaces that are manually managed and not in the Ansible inventory.

### Hosts

These settings scan all hosts in the Ansible inventory and generates DNS records based on their `network_interfaces` list.

For example:

```yaml
all:
  hosts:
    node001:
      network_interfaces:
        - interface: eth1
          ip4: 10.10.3.1
          mac: 08:00:27:0d:44:90
          network: net-admin
        - interface: ib0
          ip4: 10.20.3.1
          network: interconnect
          type: infiniband
```

Generates the following forward records:

* `node001` → 10.10.3.1  (main identity, first interface)
* `node001-net-admin` → 10.10.3.1  (extended name)
* `node001-interconnect` → 10.20.3.1  (extended name)

These settings also supports aliases. Multiple aliases can be defined as a list:

```yaml
all:
  hosts:
    node001:
      alias:
        - foo
        - bar
      network_interfaces:
        - interface: eth1
          ip4: 10.10.3.1
          network: net-admin
```

Produces:

* `node001` → 10.10.3.1
* `foo` → 10.10.3.1
* `bar` → 10.10.3.1
* `node001-net-admin` → 10.10.3.1

### Forwarding and recursion

To integrate this DNS server into an existing IT infrastructure, set `dns_server_forwarders`:

```yaml
dns_server_forwarders:
  - 8.8.8.8
  - 8.8.4.4
```

Enable recursion:

```yaml
dns_server_recursion: yes
```

Enable `forward only` (queries not answered locally are forwarded and never resolved recursively):

```yaml
dns_server_forward_only: true
```

## Advanced usage

### Extended naming

Control whether `hostname-network` extended records are generated using `dns_server_enable_extended_names` (default: `true`).

With `dns_server_enable_extended_names: false`, only the base hostname and alias records are written - no `hostname-network` entries.

### Forward-only domains

Forward specific domains to an upstream resolver:

```yaml
dns_server_forward_only_domains:
  - domain: storage_cluster1.local
    forwarder_ip: 10.10.5.10
```

### Override zone

Override DNS responses for specific names using BIND's `response-policy` feature:

```yaml
dns_server_overrides:
  0.uk.pool.ntp.org: 10.11.0.1
```

DNS lookups for `0.uk.pool.ntp.org` will return `10.11.0.1`.

### Wildcard records

Add wildcard DNS records at the end of the forward zone:

```yaml
dns_server_wildcard_records:
  - hostname: "*.foo.bar"
    ip4: 10.10.70.201
```

### Raw content

Append raw content to `named.conf`:

```yaml
dns_server_raw_content: |
  zone "localhost" {
    type primary;
    file "master/localhost-forward.db";
    notify no;
  };
```

Append raw content to the options block:

```yaml
dns_server_raw_options_content: |
  also-notify port 5353;
```
