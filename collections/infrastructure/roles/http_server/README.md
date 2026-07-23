# HTTP server

## Description

These settings install, configures, and starts an HTTP server (Apache). It also allows restricting listening interfaces, enabling modules, and pushing raw configuration snippets.

The HTTP server is used by a wide range of roles, from repositories to PXE and diskless.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

If you need more advanced configurations, consider using an external role such as [geerlingguy/ansible-role-apache](https://github.com/geerlingguy/ansible-role-apache).

## Instructions

### Restrict listen (ports and IPs)

These settings are useful to secure the web server by preventing listening on unwanted interfaces. They can also be combined with the **haproxy** role when listening on a virtual IP.

Set `http_server_listen` to a list of IPs, ports, or `ip:port` pairs:

```yaml
http_server_listen:
  - 10.10.0.1:80   # explicit ip:port
  - 10.20.0.1      # implicit port 80
  - 7777            # all interfaces, custom port
```

Or set it to `auto` to generate listen directives from the host's `network_interfaces`:

```yaml
http_server_listen: auto
```

When `http_server_listen` is set, these settings automatically comments out the distribution's default `Listen 80` line to avoid conflicts. To explicitly disable the default listen directive regardless:

```yaml
http_server_listen_disable_default: true
```

Default is `false`.

### Enable modules

You can enable specific Apache modules using the `http_server_modules` list. Each entry must be a dict with at least a `name` key:

```yaml
http_server_modules:
  - name: cgi
  - name: rewrite
    state: present
```

### Push raw configuration

You can push raw Apache configuration snippets using `http_server_configurations_files`:

```yaml
http_server_configurations_files:
  - name: myapp
    configuration: |
      <VirtualHost *:8080>
        ServerName myapp.cluster.local
        DocumentRoot /var/www/myapp
      </VirtualHost>
```

Each entry generates a file under the OS Apache conf directory (e.g. `/etc/httpd/conf.d/myapp.conf`).
