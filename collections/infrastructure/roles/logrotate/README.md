# logrotate

## Description

This role installs logrotate and manages its global configuration and custom per-service rules.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

### Global configuration

The global `/etc/logrotate.conf` is rendered from the `logrotate_global_*` variables. Default values provide a sensible baseline (daily rotation, 7 rotations, xz compression, rotated files named `<name>-<date>.log.xz`).

New log files keep the mode and owner of the rotated ones (`create` without arguments), as with distribution
defaults: services writing their logs as their own user keep working. Set `logrotate_global_create` (for example
`0640 root root`) to force them.

On Ubuntu, `/var/log` belongs to the `syslog` group and logrotate refuses to rotate files there unless told which
user and group to use: the role sets `su root adm` there, as Ubuntu does. `logrotate_global_su` overrides it.

When xz compression is enabled, the role installs xz.

### Custom rules

Custom rules are defined as a list under `logrotate_custom_rules`. Each entry generates a file under `/etc/logrotate.d/`:

```yaml
logrotate_custom_rules:
  - name: myapp
    path: /var/log/myapp/*.log
    options:
      - daily
      - rotate 14
      - compress
      - delaycompress
      - missingok
      - notifempty
      - create 0640 myapp myapp
```

On OpenSuse Leap 16, the distribution configuration moved to `/usr/etc/logrotate.conf`, and packages install their
files in `/usr/etc/logrotate.d`. The generated `/etc/logrotate.conf` takes precedence over the distribution one, and
includes both `/etc/logrotate.d` and `/usr/etc/logrotate.d`.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `logrotate_global_daily` | `true` | Rotate daily. |
| `logrotate_global_weekly` | `false` | Rotate weekly. |
| `logrotate_global_monthly` | `false` | Rotate monthly. |
| `logrotate_global_rotate` | `7` | Number of rotations to keep. |
| `logrotate_global_compress` | `true` | Compress rotated logs. |
| `logrotate_global_delaycompress` | `false` | Delay compression by one rotation. |
| `logrotate_global_missingok` | `true` | Do not error if log file is missing. |
| `logrotate_global_notifempty` | `true` | Do not rotate empty log files. |
| `logrotate_global_create` | `""` | Mode, owner and group of new log files. Empty: same as rotated file. |
| `logrotate_global_su` | `""` (`root adm` on Ubuntu) | User and group used to rotate. |
| `logrotate_global_dateext` | `true` | Use date as extension for rotated logs. |
| `logrotate_global_dateformat` | `-%Y%m%d` | Date format for rotated log names. |
| `logrotate_global_extension` | `.log` | Extension kept at the end of rotated log names. |
| `logrotate_enable_xz` | `true` | Use xz compression instead of gzip. |
| `logrotate_custom_rules` | `[]` | Custom rules (`name`, `path`, `options`), written to `/etc/logrotate.d/<name>`. |
