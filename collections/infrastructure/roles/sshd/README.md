# SSHD

## Description

These settings configure the SSHD daemon on hosts.

Objective is to harden a few settings and keep the default configuration for most other settings.

These settings write a configuration file into the sshd include directory, so its settings are loaded first and take precedence over the system defaults.

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

Use `sshd_denyusers`, `sshd_allowusers`, `sshd_denygroups`, and `sshd_allowgroups` to restrict which users can connect. OpenSSH evaluates these in exactly this order — the first match takes precedence.

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
