# HTTP server

## Description

This role simply install, configures, and start an http server. It also allows to restrict listening of web server, enable modules, and push basic raw configurations.

The http server is used in a wide range of roles, from repositories to PXE or diskless.

Role configuration is reduced to minimum needed for most cluster's requirements.
If you need more advanced configurations, consider using an external role, like [https://github.com/geerlingguy/ansible-role-apache](https://github.com/geerlingguy/ansible-role-apache).

## Instructions

### Restrict listen (ports and ip)

These settings are useful to secure web server by preventing listening on non desired interfaces. It can also be combined with **haproxy** role in case you need to listen on a virtual ip and avoid conflicts.

To define ip:port or port to listen, simply set the `http_server_listen` list, as a list of ip (port 80 is then considered implicit), port (will listen on all interfaces) or ip:port couple to be precise.

```yaml
http_server_listen:
  - 10.10.0.1:80
  - 10.20.0.1 #  implicit port 80
  - 7777
```

If you wish listen configuration to be auto generated from Ansible inventory `network_interfaces` key of the target host, simple set value to `auto`. In that case, http server will be configured to listen on all ip listed under its `network_interfaces` definition, on port 80.

```yaml
http_server_listen: auto
```

Lastly, if you wish the role to disable default listen configuration setup by distribution packages, set `http_server_listen_disable_default` to true. Default is false.

```yaml
http_server_listen_disable_default: true
```

### Enable a specific module

You can request specific modules to be enabled using the `http_server_modules` list:

```yaml
http_server_modules:
  - cgi
```

### Push a dedicated configuration

In case of more complex need, you can push raw configuration using the `http_server_configurations_files` variable, as a list of name/configuration keys couple, configuration containing the raw content of apache settings you wish to apply.

```yaml
http_server_configurations_files:
  - name: ..
    configuration: |
    ....
```

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.3.2: Adapt to os hw split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Update to BB 2.0 format. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.3.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.2: Added OpenSuSE support. Neil Munday <neil@mundayweb.com>
* 1.1.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Regrouped all distribs into a main file. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
