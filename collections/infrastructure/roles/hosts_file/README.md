# Hosts file

## Description

This role provides a basic /etc/hosts files.

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 1 (Networks)
* Section 2 (Hosts definition)

## Instructions

This role will gather all hosts from the inventory, and add them, using all
their known internal network connections, into */etc/hosts* file.

In case of multiple icebergs system, administrator can reduce the scope of this
gathering by setting `hosts_file_range`:

* **all** will use all Ansible inventory hosts
* **iceberg** will reduce the gathering to the current host iceberg

Default is **iceberg**.

```yaml
hosts_file_range: all
```

It is also possible to define external hosts to be added into hosts file.
To do so, define `hosts_file_external_hosts` this way:

```yaml
hosts_file_external_hosts:
  myhost: 10.10.10.10
  mysecondhost: 7.7.7.7
  mythirdhost:
    ip: 10.10.10.33
    alias:
      - machine3
      - extmachine3
```

This role is using either `bb_domain_name` or `hosts_file_domain_name` variable to set FQDN. Default is `cluster.local`.
Note that `hosts_file_domain_name` precedence the global variable `bb_domain_name` if set. 

## Advanced usage

### Extended naming

User can enable or disable extended naming using the `hosts_file_enable_extended_names` variable.
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

If `hosts_file_enable_extended_names: true`, then the following content will be written by default into `/etc/hosts` file (assuming here domain name set is `bluebanquise.local`):

```
10.10.0.3 c001 c001.bluebanquise.local foobar
10.10.3.1 c001-net-admin
10.20.3.1 c001-para fuuuuu
```

While if `hosts_file_enable_extended_names: false`, then the following content will be written into `/etc/hosts` file:

```
10.10.0.3 c001 c001.bluebanquise.local foobar
```

## Changelog

* 1.5.2: Fix global logic. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.1: Fix typo on domain name variable. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.0: Add capability to disable extended names, and ensure direct name comes first. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.1: Improve code. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.0: Use bb_nodes cache. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.2: Add missing services entries. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Update to BB 2.0 format. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.3.0: Add optional alias to every interface. Matthieu Isoard <indigoping4cgmi@gmail.com>
* 1.2.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.8: Prevent unsorted ranges. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.7: Clean code. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.4: Rewrite whole macro, add BMC alias. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Accelerated mode. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Added role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
