Log client
----------

Description
^^^^^^^^^^^

This role provides an rsyslog client, to be used in combinaison with the log_server role.

Instructions
^^^^^^^^^^^^

Log server port is set to 514 by default, and can be customized with log_client_server_port variable.
This value should be set accordingly to the log_server_port variable.

To be done
^^^^^^^^^^

Integrate journalctl logging instead of rsyslog.

Changelog
^^^^^^^^^
* 1.0.3: Enable log server port customization with log_client_server_port. strus38
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
