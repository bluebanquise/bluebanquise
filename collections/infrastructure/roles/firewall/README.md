# Firewall

## Description

This role configures the firewalld service on the hosts.

For each network interface of the host where the play runs, the role binds the
source address **subnet/prefix** of the interface network to the zone defined in
the network **firewall_zone** key.

## Instructions

### Inventory configuration

Enable or disable the firewall service in the operating system group (`true` if not set):

```yaml
os_firewall: true
```

To add a network of the host to a zone, define the zone name in
**firewall_zone** in the network:

```yaml
networks:
  net-admin:
    subnet: 10.10.0.0
    prefix: 16
    gateway4: 10.10.2.1
    firewall_zone: internal
  interconnect:
    subnet: 10.20.0.0
    prefix: 16
    firewall_zone: trusted
```

`firewall_zone` is optional: networks without it are not bound to any zone, and their traffic is handled by firewalld default zone (`public`, unless changed).

If the `firewall_zone` of a network changes, the role moves its subnet from the previous zone to the new one.

To add or delete custom services that are not handled by any other role, define
the `firewall_zones` parameter as below:

```yaml
firewall_zones:
  - zone: internal            # zone name
    services_enabled:         # list of services to enable
      - high-availability
      - prometheus
    services_disabled:        # list of services to disable
      - cockpit
```

It is possible to add or delete custom ports and rich rules with the same
parameter:

```yaml
firewall_zones:
  - zone: internal            # zone name
    ports_enabled:            # list of ports to enable
      - 1234/tcp
    ports_disabled:           # list of ports to disable
      - 5678/tcp
    rich_rules_enabled:       # list of rich rules to enable
      - "rule family=ipv4 forward-port port=443 protocol=tcp to-port=8443"
    rich_rules_disabled:      # list of rich rules to disable
      - 'rule service name="ftp" audit limit value="1/m" accept'
    icmp_blocks_enabled:      # list of ICMP types to block
      - echo-request
    icmp_blocks_disabled:     # list of ICMP types to unblock
      - echo-reply
    icmp_block_inversion: true
    masquerade: true
```

Since firewall configuration is often specific to a single host, `firewall_zones`
can be defined in a dedicated host variables file instead of a group variable.
Place the file at `host_vars/<hostname>/firewall.yml`, at the root of the inventory:

```
inventory/
├── cluster/
├── group_vars/
└── host_vars/
    └── mgt1/
        └── firewall.yml
```

For example, `host_vars/mgt1/firewall.yml`:

```yaml
firewall_zones:
  - zone: internal
    services_enabled:
      - high-availability
    ports_enabled:
      - 8443/tcp
```

This keeps host-specific firewall rules isolated from shared group variables
and makes them easy to audit per node.

To control whether firewalld allows zone drifting (packets being classified into
multiple zones), set `firewall_firewalld_allow_zone_drifting`. It defaults to
`false`, which is the recommended value for security:

```yaml
firewall_firewalld_allow_zone_drifting: false
```

### Firewalld policies (zone-to-zone forwarding)

Zone-level configuration (above) only governs traffic whose ingress **and** egress
interfaces are bound to the same zone. A host acting as a gateway - one interface
in one zone, a second interface in another - needs an explicit firewalld **policy**
to forward traffic between the two zones at all; without one, cross-zone forwarding
is denied unconditionally, silently (no error, packets are just dropped).

Define policies with `firewall_policies`:

```yaml
firewall_policies:
  - name: internal-to-external    # policy name
    ingress_zones:                # required: zone(s) traffic enters from
      - internal
    egress_zones:                 # required: zone(s) traffic leaves through
      - external
    target: ACCEPT                # CONTINUE (firewalld's own default), ACCEPT, DROP or REJECT
    masquerade: true              # NAT traffic that crosses this policy
    services_enabled:
      - dns
    services_disabled: []
    ports_enabled:
      - 7770/tcp
    ports_disabled: []
    rich_rules_enabled: []
    rich_rules_disabled: []
```

`name`, `ingress_zones` and `egress_zones` are required for every entry. Masquerade
must be declared **on the policy itself** (as above) to NAT traffic crossing zones -
setting `masquerade: true` on a zone (see above) only NATs traffic whose ingress and
egress interfaces are both in that same zone, it has no effect on policy-forwarded
traffic.

Leaving `target` unset keeps firewalld's own default, `CONTINUE`, which does not
forward anything on its own. For a working gateway, `target: ACCEPT` (or ports/
services/rich rules explicitly enabling the wanted traffic) is required.

### Integration with other roles

BlueBanquise ships with roles that already support some level of firewall
configuration by adding services to the default zone (public).

To change the default zone for all roles at once, set `bb_services_firewall_zone`:

```yaml
bb_services_firewall_zone: internal
```

For each role individually, override the default zone by setting
`<rolename>_firewall_zone` in the inventory. Role-level variables always take
precedence over `bb_services_firewall_zone`.

For example, to add the pxe_stack services to the internal zone:

```yaml
pxe_stack_firewall_zone: internal
```

### Configuration changes

Configuration changes are applied with a firewalld reload, which keeps established connections.
When the role creates a new zone, firewalld is reloaded immediately, so the zone can be configured in the same run.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `os_firewall` | `true` | Enable firewalld and configure it (global variable, usually set in OS groups). |
| `firewall_zones` | not set | Zones settings: services, ports, rich rules, ICMP blocks, masquerade. |
| `firewall_policies` | `[]` | Firewalld policies, for traffic forwarded between zones. |
| `firewall_firewalld_allow_zone_drifting` | `false` | Value of firewalld `AllowZoneDrifting` setting. |
| `firewall_start_services` | `bb_start_services`, else `true` | Reload firewalld on configuration change. |

Networks keys used by the role, in addition to the core ones of `resources/data_model.md`:

| Key | Description |
|-----|-------------|
| `firewall_zone` | Zone the network subnet is bound to. |
