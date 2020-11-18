Log client
----------

Description
^^^^^^^^^^^

This role provides an rsyslog client, to be used in combinaison with the log_server role.

Instructions
^^^^^^^^^^^^

Log server port is set to 514 by default, and can be customized with log_client_server_port variable.
This value should be set accordingly to the log_server_port variable.

Log client verbosity defaults to info, it can be one of the following (defined in the syslog protocol):

+----------+----------------------------------+
| Severity | Logs type                        |
+==========+==================================+
| emerg    | system is unusable               |
+----------+----------------------------------+
| alert    | action must be taken immediately |
+----------+----------------------------------+
| crit     | critical conditions              |
+----------+----------------------------------+
| err      | error conditions                 |
+----------+----------------------------------+
| warning  | warning conditions               |
+----------+----------------------------------+
| notice   | normal but significant condition |
+----------+----------------------------------+
| info     | informational messages           |
+----------+----------------------------------+
| debug    | debug-level messages             |
+----------+----------------------------------+

To be done
^^^^^^^^^^

Integrate journalctl logging instead of rsyslog.

Changelog
^^^^^^^^^
* 1.0.4: Enable verbosity configuration with log_client_verbosity <dilassert@gmail.com>
* 1.0.3: Enable log server port customization with log_client_server_port. strus38
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
