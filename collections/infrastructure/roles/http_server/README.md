# HTTP server

## Description

This role simply install, configures, and start an http server.

The http server is used in a wide range of roles, from repositories to PXE or diskless.

Role configuration is reduced to minimum needed for most cluster's requirements.
If you need more advanced configurations, consider using an external role, like [https://github.com/geerlingguy/ansible-role-apache](https://github.com/geerlingguy/ansible-role-apache).

## Instructions

### Restrict listen (ports and ip)

These settings are useful combined with **haproxy** role in case you need to listen on a virtual ip and avoid conflicts.

You can combine the following settings:

Simply set the `http_server_listen` list, as a list of ip (port 80 is then considered implicit), port (will listen on all interfaces) or ip:port couple to be precise:

```yaml
http_server_listen:
  - 10.10.0.1:80
  - 10.20.0.1 #  implicit port 80
  - 7777
```

If you wish listen to be auto generated from Ansible inventory declared `network_interfaces` of the target host, simple set `http_server_listen_from_inventory` to **true**. If set to true, http server will be configured to listen on all ip listed under its `network_interfaces` definition, on port 80.
Default is false.

```yaml
http_server_listen_from_inventory: true
```

Lastly, if you wish the role to disable default listen configuration setup by distribution packages, set `http_server_listen_disable_default` to true. Default is false.

```yaml
http_server_listen_disable_default: true
```






```yaml
http_server_custom_ports:
  - 8080
```

Note: this will not remove default 80 port, but only add new additional ports for http requests.

### Restrict listen on specific ip

This setting is useful combined with **haproxy** role in case you need to listen on a virtual ip and avoid conflicts.

You can either instruct http server to only listen on specific ip:

```yaml
http_server_listen_only_on:
  - 10.10.0.1:80
  - 10.20.0.1
```

Note that you can specify the port authorized per interface or allow all by not defining a port.

Or use the automatic mechanism to let the role restrict http sever to host's defined network_interfaces in the Ansible inventory.

```yaml
http_server_listen_only_on: auto
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

>>>>> LEGACY, to be included in documentation instead and in repositories client role.

This role simply install an http server. Repositories files manipulations have
to be done manually by system administrator. Refer to main documentation.

There is a split between boot images and packages repositories. Boot images
include the installer system which starts the deployment after PXE boot, while
packages repositories include the software that will be installed on the
systems.

Boot images repositories structure follows a specific pattern and includes the
minor release version in the path:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/centos/7.6/x86_64/os/

Packages repositories structure follows a specific pattern, which defaults to
the major release version in the path:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/centos/7/x86_64/os/

System administrator should create these directories manually, and put boot
images and packages inside.

Note: we recommend to use the same directory path to later sync the Errata
published by upstream operating system vendor.

Then, repositories that will be setup on clients are stored by default in
*/etc/bluebanquise/inventory/group_vars/all/general_settings/repositories.yml*.

Keep in mind that it is possible to precede this file in equipment_profiles
groups, and so put a repository file in for example
*/etc/bluebanquise/inventory/group_vars/equipment_supermicro_sandy_compute*
that will be considered by these nodes over the default one. This can be useful
to define different repositories for different equipment.

Input
^^^^^

None

Output
^^^^^^

Http server packages installed.

Changelog
^^^^^^^^^

* 1.2.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.2: Added OpenSuSE support. Neil Munday <neil@mundayweb.com>
* 1.1.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Regrouped all distribs into a main file. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
