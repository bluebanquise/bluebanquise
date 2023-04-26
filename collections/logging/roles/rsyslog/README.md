# Log

|      OS      | Version | Supported |
|:-------------|:--------|:---------:|
| Ubuntu       |   20.04 |    yes    |
| Ubuntu       |   22.04 |    yes    |
| RHEL         |       7 |    yes    |
| RHEL         |       8 |    yes    |
| RHEL         |       9 |    yes    |
| OpenSuseLeap |      15 |    yes    |
| Debian       |      11 |    yes    |

## Description

This role provides an rsyslog configuration, for both server and client.

## Instructions

Log server port is set to 514 by default, and can be customized with log_port variable.
This value should be set accordingly between server and client.

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

## Advanced usage

You can inject your own custom configuration into several files, using `log_configuration_files`.
This variable can also be used to override the default rsyslog configuration.
It uses variables:
- **name**: the configuration file name
- **content**: the content of your configuration file, it can be single line or multiline
- **path**: the directory containing your configuration file, it defaults to `/etc/rsyslog.d` if it is not specified

For example:

```yaml
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
```

## Changelog

* 1.4.2: Update to BB 2.0 format. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.4.1: Register server local apps locally;more precise logrotate wildcards. <boubee.thiago@gmail.com>
* 1.4.0: Merge both client and server. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.1: Add OpenSuSE support. Neil Munday <neil@mundayweb.com>
* 1.2.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Add custom configuration path. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Enable custom rsyslog configuration with log_client_custom_config <dilassert@gmail.com>
* 1.0.4: Enable verbosity configuration with log_client_verbosity <dilassert@gmail.com>
* 1.0.3: Enable log server port customization with log_client_server_port. strus38
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
