# Firewall

## Description

This role configures the firewall service on the hosts.

For each network interface of the host where the play runs, this role binds the
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
configuration by adding services to the default zone (public). For each role,
it is possible to override the default zone by setting
**${rolename}_firewall_zone** in the inventory.

For example, if you want to add the services of the pxe_stack roles to the
internal zone, you must set the variable `pxe_stack_firewall_zone: internal`.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.3.5: Allow usage on all distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.4: Fix condition in handler. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.3: Adapt to os hw split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.2: Fix issue with non networked nic. From @GaelBil. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Firewalld: enforce interfaces to their relevant zone. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.3.0: Add firewalld_allow_zone_drifting variable. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.3: Add OpenSuSE support. Neil Munday <neil@mundayweb.com>
* 1.1.2: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Allow creation of new zones. Bruno Travouillon <devel@travouillon.fr>
* 1.0.0: Role creation. Bruno Travouillon <devel@travouillon.fr>
