# Hosts file

## Description

These settings generate and deploys `/etc/hosts`, including hosts from the inventory, network services, and optional external entries.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

These settings gather all hosts from the inventory and adds them, using all their known network interfaces, into `/etc/hosts`.

Network services defined under each network (e.g. `pxe4`, `dns4`) are also automatically included.

### Domain name

These settings use `hosts_file_domain_name` or `bb_domain_name` to build FQDNs. Default is `cluster.local`. `hosts_file_domain_name` takes precedence over `bb_domain_name` if both are set.

### External hosts

Additional hosts not in the inventory can be added via `hosts_file_external_hosts`:

```yaml
hosts_file_external_hosts:
  myhost: 10.10.10.10
  mysecondhost: 7.7.7.7
  mythirdhost:
    ip4: 10.10.10.33
    alias:
      - machine3
      - extmachine3
```

### Extended naming

Extended naming is controlled by `hosts_file_enable_extended_names` (default: `true`).

When enabled, each interface generates a `hostname-network` entry in addition to the base hostname entry. Given:

```yaml
c001:
  alias:
    - foobar
  network_interfaces:
    - interface: eth0
      ip4: 10.10.3.1
      network: net-admin
    - interface: eth1
      ip4: 10.20.3.1
      network: para
      alias: fuuuuu
```

With `hosts_file_enable_extended_names: true` (and domain `bluebanquise.local`):

```
10.10.3.1 c001 c001.bluebanquise.local foobar
10.10.3.1 c001-net-admin
10.20.3.1 c001-para fuuuuu
```

With `hosts_file_enable_extended_names: false`:

```
10.10.3.1 c001 c001.bluebanquise.local foobar
```

### Network services

Services defined under `networks` are automatically added to `/etc/hosts`. For example, given:

```yaml
networks:
  net-admin:
    services:
      pxe4:
        - ip4: 10.10.0.1
          hostname: pxe4
      dns4:
        - ip4: 10.10.0.1
          hostname: dns4
```

The following entries will be added:

```
10.10.0.1 pxe4
10.10.0.1 dns4
```

### Performance

These settings use `delegate_to: localhost` with `run_once: true` and `delegate_facts: true` to build the full host map once on the controller, then pushes the rendered file to all targets. This avoids per-host fact computation and scales to thousands of hosts.
