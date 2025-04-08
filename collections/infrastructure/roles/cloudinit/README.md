# Cloud-init

This role is inspired by https://github.com/mrlesmithjr/ansible-cloud-init from Larry Smith Jr.

## Description

This role install and configure cloud-init on the target system.
This is mostly used to execute post-installation tasks when a diskless node boots, but can also be used for diskful configuration.

## Instructions

### Quick usage

This role allows to simply pass a whole script to cloud init to execute it at boot.

To do so, create variable `cloudinit_boot_script` and add your full script in bash, on multiple lines, this way (`|` character, then whole script is indented by 2).

For example:

```yaml
cloudinit_boot_script: |
  echo "Hello world" >> /tmp/hello
  nmcli connection modify "Wired connection 1" ipv4.method manual ipv4.address 10.0.2.152/24 ipv4.gateway 10.0.2.1 ipv4.dns 10.0.2.1
```

The template will simply execute a runcmd cloud-init instruction to execute this script.

### Standard usage

The role will install cloud-init package, write its configuration, and enable the cloud-init service, but will not start the service.

By default, configuration writen by the role will do nothing.
You need to provide your own cloud-init configuration, by setting cloudinit_configuration variable, which must contain a full cloud-init configuration.

See the following documentation to help you build your needed configuration:

* Main documentation: https://cloudinit.readthedocs.io/en/latest/index.html
* Example: https://cloudinit.readthedocs.io/en/latest/reference/examples.html

For example, to make the role write a configuration that will setup an admin user "kirby" at boot:

```yaml
cloudinit_configuration:
  users:
    - name: kirby
      sudo: ALL=(ALL) NOPASSWD:ALL
      groups: users, admin
      lock_passwd: true
      ssh_authorized_keys:
        - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAXXXXXXXX...
```

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
