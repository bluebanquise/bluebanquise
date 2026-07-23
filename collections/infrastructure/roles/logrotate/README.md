# logrotate

## Description

This role installs logrotate and manages its global configuration and custom per-service rules.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

### Global configuration

The global `/etc/logrotate.conf` is rendered from the `logrotate_global_*` variables. Default values provide a sensible baseline (daily rotation, 7 rotations, xz compression).

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

## Variables

| Variable                       | Default          | Description                          |
|:-------------------------------|:-----------------|:-------------------------------------|
| logrotate_global_daily         | true             | Rotate daily                         |
| logrotate_global_weekly        | false            | Rotate weekly                        |
| logrotate_global_monthly       | false            | Rotate monthly                       |
| logrotate_global_rotate        | 7                | Number of rotations to keep          |
| logrotate_global_compress      | true             | Compress rotated logs                |
| logrotate_global_delaycompress | false            | Delay compression by one rotation    |
| logrotate_global_missingok     | true             | Do not error if log file is missing  |
| logrotate_global_notifempty    | true             | Do not rotate empty log files        |
| logrotate_global_create        | "0640 root root" | Create new log file after rotation   |
| logrotate_global_dateext       | true             | Use date as extension for rotated logs |
| logrotate_global_dateformat    | "-%Y%m%d"        | Date format for rotated log names    |
| logrotate_global_extension     | log              | Default log file extension           |
| logrotate_enable_xz            | true             | Use xz compression instead of gzip  |
| logrotate_custom_rules         | []               | List of custom per-service rules     |

## Output

Packages installed:

* logrotate

Files generated:

* /etc/logrotate.conf
* /etc/logrotate.d/{{ item.name }} (one per entry in logrotate_custom_rules)

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
