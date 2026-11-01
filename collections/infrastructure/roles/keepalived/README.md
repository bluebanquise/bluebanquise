# keepalived

## Description

This role deploys a basic keepalived configuration for use in high availability context, typically combined with the **haproxy** role.

Keepalived provides a floating IP address (virtual router) that can be used as a single reference point for clients. When the primary host fails, a backup host automatically takes over the virtual IP.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

For background on the concept: https://www.digitalocean.com/community/questions/navigating-high-availability-with-keepalived

## Instructions

Configuration is made via **vrrp_instances**. Each instance defines a group of hosts sharing the same floating virtual IPs with the same parameters.

Define instances under `keepalived_vrrp_instances`:

```yaml
keepalived_vrrp_instances:
  - name: VI_1           # Optional - auto-assigned if not set
    interface: enp0s3
    id: 101              # Optional - auto-assigned if not set (range 1-255)
    servers:
      - mg1              # First in list is MASTER with highest priority
      - mg2              # Subsequent entries are BACKUP, priority ordered by position
      - mg3
    auth_pass: "secret1"
    advert_int: 1        # Optional - advertisement interval in seconds, default 1
    virtual_ipaddress:
      - 10.10.0.3/16 brd 10.10.255.255 scope global
  - interface: enp0s8
    servers:
      - mg2
      - mg3
      - mg1
    auth_pass: "secret2"
    virtual_ipaddress:
      - 172.16.0.77/16 brd 172.16.255.255 scope global
```

All keys not marked Optional are mandatory.

Each host only gets the instances listing it in `servers`. The same `keepalived_vrrp_instances` list can
therefore be set for all hosts (for example in `group_vars/all`).

Note that keepalived only uses the first 8 characters of `auth_pass`.

### Priority

The first server in `servers` is `MASTER` with priority 100. Subsequent servers are `BACKUP` with decreasing
priorities based on their position: 88 for the second server, 87 for the third, etc.

### Virtual router ID

If `id` is not set, the role assigns IDs from the instance position in the list, starting from 78 (78, 79, 80, ...).
IDs must be unique per VRRP instance on the same network segment and must be in range 1-255.

### Firewall

The `vrrp` firewalld service (VRRP protocol, number 112) is allowed, so that backups receive the master
advertisements. Without it, all hosts would consider themselves master and hold the virtual IPs.

### Configuration changes

On configuration changes, keepalived is reloaded, without dropping the virtual IPs.

These settings provide a simple way to define keepalived VIPs. Load balancing is not managed by these settings - use the **haproxy** role for that.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `keepalived_vrrp_instances` | `[]` | VRRP instances, see above. |
| `keepalived_conf_file` | `/etc/keepalived/keepalived.conf` | Configuration file path. |
| `keepalived_firewall_services_to_add` | `[vrrp]` | Firewall services to open. |
| `keepalived_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open services in. |
| `keepalived_enable_services` | `bb_enable_services`, else `true` | Enable keepalived service. |
| `keepalived_start_services` | `bb_start_services`, else `true` | Start keepalived service, and reload it on configuration changes. |
