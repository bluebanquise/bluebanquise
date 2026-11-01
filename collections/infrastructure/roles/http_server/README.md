# HTTP server

## Description

This role installs, configures, and starts an HTTP server (Apache). It also allows restricting listening interfaces, enabling modules, and pushing raw configuration snippets.

The HTTP server is used by a wide range of roles, from repositories to PXE and diskless.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

If you need more advanced configurations, consider using an external role such as [geerlingguy/ansible-role-apache](https://github.com/geerlingguy/ansible-role-apache).

## Instructions

Folders listing is allowed in the default document root (`/var/www/html`, or `/srv/www/htdocs` on Suse),
so that repositories and images can be browsed. On Suse, the role adds `/etc/apache2/conf.d/bluebanquise.conf`
for this purpose, as the distribution configuration does not allow it.

When the configuration changes, it is checked with `apachectl configtest` (`apache2ctl configtest` on Debian and Ubuntu, `start_apache2 -t` on Suse) before Apache is restarted: an
invalid configuration makes the role fail, and the running Apache is left untouched.

### Restrict listen (ports and IPs)

These settings are useful to secure the web server by preventing listening on unwanted interfaces. They can also be combined with the **haproxy** role when listening on a virtual IP.

Set `http_server_listen` to a list of `ip:port` pairs, IPs (port 80), or ports (all addresses):

```yaml
http_server_listen:
  - 10.10.0.1:80   # explicit ip:port
  - 10.20.0.1      # implicit port 80
  - 7777           # all addresses, custom port
```

Or set it to `auto` to listen on port 80 of all IPs of the host `network_interfaces`:

```yaml
http_server_listen: auto
```

When `http_server_listen` is set, the distribution default `Listen 80` directive is commented out to avoid
conflicts. It is restored, and the custom listen configuration removed, when `http_server_listen` is unset.

Ports other than 80 found in `http_server_listen` are opened in the firewall, in addition to the `http` service.

### Enable modules

You can enable specific Apache modules using the `http_server_modules` list. Each entry must be a dict with at least a `name` key:

```yaml
http_server_modules:
  - name: cgi
  - name: rewrite
    state: present
```

This uses `a2enmod`, which only exists on Debian, Ubuntu and Suse. On RedHat family systems, modules are
loaded by `/etc/httpd/conf.modules.d/` files (use `http_server_configurations_files` to load additional
ones), and the role fails if `http_server_modules` is set.

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

Each entry generates a file under the OS Apache configuration folder (`/etc/httpd/conf.d/myapp.conf`,
`/etc/apache2/conf-enabled/myapp.conf`, or `/etc/apache2/conf.d/myapp.conf`).

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `http_server_listen` | not set | `auto`, or list of `ip:port`, `ip` or `port` to listen on. Not set: distribution default (port 80, all addresses). |
| `http_server_modules` | `[]` | Apache modules to enable (Debian, Ubuntu and Suse only). |
| `http_server_configurations_files` | `[]` | Raw configuration files (`name`, `configuration`). |
| `http_server_firewall_services_to_add` | `[http]` | Firewall services to open. |
| `http_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open services and ports in. |
| `http_server_enable_services` | `bb_enable_services`, else `true` | Enable Apache service. |
| `http_server_start_services` | `bb_start_services`, else `true` | Start Apache service, and restart it on configuration changes. |
