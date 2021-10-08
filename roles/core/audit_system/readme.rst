Audit system
------------

Description
^^^^^^^^^^^

This role provides the default auditd configuration which is suitable for RHEL8 systems.
Also allows to send the audit logs to the syslog server (cf: https://access.redhat.com/solutions/4986931)

Instructions
^^^^^^^^^^^^

Files: 

* /etc/audit/auditd.conf - configuration file for audit daemon
* /etc/audit/audit.rules - audit rules to be loaded at startup
* /etc/audit/plugins.d/syslog.conf - controls the configuration of the syslog plugin

Changelog
^^^^^^^^^
* 1.0.0: Role creation. osmocl <osmocl@osmo.cl>
