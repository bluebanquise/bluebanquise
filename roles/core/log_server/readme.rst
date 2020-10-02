Log server
----------

Description
^^^^^^^^^^^

This role provides an rsyslog server to gather logs of all hosts.

Instructions
^^^^^^^^^^^^

All logs are separated by systemd instances into /var/log/rsyslog/ .

rsyslog port is set to 514 by default, and can be customized with log_server_rsyslog_port variable.

Changelog
^^^^^^^^^
* 1.0.3: Enable rsyslog port customization with log_server_rsyslog_port. strus38
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
