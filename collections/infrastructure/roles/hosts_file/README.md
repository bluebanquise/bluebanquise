# Hosts file

## Description

This role provides a basic /etc/hosts files.

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

This role is using `hosts_file_domaine_name` variable to set FQDN. Default is **cluster.local**.
Note that `hosts_file_domaine_name` is precedenced by the global variable `bb_domain_name` if set. 

## Changelog

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
