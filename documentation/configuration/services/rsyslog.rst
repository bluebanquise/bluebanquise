=======
Rsyslog
=======

Rsyslog allows to centralize logs of many nodes (clients) into a single folder on a specific node (server), to ease supervision and debugging.

.. note::

  RHEL 9 tempalte now uses a small part of the advanced format: https://www.rsyslog.com/doc/configuration/converting_to_new_format.html
  Role is expected to slowly move to this format in the future.

By default, logs will endup into ``/var/log/rsyslog/`` folder on the rsyslog server node.


Server or client
----------------

When deploying the rsyslog role on a node or a group of nodes, you need to specify if you wish to install a server or a client.

To do so, set variable ``rsyslog_profile`` to either ``server`` or ``client``. This variable can be set in the inventory itself, or in the playbook.

For example, in the playbook of a management server node:

.. code-block:: yaml

    - role: bluebanquise.infrastructure.rsyslog
      vars:
        rsyslog_profile: server

And in the playbook of a non management server node, so a client node:

.. code-block:: yaml

    - role: bluebanquise.infrastructure.rsyslog
      vars:
        rsyslog_profile: client

Enable rsyslog on a network
===========================

The role will make the rsyslog server listen on ``services_ip`` address of the management network,
or on any ip4 defined under ``log`` key in ``services``, and allow queries on the whole related subnet/prefix:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      dns_server: true
      services_ip: 10.10.0.1

Or:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      dns_server: true
      services:
        log:
          - hostname: mgt1
            ip4: 10.10.0.1

As described in main services documentation page, ``services:log`` will precedence ``services_ip`` if both are set.

Server port
===========

Log server port is set to **514** by default, and can be customized with ``rsyslog_port`` variable.
This value should be set accordingly between server and client.

Example:

.. code-block:: yaml

  rsyslog_port: 514

Server override
===============

It is possible, for specific configurations or debugging purposes, to override server ip4 by defining ``rsyslog_server_ip4`` variable in the inventory.
In that scenario, this value will be used instead of networks values.

Example:

.. code-block:: yaml

  rsyslog_server_ip4: 10.20.0.1

Verbosity
=========

Log client verbosity defaults to **info**, it can be one of the following (defined in the syslog protocol):

.. code-block:: text

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

Simply set the ``rsyslog_client_verbosity`` to the desired severity value.
Just remember that debug level can quickly fill the disk space.

Raw configurations
==================

rsyslog
-------

You can inject your own custom configuration into several files, using ``rsyslog_configuration_files``.

This variable can also be used to override the default rsyslog configuration.

It uses variables:

* **name**: the configuration file name
* **content**: the content of your configuration file, it can be single line or multiline
* **path**: the directory containing your configuration file, it defaults to ``/etc/rsyslog.d`` if it is not specified

It is important to understand that there are 2 reserved name for this variable.
If you add an entry named ``server.conf``, then the role will skip the generation of the server.conf
file from the role template and replace it with your custom version.
The same apply for ``client.conf``, if set, then the role will skip the template of the role and only use the custom version.

For example:

.. code-block:: yaml

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


And to replace for example the server.conf file by a custom version:

.. code-block:: yaml

  rsyslog_configuration_files:
    - name: server.conf
      content: |
        foobar

logrotate
---------

Default logrotate configuration provided by the role might not conver all the target cluster needs.

It is possible to overwride it by defining variable ``rsyslog_logrotate_config``. If set, the raw content of this multilines variable
will be used instead of default configuration.

For example:

.. code-block:: yaml

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
