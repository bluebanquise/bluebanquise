# Grafana

## Description

This role deploys Grafana on the host, and provisions its datasources and dashboards.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Grafana is available by default at `http://<host>:3000`, with user `admin` and password `admin`.

### Repositories

The `grafana` package must be available in the configured repositories. RHEL provides it in its
AppStream repository (Grafana 10.2 on RHEL 10), and OpenSuse Leap 16 in its main repository (Grafana 12).
On Debian and Ubuntu, or to get a recent version on RHEL, use Grafana repositories,
defined in `bb_repositories` and configured by the `repositories` role first (see the `repositories`
role README for the format of each distribution). On clusters without internet access, mirror the
repository on the management host and use the local URL instead.

**RHEL:**

```yaml
bb_repositories:
  - name: grafana
    baseurl: https://rpm.grafana.com
    gpgcheck: true
    gpgkey: https://rpm.grafana.com/gpg.key
```

**OpenSuse Leap** (only needed for a version newer than the distribution one): the key `https://rpm.grafana.com/gpg.key` must be imported (`rpm --import`):

```yaml
bb_repositories:
  - name: grafana
    repo: https://rpm.grafana.com
```

**Ubuntu:** the key `https://apt.grafana.com/gpg.key` must be available, dearmored, as `/etc/apt/keyrings/grafana.gpg`:

```yaml
bb_repositories:
  - repo: deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main
```

**Debian 13** (deb822 format):

```yaml
bb_repositories:
  - name: grafana
    uris: https://apt.grafana.com
    suites: stable
    components: main
    signed_by: /etc/apt/keyrings/grafana.gpg
```

### Admin account

The admin password is enforced at each run, using `grafana-cli`, even if it was changed using the web interface.
Use Ansible Vault to protect it:

```yaml
grafana_admin_user: admin
grafana_admin_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
```

### Configuration

The role writes a minimal `/etc/grafana/grafana.ini`: paths, listening address and port, domain and
admin account. Any other option of the [Grafana configuration](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/)
can be set in `grafana_configuration`, as a dictionary of sections, each being a dictionary of options.
These are merged over the role configuration, and can override it.

For example, to send emails, and allow anonymous read only access:

```yaml
grafana_configuration:
  smtp:
    enabled: true
    host: smtp.cluster.local:25
    from_address: grafana@cluster.local
  auth.anonymous:
    enabled: true
    org_role: Viewer
```

### LDAP authentication

Set the content of `/etc/grafana/ldap.toml` in `grafana_ldap_configuration`
(see [Grafana LDAP documentation](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/ldap/)).
The `[auth.ldap]` section is then enabled automatically:

```yaml
grafana_ldap_configuration: |
  [[servers]]
  host = "ldap.cluster.local"
  port = 389
  bind_dn = "cn=admin,dc=cluster,dc=local"
  bind_password = "secret"
  search_filter = "(uid=%s)"
  search_base_dns = ["dc=cluster,dc=local"]

  [servers.attributes]
  username = "uid"
  email = "mail"

  [[servers.group_mappings]]
  group_dn = "*"
  org_role = "Viewer"
```

### Datasources

Datasources are written to `/etc/grafana/provisioning/datasources/bluebanquise.yml`, using
[Grafana provisioning format](https://grafana.com/docs/grafana/latest/administration/provisioning/#data-sources):
any key of this format can be used.

```yaml
grafana_datasources:
  - name: prometheus
    uid: prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
```

Setting `uid` to the same value as `name` allows dashboards to refer to the datasource either way.

Removing a datasource from the list does not remove it from Grafana. To do so, delete it using the
web interface, or use `deleteDatasources` (see Grafana documentation).

### Dashboards

Dashboards are installed in `/var/lib/grafana/dashboards`, and loaded by Grafana (file provisioning).
Provisioned dashboards cannot be saved from the web interface: save a copy to edit them.

Dashboards can be downloaded from [grafana.com](https://grafana.com/grafana/dashboards/), by ID and revision.
Their datasource placeholder (like `${DS_PROMETHEUS}`) is replaced by `datasource`. The management
host needs access to grafana.com.

```yaml
grafana_dashboards:
  - dashboard_id: 1860
    revision_id: 37
    datasource: prometheus
```

Dashboards JSON files can also be stored in a folder of the Ansible host, set in `grafana_dashboards_dir`.
All `*.json` files of this folder are installed.

```yaml
grafana_dashboards_dir: /var/lib/bluebanquise/inventory/dashboards
```

To remove a dashboard, remove it from the list or folder, and delete its file on the host.

### Plugins

```yaml
grafana_plugins:
  - grafana-clock-panel
```

Plugins are downloaded by `grafana-cli`, so the host needs access to grafana.com.

### Upgrade from previous versions

Version 3.0.0 of this role was simplified, and variables of previous versions are rejected.
Most of them were grafana.ini sections, now set in `grafana_configuration`:

| Previous variable | Now |
|-------------------|-----|
| `grafana_security.admin_user`, `.admin_password` | `grafana_admin_user`, `grafana_admin_password` |
| `grafana_server`, `grafana_database`, `grafana_remote_cache`, `grafana_users`, `grafana_auth`, `grafana_analytics`, `grafana_smtp`, `grafana_alerting`, `grafana_log`, `grafana_metrics`, `grafana_tracing`, `grafana_snapshots`, `grafana_image_storage`, `grafana_panels` | Matching sections (`server`, `database`, `smtp`, `unified_alerting`, etc.) in `grafana_configuration` |
| `grafana_welcome_email_on_sign_up` | `grafana_configuration.emails.welcome_email_on_sign_up` |
| `grafana_url` | `grafana_configuration.server.root_url` |
| `grafana_ldap` | `grafana_ldap_configuration`, now the raw `ldap.toml` content |
| `grafana_datasources` | Same name, now in Grafana provisioning format (`basicAuthPassword` goes into `secureJsonData`, etc.) |
| `grafana_api_keys`, `grafana_api_keys_dir` | Removed: API keys were removed from Grafana 12. Use service accounts. |
| `grafana_install_oss_packages` | Removed: use Grafana repositories. |
| `grafana_cap_net_bind_service` | Removed: use a reverse proxy to serve Grafana on ports below 1024. |
| `grafana_provisioning_synced`, `grafana_instance`, `grafana_logs_dir`, `grafana_data_dir`, `grafana_user_uid`, `grafana_user_gid`, `grafana_user_home`, `grafana_session`, `grafana_environment`, `grafana_alert_notifications` | Removed. |

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `grafana_address` | `0.0.0.0` | Listening address. |
| `grafana_port` | `3000` | Listening port. |
| `grafana_domain` | host FQDN | Domain name used to reach Grafana. |
| `grafana_admin_user` | `admin` | Admin user name. |
| `grafana_admin_password` | `admin` | Admin password, enforced at each run. |
| `grafana_configuration` | `{}` | Additional grafana.ini sections and options. |
| `grafana_ldap_configuration` | `""` | Content of `/etc/grafana/ldap.toml`. Enables LDAP authentication when set. |
| `grafana_plugins` | `[]` | Plugins to install. |
| `grafana_datasources` | `[]` | Datasources, in Grafana provisioning format. |
| `grafana_dashboards` | `[]` | Dashboards to download from grafana.com (`dashboard_id`, `revision_id`, `datasource`). |
| `grafana_dashboards_dir` | `""` | Folder of the Ansible host containing dashboards JSON files to install. |
| `grafana_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open the Grafana port in. |
| `grafana_enable_services` | `bb_enable_services`, else `true` | Enable Grafana service. |
| `grafana_start_services` | `bb_start_services`, else `true` | Start Grafana service, and enforce admin password. |
