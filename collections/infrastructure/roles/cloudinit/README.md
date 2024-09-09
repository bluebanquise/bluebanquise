# Cloud-init

This role is inspired by https://github.com/mrlesmithjr/ansible-cloud-init from Larry Smith Jr.

## Description

This role install and configure cloud-init on the target system.
This is mostly used to execute post-installation tasks when a diskless node boots, but can also be used for diskful configuration.

## Instructions

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

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
