# Rsyslog

|      OS      | Version | Supported |
|:-------------|:--------|:---------:|
| RHEL         |       9 |    yes    |
| RHEL         |      10 |    yes    |
| Ubuntu       |   24.04 |    yes    |
| Ubuntu       |   26.04 |    yes    |
| Debian       |      13 |    yes    |
| OpenSuseLeap |      16 |    yes    |

Note: RHEL 9+ templates use a small part of the advanced format: https://www.rsyslog.com/doc/configuration/converting_to_new_format.html
Role is expected to slowly move to this format in the future.

## Description

These settings provide an rsyslog configuration, for both server and client.

On server side, all logs will endup in the `/var/log/rsyslog/` folder.
## Instructions

### Server or client

These settings allow to deploy a client or a server, using `rsyslog_profile` value, which can be **server** or **client**:

On servers target, set the following in the inventory or in the playbook:

```yaml
rsyslog_profile: server
```

And on clients target, set the following in the inventory or in the playbook:

```yaml
rsyslog_profile: client
```

### Networks

Servers need to be defined in networks as services, using their ip and/or hostname:

```yaml
networks:
  net-admin:
    prefix: 16
    subnet: 10.10.0.0
    dhcp_server: true
    dns_server: true
    services:
      dns:
        - ip4: 10.10.0.1
          hostname: mg1-dns
      pxe:
        - ip4: 10.10.0.1
          hostname: mg1-pxe
      ntp:
        - ip4: 10.10.0.1
          hostname: mg1-ntp
      log:
        - ip4: 10.10.0.1          # <<<<<<
          hostname: mg1-rsyslog  
```

Note that these settings are compatible with the magic all in one services_ip key as a replacement of services key:

```yaml
networks:
  net-admin:
    prefix: 16
    subnet: 10.10.0.0
    dhcp_server: true
    dns_server: true
    services_ip: 10.10.0.1   # <<<<<<
```

### Port

Log server port is set to *514* by default, and can be customized with `rsyslog_port` variable.
This value should be set accordingly between server and client.

### Server override

It is possible, for specific configurations or debugging purposes, to override server ip4 by defining `rsyslog_server_ip4` variable in the inventory.
In that scenario, this value will be used instead of networks values.

Example:

```yaml
rsyslog_server_ip4: 10.20.0.1
```

### Verbosity

Log client verbosity defaults to *info*, it can be one of the following (defined in the syslog protocol):

```
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
```

Simply set the `rsyslog_client_verbosity` to the desired severity value.

## Advanced usage

You can inject your own custom configuration into several files, using `rsyslog_configuration_files`.
This variable can also be used to override the default rsyslog configuration.
It uses variables:
- **name**: the configuration file name
- **content**: the content of your configuration file, it can be single line or multiline
- **path**: the directory containing your configuration file, it defaults to `/etc/rsyslog.d` if it is not specified

It is important to understand that there are 2 reserved name for this variable.
If you add an entry named `server.conf`, then these settings will skip the generation of the server.conf file from these settings template and replace it with your custom version. The same apply for `client.conf`, if set, then these settings will skip the template of these settings and only use the custom version.

For example:

```yaml
rsyslog_configuration_files:
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

And to replace for example the server.conf file by a custom version:

```yaml
rsyslog_configuration_files:
  - name: server.conf
    content: |
      foobar
```

### Logrotate override

The default logrotate configuration provided by these settings may not cover all cluster needs. Override it by defining `rsyslog_logrotate_config` with the full desired content:

```yaml
rsyslog_logrotate_config: |
  /var/log/rsyslog/*/*.log
  /var/log/rsyslog/*/messages
  /var/log/rsyslog/*/cron
  /var/log/rsyslog/*/secure
  /var/log/rsyslog/*/maillog
  /var/log/rsyslog/*/spooler
  {
      daily
      missingok
      rotate 5
      sharedscripts
      postrotate
          /usr/bin/systemctl kill -s HUP rsyslog.service > /dev/null 2>/dev/null || true
      endscript
  }
```
