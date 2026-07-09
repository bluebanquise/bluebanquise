# Firewall

## Description

These settings configure the firewall service on the hosts.

For each network interface of the host where the play runs, these settings bind the
source address **subnet/prefix** to the zone defined in **firewall.zone** if
the network must be in the firewall.

## Instructions

### Inventory configuration

Enable or disable the firewall service in the equipment profile:

```yaml
os_firewall: true
```

To add a network of the host to a zone, define the zone name in
**firewall.zone** in the network:

```yaml
networks:
  ice1-1:
    subnet: 10.10.0.0
    prefix: 16
    netmask: 255.255.0.0
    broadcast: 10.10.255.255
    gateway: 10.10.2.1
    firewall:
      zone: internal
  interconnect-1:
    subnet: 10.20.0.0
    prefix: 16
    firewall:
      zone: trusted
```

To add or delete custom services that are not handled by any other role, define
the `firewall_zones` parameter as below:

```yaml
firewall_zones:
  - zone: internal            <<< zone name
    services_enabled:         <<< list of service to enable
      - high-availability
      - prometheus
    services_disabled:        <<< list of service to disable
      - cockpit
```

It is possible to add or delete custom ports and rich rules with the same
parameter:

```yaml
firewall_zones:
  - zone: internal            <<< zone name
    ports_enabled:            <<< list of ports to enable
      - 1234/tcp
    ports_disabled:           <<< list of ports to disable
      - 5678/tcp
    rich_rules_enabled:       <<< list of rich rules to enable
      - "rule family=ipv4 forward-port port=443 protocol=tcp to-port=8443"
    rich_rules_disabled:      <<< list of rich rules to disable
      - 'rule service name="ftp" audit limit value="1/m" accept'
    icmp_block_inversion: yes
    masquerade: yes
```

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
