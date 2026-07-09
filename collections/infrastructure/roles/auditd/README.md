# Auditd

## Description

These settings provide the default auditd configuration suitable for RedHat, Debian, Ubuntu, and Suse family systems.

It also allows sending audit logs to the syslog server (cf: https://access.redhat.com/solutions/4986931),
and is able to restart the auditd service using the FQCN module (solves: https://access.redhat.com/solutions/2664811).

## Instructions

Since auditd manages sensitive data, you need to manually set variable `auditd_forward_audit_logs` to `true` to send audit logs to the rsyslog server.
Set `auditd_config_root_log` to `true` to log commands entered by the root user, including su/sudo.

Files (path may slightly vary depending on target distribution):

* /etc/audit/auditd.conf - configuration file for the audit daemon
* /etc/audit/rules.d/audit.rules - audit rules to be loaded at startup
* /etc/audit/plugins.d/syslog.conf - controls the configuration of the syslog plugin
