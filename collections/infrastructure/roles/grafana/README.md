# Grafana

## Description

These settings deploy Grafana on the host. It allows configuring:
- Server, security, database, and auth settings (via `grafana.ini`)
- Dashboards (from grafana.com or local JSON files)
- Datasources
- Plugins
- LDAP connection
- API keys

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Grafana is available by default at `http://<host>:3000` with user `admin` / password `admin`.

### Variables

| Name | Default | Description |
|---|---|---|
| `grafana_provisioning_synced` | `false` | Remove previously provisioned dashboards no longer referenced |
| `grafana_install_oss_packages` | `false` | Install Grafana OSS directly from grafana.com instead of system repositories |
| `grafana_instance` | `{{ ansible_fqdn \| default(inventory_hostname) }}` | Grafana instance name |
| `grafana_logs_dir` | `/var/log/grafana` | Path to logs directory |
| `grafana_data_dir` | `/var/lib/grafana` | Path to data directory |
| `grafana_address` | `0.0.0.0` | Address Grafana listens on |
| `grafana_port` | `3000` | Port Grafana listens on |
| `grafana_cap_net_bind_service` | `false` | Allow binding to ports below 1024 without root |
| `grafana_url` | `http://{{ grafana_address }}:{{ grafana_port }}` | Public URL for Grafana |
| `grafana_api_url` | `{{ grafana_url }}` | URL used for API provisioning calls |
| `grafana_domain` | `{{ ansible_fqdn \| default('localhost') }}` | Domain used in root_url (OAuth) |
| `grafana_server` | see defaults | `[server]` section options |
| `grafana_security` | `{admin_user: admin, admin_password: admin}` | `[security]` section options |
| `grafana_database` | `{type: sqlite3}` | `[database]` section options |
| `grafana_welcome_email_on_sign_up` | `false` | Send welcome email after sign-up |
| `grafana_users` | see defaults | `[users]` section options |
| `grafana_auth` | `{}` | `[auth]` section options |
| `grafana_ldap` | `{}` | LDAP configuration (servers and group_mappings) |
| `grafana_session` | `{}` | `[session]` section options |
| `grafana_analytics` | `{}` | `[analytics]` section options |
| `grafana_smtp` | `{}` | `[smtp]` section options |
| `grafana_alerting` | `{execute_alerts: true}` | `[alerting]` section options |
| `grafana_log` | `{}` | `[log]` section options |
| `grafana_metrics` | `{}` | `[metrics]` section options |
| `grafana_tracing` | `{}` | `[tracing]` section options |
| `grafana_snapshots` | `{}` | `[snapshots]` section options |
| `grafana_image_storage` | `{}` | `[external_image_storage]` section options |
| `grafana_plugins` | `[]` | List of Grafana plugins to install |
| `grafana_dashboards` | `[]` | List of dashboards to import from grafana.com |
| `grafana_dashboards_dir` | `dashboards` | Local directory with dashboard JSON files |
| `grafana_datasources` | `[]` | List of datasources to configure |
| `grafana_api_keys` | `[]` | List of API keys to create |
| `grafana_api_keys_dir` | `~/grafana/keys` | Local directory to store generated API key files |
| `grafana_environment` | `{}` | Extra environment variables for grafana-server |
| `grafana_panels` | `{}` | `[panels]` section options |
| `grafana_user_gid` | (unset) | Force grafana group GID |
| `grafana_user_uid` | (unset) | Force grafana user UID |
| `grafana_user_home` | `/usr/share/grafana` | grafana user home directory |

Security note: these settings alway resets the admin password to the value in `grafana_security.admin_password`. Use Ansible Vault to protect it:

```yaml
grafana_security:
  admin_user: admin
  admin_password: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    ...
```

### Datasources

```yaml
grafana_datasources:
  - name: prometheus
    type: prometheus
    access: proxy
    url: 'http://localhost:9090'
    basicAuth: false
    isDefault: true
```

### Dashboards

Import by ID from grafana.com:

```yaml
grafana_dashboards:
  - dashboard_id: 1860
    revision_id: 4
    datasource: prometheus
```

Or place JSON files in the `grafana_dashboards_dir` local directory and they will be imported automatically.

### Playbook example

```yaml
- name: management playbook
  hosts: mg_managements
  roles:
    - role: bluebanquise.infrastructure.prometheus
    - role: bluebanquise.infrastructure.grafana
      vars:
        grafana_port: 3000
        grafana_security:
          admin_user: admin
          admin_password: mysecretpassword
        grafana_plugins:
          - raintank-worldping-app
        grafana_dashboards:
          - dashboard_id: 4323
            revision_id: 3
            datasource: prometheus
        grafana_datasources:
          - name: prometheus
            type: prometheus
            access: proxy
            url: http://127.0.0.1:9090
            isDefault: true
```

### Installing a specific version

To install a pinned version from system repositories:

```bash
ansible-playbook /etc/bluebanquise/playbooks/grafana.yml --limit management1 \
  -e "grafana_packages_to_install=['grafana-10.4.0']"
```

To install directly from grafana.com (bypassing system repositories):

```bash
ansible-playbook /etc/bluebanquise/playbooks/grafana.yml --limit management1 \
  -e "grafana_install_oss_packages=true grafana_packages_to_install=['grafana-10.4.0-1.x86_64.rpm']"
```

Check the [download page](https://grafana.com/grafana/download?edition=oss) for the filename matching your OS.

Note: if you add dashboards, these settings check that datasources are accessible. Apply datasource-providing roles (e.g. prometheus) before grafana.
