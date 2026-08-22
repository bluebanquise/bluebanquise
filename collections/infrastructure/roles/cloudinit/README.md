# Cloud-init

These settings are inspired by https://github.com/mrlesmithjr/ansible-cloud-init from Larry Smith Jr.

## Description

These settings install and configures cloud-init on the target system.
This is mostly used to execute post-installation tasks when a diskless host boots, but can also be used for diskful configuration.

These settings will install the cloud-init package, write its configuration, and enable the cloud-init service for next boot, but will not start the service directly.

## Instructions

### Quick usage

These settings allow passing a base64-encoded script to cloud-init to execute at boot.

First, encode your script using:

```bash
cat myscript.sh | base64 -w 0
```

Then set the resulting string as the value of `cloudinit_boot_script`:

```yaml
cloudinit_boot_script: ZWNobyAiSGVsbG8gd29ybGQiID4+IC90bXAvaGVsbG8K
```

At boot, cloud-init will decode and execute the script via:

```
echo <base64_content> | base64 -d | /bin/bash
```

### Standard usage

By default, the configuration written by these settings will do nothing (empty users and groups).
You need to provide your own cloud-init configuration by setting the `cloudinit_configuration` variable, which must contain a full cloud-init configuration.

See the following documentation to help you build your needed configuration:

* Main documentation: https://cloudinit.readthedocs.io/en/latest/index.html
* Examples: https://cloudinit.readthedocs.io/en/latest/reference/examples.html

For example, to make these settings write a configuration that will set up an admin user "kirby" at boot:

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
