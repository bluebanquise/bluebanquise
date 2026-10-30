# loki

## Description

This role deploys Loki on the management host, to store and query the logs centralized by rsyslog.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

Logs flow is:

```
hosts --> rsyslog (management host) --> Alloy (127.0.0.1:1514) --> Loki (127.0.0.1:3100) <-- Grafana
```

* rsyslog forwards all the messages it receives (see the **rsyslog** role) to Alloy, using `/etc/rsyslog.d/loki.conf`.
* Alloy (successor of Promtail) receives them on a local syslog listener, adds labels, and pushes them to Loki.
* Loki stores them on the local filesystem (`/var/lib/loki`), in a single process.

The following labels are added to each log line:

| Label | Content |
|-------|---------|
| `job` | `syslog` |
| `host` | Host that emitted the message |
| `app` | Program that emitted the message (`sshd`, `kernel`...) |
| `level` | Severity (`info`, `warning`, `error`...) |

Loki can then be used as a Grafana datasource (see the **grafana** role), with URL `http://localhost:3100`:

```yaml
grafana_datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://localhost:3100
```

Example query, in Grafana Explore: `{job="syslog", host="c001", level="error"}`.

Further details: [Loki](https://grafana.com/docs/loki/latest/) and [Alloy](https://grafana.com/docs/alloy/latest/) documentation.

## Requirements

The `loki` and `alloy` packages must be available in the configured repositories. They are not provided
by the distributions, use Grafana repositories, defined in `bb_repositories` and configured by the
`repositories` role first (see the **grafana** role README for the format of each distribution). On
clusters without internet access, mirror the repository on the management host and use the local URL instead.

The role uses the systemd units and users (`loki`, `alloy`) shipped by these packages.

rsyslog must be installed and configured to receive the hosts logs (**rsyslog** role).

## Instructions

### Configuration

Loki configuration is generated in `/etc/loki/config.yml`, and checked with `loki -verify-config` before being
written. Alloy configuration is generated in `/etc/alloy/config.alloy`, and checked with `alloy fmt`.

By default, Loki only listens on `127.0.0.1`, which is enough when Grafana runs on the same host. To reach
it from another host, set `loki_ip` to an IP of the host (or `0.0.0.0`): the Loki port is then opened in the firewall.

### Retention

Logs are kept forever by default. To delete logs older than a given duration, set `loki_retention_period`,
for example `30d` or `720h`.

### Upgrade from role versions 1.x (Promtail)

Role versions 1.x used Promtail, which reached end of life, and Loki 2 configuration options removed in Loki 3.
When upgrading:

* The Promtail service is stopped and disabled, and its unit and rsyslog forwarder removed. The `promtail`
  package and user can then be removed manually.
* The role 1.x replaced the packaged `loki.service` with its own one, at the same path. A drop-in file
  (`/etc/systemd/system/loki.service.d/bluebanquise.conf`) makes sure the new configuration file is used.
* Logs stored by Loki 2 (`boltdb` index) cannot be read by Loki 3, and are not visible anymore. Loki 3 stores
  its data in other folders: once not needed anymore, delete `/var/lib/loki/index`, `/var/lib/loki/chunks` and `/tmp/wal`.
* Variables `loki_users`, `loki_groups`, `loki_conf_dir`, `loki_index_dir`, `loki_chunks_dir` and `loki_promtail_*`
  are not used anymore: the role fails if they are still set, remove them from the inventory.
  `loki_promtail_syslog_ip` and `loki_promtail_syslog_port` are replaced by `loki_syslog_ip` and `loki_syslog_port`.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `loki_ip` | `127.0.0.1` | Loki HTTP listening address. |
| `loki_port` | `3100` | Loki HTTP port. |
| `loki_grpc_port` | `9095` | Loki gRPC port (always on `127.0.0.1`). |
| `loki_data_dir` | `/var/lib/loki` | Loki data directory. |
| `loki_retention_period` | `0s` | Delete logs older than this duration, `0s` to keep them forever. |
| `loki_syslog_ip` | `127.0.0.1` | Alloy syslog listener address, receiving rsyslog traffic. |
| `loki_syslog_port` | `1514` | Alloy syslog listener port (TCP). |
| `loki_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open Loki port in, when `loki_ip` is not a loopback address. |
| `loki_enable_services` | `bb_enable_services`, else `true` | Enable loki and alloy services. |
| `loki_start_services` | `bb_start_services`, else `true` | Start loki and alloy services, and restart them on configuration changes. |

## Change log

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.0.0: Role creation. Neil Munday <neil@mundayweb.com>
