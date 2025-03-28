# DNS server

## Description

This role provides a dns server based on bind.

## Basic instructions

The role will generate 5 files (path may vary depending of Linux distribution):

* `/etc/named.conf` (or `/etc/bind/named.conf.options`) that contains main configuration, and that will try to bind to all networks defined on the host it is deployed on, using **services_ip.dns_ip** variable ip of the network.
* `/var/named/forward` that contains forward resolution of hosts
* `/var/named/forward.soa` included by /var/named/forward
* `/var/named/reverse` that contains reverse resolution of hosts
* `/var/named/reverse.soa` included by /var/named/reverse

### Domain name

By default, domain name used is `cluster.local`.

If global variable `bb_domain_name` is set then this value is used.

It is possible to update domaine name used by setting `dns_server_domain_name` value:

```yaml
dns_server_domain_name: foobar.local
```

Note that `dns_server_domain_name` precedence `bb_domain_name` global variable.

### Networks

This DNS role will automatically add networks of the cluster defined in the Ansible inventory,
assuming their variable **dns_server** is set to true (or not set, since true is the default value):

```yaml
networks:
  ice1-1:
    subnet: 10.11.0.0
    prefix: 16
    netmask: 255.255.0.0
    broadcast: 10.11.255.255
    dhcp_server: true
    dns_server: true  # <<<<<<<<<<
    services:
      dns:
        - ip4: 10.11.0.1
          hostname: mgt1-dns
```

The role will listen on any ip4 defined under dns key in services, and allow queries on the whole related subnet/prefix:

```yaml
networks:
  ice1-1:
    subnet: 10.11.0.0
    prefix: 16
    netmask: 255.255.0.0
    broadcast: 10.11.255.255
    dhcp_server: true
    dns_server: true
    services:
      dns:
        - ip4: 10.11.0.1  # <<<<<<<<<<
          hostname: mgt1-dns
```

Note that you can add manually listen ip and queries allowed ranges using respectively `dns_server_listen_on_ip4` and `dns_server_allow_query` lists.
For example:

```yaml
dns_server_listen_on_ip4:
  - 10.21.1.3
dns_server_allow_query:
  - 10.21.1.0/24
```

This can be useful if an interface is manually managed and not present in the Ansible inventory.

### Nodes

The role will scan all hosts defined in the Ansible inventory, and by default will add an entry for the node main network as direct record, and another record for each logical network node is connected to.

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
        - interface: eth0
          skip: true
        - interface: ib0
          ip4: 10.20.3.1
          network: interconnect
          type: infiniband
```

Will generate the following forward records:

* node001 -> 10.10.3.1
* node001-net-admin -> 10.10.3.1
* node001-interconnect -> 10.20.3.1

The role also supports alias and will generate a forward record on them too.

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
          mac: 08:00:27:0d:44:90
          network: net-admin
        - interface: eth0
          skip: true
        - interface: ib0
          ip4: 10.20.3.1
          network: interconnect
          type: infiniband
```

* node001 -> 10.10.3.1
* node001-net-admin -> 10.10.3.1
* node001-interconnect -> 10.20.3.1
* foo -> 10.10.3.1
* bar -> 10.10.3.1

### Forward and recursion

To configure forwarding and integrate this dns server into an existing IT
configuration, set variable `dns_server_forwarders` as a list of target forwarders.

```yaml
dns_server_forwarders:
  - 8.8.8.8
  - 8.8.4.4
```

You can enable recursion with the forwarders configuration using the following variable:
```yaml
dns_server_recursion: yes
```

## Advanced usage

### Override zone

To optionally override the IP addresses returned by certain host (`response-policy` bind parameter) you can define `dns_server_overrides` variable, like the following content for example:

```yaml
dns_server_overrides:
  0.uk.pool.ntp.org: 10.11.0.1
```

In this example, DNS look-ups for *0.uk.pool.ntp.org* will return *10.11.0.1*.

This will cause `/var/named/override` to be generated.

### Extended naming

User can enable or disable extended naming using the `dns_server_enable_extended_names` variable.
Default is `true`.

For example, for an host defined this way:

```yaml
c001:
  alias:
    - foobar
  network_interfaces:
    - name: eth0
      ip4: 10.10.3.1
      network: net-admin
    - name: eth1
      ip4: 10.20.3.1
      network: para
      alias: fuuuuu
```

If `dns_server_enable_extended_names: true`, then the following content will be written by default into forward zone:

```
c001 IN A 10.10.3.1
foobar IN A 10.10.3.1
c001-net-admin IN A 10.10.3.1
c001-para IN IN A 10.20.3.1
fuuuuu IN A 10.20.3.1
```

While if `dns_server_enable_extended_names: false`, then the following content will be written into forward zone:

```
c001 IN A 10.10.3.1
foobar IN A 10.10.3.1
```

### Forward only domains

You can set forward only on domains using the `dns_server_forward_only_domains` list:

```yaml
dns_server_forward_only_domains:
  - domain: storage_cluster1.local
    forwarder_ip: 10.10.5.10
```

### DNSSEC

Available options:

 * dns_server_dnssec_enable           # Allows connection to dnssec enabled servers. Default true.
 * dns_server_dnssec_sign             # Generate keys and sign zones. Default false.
 * dns_server_dnssec_overwrite_key    # Overwrite all existing keys. Default false.


To verify that DNSSEC is being used, use the dig command.
For example, to check that the DNSSEC signature is attached to the record:

```sh
dig mngt0-1.cluster.local +dnssec  @10.10.0.1
```

Where 10.10.0.1 is the DNS server, and "mngt0-1.smc.local" is the FQDN of a node. The output should contain "RRSIG" in the "ANSWER SECTION" field.
To check the Zone-signing-key and Key-signing-key, use the following command:

```sh
dig DNSKEY cluster.local @10.10.0.1
```

The output should contain "DNSKEY  256" (Zone-signing-key) and "DNSKEY 257" (Key-signing-key) in the "ANSWER SECTION" field.

### Raw content

You can add additional raw content to named.conf file using the `dns_server_raw_content` key:

```yaml
dns_server_raw_content: |
  zone "localhost" {
    type primary;
    file "master/localhost-forward.db";
    notify no;
  };
```

If your content have to be added to options, uses the

```yaml
dns_server_raw_options_content: |
  also-notify port 5353;
```

### DNS Round Robin

For load balancing with multiple DNS server nodes, the variable `dns_alias` can be added in the network interface section of each node in the inventory.
These entries will be skipped by roles like `hosts_file`. Ex:

```yaml
fn_management:
  hosts:
    mgt1
	  network_interfaces:
        - interface: eth0
          ip4: 10.0.0.10
          network: ice1-1
          dns_alias:
            - www
    mgt2
	  network_interfaces:
        - interface: eth0
          ip4: 10.0.0.20
          network: ice1-1
          dns_alias:
            - www
```

This will create a `foward.zone` file with:

```yaml
  www IN A 10.0.0.10
  www IN A 10.0.0.20
```

## Changelog

* 1.12.0: Added alias for round robin load balance. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.11.0: Enable dnssec at dns server. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.10.4: Increase role performances bby caching first octets. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.10.3: Fix global logic. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.10.2: Fix role for Ubuntu and Debian distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.10.1: Fix extended names for all zones. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.10.0: Add forward only domains. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.0: Allow services and services_ip together. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.8.1: Fix typo on domain name variable. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.8.0: Add capability to disable extended names, and ensure direct name comes first. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.7.4: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.7.3: Add missing services records. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.7.2: Rename systemd service to named for Ubuntu. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.7.1: Find correct default resolution network in reverse zone. Alexandra Darrieutort <alexandra.darrieutort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
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
