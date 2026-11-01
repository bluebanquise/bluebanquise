# Hosts file

## Description

This role generates and deploys `/etc/hosts`, including hosts from the inventory, network services, and optional external entries.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

The role gathers all hosts from the inventory (or from the group set in `hosts_file_restrict_to_group`,
else `bb_restrict_to_group`) and adds them into `/etc/hosts`, using:

* The first interface of each host, with its name and its aliases (`alias` host key).
* The BMC of each host (`bmc` key), with its name and its aliases (`bmc.alias` key).
* The network services (`pxe4`, `dns4`, etc.) defined under each network.
* With extended names enabled (default), all interfaces of each host, named `<hostname>-<network>`, and the interfaces aliases (`alias` key of an interface).

Each name is written with its FQDN and its short name. The first line of an IP address is used for reverse
resolution, so the main name of a host is always written first.

### Domain name

FQDNs use `hosts_file_domain_name`, else `bb_domain_name`, else `cluster.local`.

### FQDN first

By default (`hosts_file_fqdn_first: true`), the FQDN is written before the short name. With glibc, the first
name of a line is the canonical name of the host: `hostname -f` returns the FQDN only in this case. Set
`hosts_file_fqdn_first: false` to write the short name first.

### Example

Given the following host (domain `bluebanquise.local`):

```yaml
c001:
  alias:
    - foobar
  bmc:
    name: bc001
    ip4: 10.10.103.1
    network: net-admin
    alias: c001-bmc
  network_interfaces:
    - interface: eth0
      ip4: 10.10.3.1
      network: net-admin
    - interface: eth1
      ip4: 10.20.3.1
      network: para
      alias: fuuuuu
```

With `hosts_file_enable_extended_names: true` (default):

```
10.10.3.1 c001.bluebanquise.local c001
10.10.3.1 foobar.bluebanquise.local foobar
10.10.103.1 bc001.bluebanquise.local bc001
10.10.103.1 c001-bmc.bluebanquise.local c001-bmc
10.10.3.1 c001-net-admin.bluebanquise.local c001-net-admin
10.20.3.1 c001-para.bluebanquise.local c001-para
10.20.3.1 fuuuuu.bluebanquise.local fuuuuu
```

With `hosts_file_enable_extended_names: false`, the last 3 lines (all interfaces and interfaces aliases) are not written.

### Network services

Services defined under `networks` are automatically added. For example, given:

```yaml
networks:
  net-admin:
    services:
      pxe4:
        - ip4: 10.10.0.1
          hostname: pxe
      dns4:
        - ip4: 10.10.0.1
          hostname: dns
```

The following entries are added:

```
10.10.0.1 pxe.bluebanquise.local pxe
10.10.0.1 dns.bluebanquise.local dns
```

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

External hosts are written as is, without domain name.

### Large clusters

With `bb_enable_flat_optimizations: true`, the hosts list is built and the file rendered only once, on the
Ansible host, then copied to all hosts. This scales to thousands of hosts. In this mode, the file is the
same for all hosts: role variables are read from the first host of the play only.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `hosts_file_domain_name` | `bb_domain_name`, else `cluster.local` | Domain name of hosts. |
| `hosts_file_fqdn_first` | `true` | Write FQDN before short name (canonical name). |
| `hosts_file_enable_extended_names` | `true` | Also write all interfaces (`<hostname>-<network>`) and interfaces aliases. |
| `hosts_file_external_hosts` | `{}` | Hosts not in the inventory. |
| `hosts_file_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only write hosts of this group. |
