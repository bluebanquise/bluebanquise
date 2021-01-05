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


You can split the configuration into several files, using **log_client_configuration_files**. 
This variable can also be used to override the default rsyslog configuration.
It uses variables:
- **name**: the configuration file name
- **content**: the content of your configuration file, it can be single line or multiline
- **path**: the directory containing your configuration file, it defaults to /etc/rsyslog.d if it is not specified

For example:

.. code-block:: yaml

  log_client_configuration_files:
    - name: local-rules.conf
      content: |
        *.info;mail.none;authpriv.none;cron.none                /var/log/messages
        authpriv.*                                              /var/log/secure
        mail.*                                                  -/var/log/maillog
        cron.*                                                  /var/log/cron
        *.emerg                                                 :omusrmsg:*
        uucp,news.crit                                          /var/log/spooler
        local7.*                                                /var/log/boot.log
  
    - name: forwarding-rules.conf
      content: |
        *.* @@10.0.0.0:514
    - name: rsyslog.conf
      path: /etc
      content: |
        # rsyslog configuration file

        # For more information see /usr/share/doc/rsyslog-*/rsyslog_conf.html
        # If you experience problems, see http://www.rsyslog.com/doc/troubleshoot.html

        #### MODULES ####

        # The imjournal module bellow is now used as a message source instead of imuxsock.
        $ModLoad imuxsock # provides support for local system logging (e.g. via logger command)
        $ModLoad imjournal # provides access to the systemd journal
        #$ModLoad imklog # reads kernel messages (the same are read from journald)
        #$ModLoad immark  # provides --MARK-- message capability

        # Include all config files in /etc/rsyslog.d/
        $IncludeConfig /etc/rsyslog.d/*.conf
        ...

To be done
^^^^^^^^^^

Integrate journalctl logging instead of rsyslog.

Changelog
^^^^^^^^^
* 1.1.0: Enable custom rsyslog configuration with log_client_custom_config <dilassert@gmail.com>
* 1.0.4: Enable verbosity configuration with log_client_verbosity <dilassert@gmail.com>
* 1.0.3: Enable log server port customization with log_client_server_port. strus38
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
