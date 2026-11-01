# SSHD

## Description

These settings configure the SSHD daemon on hosts.

Objective is to harden a few settings and keep the default configuration for most other settings.

These settings write `/etc/ssh/sshd_config.d/00-bluebanquise.conf`. Files of this directory are included at the top of
`sshd_config` in alphabetical order, and sshd uses the first value found for each setting: these settings take
precedence over the distribution ones, including other files of the directory (for example `50-cloud-init.conf` on Ubuntu).
Role versions before 1.1.0 wrote `bluebanquise.conf`, read after such files: it is removed.

The configuration is checked with `sshd -t` before sshd is restarted, so that an invalid configuration does not stop
a running sshd.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16 (where the distribution
configuration is `/usr/etc/ssh/sshd_config`, which already includes the directory).

> **Note:** By default all variables are unset, so without any configuration set, this will do nothing.

## Instructions

### Disable password authentication

To prevent password-based logins, set `sshd_passwordauthentication` to `no`:

```yaml
sshd_passwordauthentication: no
```

### Disable root access

To prevent root from logging in via SSH:

```yaml
sshd_permitrootlogin: no
```

### Restrict user access

Use `sshd_denyusers`, `sshd_allowusers`, `sshd_denygroups`, and `sshd_allowgroups` to restrict which users can connect. OpenSSH evaluates these in exactly this order - the first match takes precedence.

> **Note:** Remember to allow the bluebanquise user so that Ansible can still push configuration. On most hosts, restricting access to only the bluebanquise user is a good default.

```yaml
sshd_denyusers:
sshd_allowusers: bluebanquise anotheruser
sshd_denygroups:
sshd_allowgroups:
```

### Raw configuration

Any other OpenSSH server directives can be injected verbatim using `sshd_raw`:

```yaml
sshd_raw: |
  X11Forwarding no
  PermitTunnel no
```

YAML booleans (`yes`, `no`, `true`, `false` without quotes) are written as `yes` and `no`.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `sshd_permitrootlogin` | not set | `PermitRootLogin` (`yes`, `no`, `prohibit-password`...). |
| `sshd_passwordauthentication` | not set | `PasswordAuthentication`. |
| `sshd_denyusers` / `sshd_allowusers` | not set | `DenyUsers` / `AllowUsers` (space separated). |
| `sshd_denygroups` / `sshd_allowgroups` | not set | `DenyGroups` / `AllowGroups` (space separated). |
| `sshd_raw` | not set | Raw directives, written first. |
| `sshd_server_firewall_services_to_add` | `[ssh]` | Firewall services to open. |
| `sshd_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone. |
| `sshd_server_enable_services` | `bb_enable_services`, else `true` | Enable sshd service. |
| `sshd_server_start_services` | `bb_start_services`, else `true` | Start sshd service, and restart it on configuration changes. |
