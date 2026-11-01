# Cloud-init

These settings are inspired by [ansible-cloud-init](https://github.com/mrlesmithjr/ansible-cloud-init) from Larry Smith Jr.

## Description

This role installs and configures cloud-init on the target system.
This is mostly used to execute post-installation tasks when a diskless host boots, but can also be used for diskful configuration.

The role installs the cloud-init package, writes its configuration, and enables the cloud-init service for next boot, but does not start the service directly.

The configuration is written in `/etc/cloud/cloud.cfg.d/99-bluebanquise.cfg`. The distribution `/etc/cloud/cloud.cfg` file is not modified, as it defines the modules cloud-init runs at each boot stage (users creation, `runcmd`, etc.).

## Instructions

### Quick usage

The role allows passing a base64-encoded script to cloud-init to execute at boot.

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

Note that when `cloudinit_boot_script` is set, `cloudinit_configuration` is ignored: the boot script is the only configuration written.

### Standard usage

By default, the configuration written by the role does nothing (empty users and groups).
Provide your own cloud-init configuration by setting the `cloudinit_configuration` variable. Its content is written as is in the configuration file, and merged by cloud-init with the distribution configuration.

See the following documentation to help you build your needed configuration:

* [Main documentation](https://cloudinit.readthedocs.io/en/latest/index.html)
* [Examples](https://cloudinit.readthedocs.io/en/latest/reference/examples.html)

For example, to make the role write a configuration that will set up an admin user "kirby" at boot:

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

Note that setting `users` replaces the distribution default user list (for example the `default` cloud user).

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cloudinit_configuration` | `{groups: [], users: []}` | cloud-init configuration to write. |
| `cloudinit_boot_script` | not set | Base64-encoded script to run at boot. When set, replaces `cloudinit_configuration`. |
| `cloudinit_enable_services` | `bb_enable_services`, else `true` | Enable cloud-init services at boot. |
