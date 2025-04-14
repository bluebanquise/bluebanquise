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

Note: RHEL 9 tempalte now use a small part of the advanced format: https://www.rsyslog.com/doc/configuration/converting_to_new_format.html
Role is expected to slowly move to this format in the future.

## Description

This role provides an rsyslog configuration, for both server and client.

On server side, all logs will endup in the `/var/log/rsyslog/` folder.

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 1 (Networks)
* Section 2 (Hosts definition)

## Instructions

### Server or client

The role allows to deploy a client or a server, using `rsyslog_profile` value, which can be **server** or **client**:

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

Note that the role is compatible with the magic all in one services_ip key as a replacement of services key:

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
If you add an entry named `server.conf`, then the role will skip the generation of the server.conf file from the role template and replace it with your custom version. The same apply for `client.conf`, if set, then the role will skip the template of the role and only use the custom version.

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

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.6.1: Fix documentation and start move to advanced format for RHEL 9 version. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.0: Add rsyslog_server_ip4 to override network values. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.1: Fix typo in client template (reported by @sgaosdgr). Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.0: Allow services and services_ip together. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.6: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.5: Fix variables names and datamodel compatibility and update readme. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.4: Fix variables names. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.3: Proper command to restart rsyslog post rotation. Thiago Cardozo <boubee.thiago@gmail.com>
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
