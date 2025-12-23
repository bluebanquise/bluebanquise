====
HTTP
====

The http server is used in a wide range of roles, from repositories to PXE or diskless.

Stack can simply install, configures, and start an http server.
It also allows to restrict listening of web server, enable modules, and push basic raw configurations.

If you need more advanced configurations, consider using an external role, like [https://github.com/geerlingguy/ansible-role-apache](https://github.com/geerlingguy/ansible-role-apache).

Restrict listen (ports and ip)
==============================

These settings are useful to secure web server by preventing listening on non desired interfaces.
It can also be combined with **haproxy** in case you need to listen on a virtual ip and avoid conflicts.

To define ip:port or port to listen, simply set the ``http_server_listen`` list, as a list of ip (port 80 is then considered implicit), port (will listen on all interfaces) or ip:port couple to be precise.

.. code:: yaml

  http_server_listen:
    - 10.10.0.1:80
    - 10.20.0.1 #  implicit port 80
    - 7777      #  will listen on all ip

If you wish listen configuration to be auto generated from Ansible inventory ``network_interfaces`` key of the target host, simple set value to ``auto``.
In that case, http server will be configured to listen on all ip listed under its ``network_interfaces`` definition, on port 80.

.. code:: yaml

  http_server_listen: auto

Lastly, if you wish the role to disable default listen configuration setup by distribution packages,
set ``http_server_listen_disable_default`` to ``true``. Default is ``false``.

.. code:: yaml

  http_server_listen_disable_default: true

Enable a specific module
========================

You can request specific modules to be enabled using the ``http_server_modules`` list:

.. code:: yaml

  http_server_modules:
    - cgi

Raw custom configuration
========================

In case of more complex need, you can push raw configuration using the ``http_server_configurations_files`` variable,
as a list of name/configuration keys couple, configuration containing the raw content of apache settings you wish to apply.

.. code:: yaml

  http_server_configurations_files:
    - name: ..
      configuration: |
      ....
