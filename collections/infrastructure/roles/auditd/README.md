# Auditd

## Description

This role installs and enables auditd on RedHat, Debian, Ubuntu, and Suse family systems.

It can also:

* Forward audit logs to the local syslog daemon (see [Red Hat solution 4986931](https://access.redhat.com/solutions/4986931)). Logs then reach a remote syslog server only if the local syslog daemon is configured to forward them (see the `rsyslog` role, client part).
* Log every command executed by the root user, including through su/sudo.

Note that auditd cannot be restarted using `systemctl` on RedHat family systems, so the role restarts it using the legacy `service` command (see [Red Hat solution 2664811](https://access.redhat.com/solutions/2664811)).

## Instructions

Since auditd manages sensitive data, logs forwarding is disabled by default. Set `auditd_forward_audit_logs` to `true` to enable it.

Set `auditd_config_root_log` to `true` to log commands entered by the root user.

Both settings can be switched back to `false` later: the role then disables logs forwarding and removes the root logging rules.

Files (path may slightly vary depending on target distribution):

* /etc/audit/auditd.conf - configuration file for the audit daemon
* /etc/audit/rules.d/audit.rules - audit rules to be loaded at startup
* /etc/audit/plugins.d/syslog.conf - controls the configuration of the syslog plugin

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `auditd_forward_audit_logs` | `false` | Forward audit logs to the local syslog daemon. |
| `auditd_config_root_log` | `false` | Log all commands executed by root (euid 0). |
| `auditd_enable_services` | `bb_enable_services`, else `true` | Enable auditd at boot. |
| `auditd_start_services` | `bb_start_services`, else `true` | Start auditd, and restart it on configuration change. |

