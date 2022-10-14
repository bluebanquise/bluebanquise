# Set Hostname

## Description

This role simply set a node static (hardcoded) hostname.

## Instruction

By default, an FQDN hostname is set. If user wish to set a basic hostname, 
variable `set_hostname_fqdn` must be set to **false**.

FQDN is based on content of variable `set_hostname_domain_name` (default is **cluster.local**).
Note that `set_hostname_domain_name` is precedenced by the global variable `bb_domain_name` if set.

Note also that using this role identify the node.
This should not be used when creating a diskless golden image.

## Changelog

* 1.2.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Add fully qualified domain name capability. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
