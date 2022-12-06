# DNS server

## Description

This role provides a dns server based on bind.

## Instructions

This DNS role will automatically add all networks of the cluster, assuming their
variable **dns_server** is set to true:

```yaml
networks:
  ice1-1:
    subnet: 10.11.0.0
    prefix: 16
    netmask: 255.255.0.0
    broadcast: 10.11.255.255
    is_in_dhcp: true
    dns_server: true  <<<<<<<<<<
    services_ip:
      dns_ip: 10.11.0.1
```

It will generate 5 files:

* `/etc/named.conf` that contains main configuration, and that will try to bind to all networks defined on the host it is deployed on, using **services_ip.dns_ip** variable ip of the network.
* `/var/named/forward` that contains forward resolution of hosts
* `/var/named/forward.soa` included by /var/named/forward
* `/var/named/reverse` that contains reverse resolution of hosts
* `/var/named/reverse.soa` included by /var/named/reverse

To configure forwarding and integrate this dns server into an existing IT
configuration, set variable `dns_server_forwarders` as a list of target forwarders.

```yaml
dns_server_forwarders:
  - 8.8.8.8
```

To optionally override the IP addresses returned by certain host you can define `dns_server_overrides` variable, like the following content for example:

```yaml
dns_overrides:
  0.uk.pool.ntp.org: 10.11.0.1
```

In this example, DNS look-ups for *0.uk.pool.ntp.org* will return *10.11.0.1*.

This will cause `/var/named/override` to be generated.

## Changelog

* 1.7.0: Add optional alias to every interface. Matthieu Isoard <indigoping4cgmi@gmail.com>
* 1.6.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.3: Bug fix for issue #724. Neil Munday <neil@mundayweb.com>
* 1.5.2: Bug fix for bond interfaces with no network defined.
* 1.5.1: Add recursion management. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.1: Bug fix for issue #682. Neil Munday <neil@mundayweb.com>
* 1.4.0: Re-worked role to work with Suse as well as existing distributions. Neil Munday <neil@mundayweb.com>
* 1.3.3: Add missing vital parameters to allow binding to external DNS servers. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.2: Re-worked reverse zone generation to fix issue #614. Neil Munday <neil@mundayweb.com>
* 1.3.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Change role to use new layout and override feature for issue #608. Neil Munday <neil@mundayweb.com>
* 1.2.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Improve role performances. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Added SOA. Bruno Travouillon <devel@travouillon.fr>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
