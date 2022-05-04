# Grafana

## Description

This role deploys grafana on the host.
It allows to configure:
- many options found in grafana.ini
- dashboards
- plugins
- LDAP connection
- etc.

## Instructions

Grafana is available by default at `http://localhost:3000`.

Please continue reading if you want advanced options to modify the default behovior.

## Requirements

- Ansible >= 2.7 (It might work on previous versions, but we cannot guarantee it)
- libselinux-python on deployer host (only when deployer machine has SELinux)
- grafana >= 5.1
- jmespath on deployer machine. If you are using Ansible from a Python virtualenv, install *jmespath* to the same virtualenv via pip.

## Role Variables

All variables which can be overridden are stored in [defaults/main.yml](defaults/main.yml) file as well as in table below.

| Name                               | Default Value | Description                        |
| -----------------------------------| ------------- | -----------------------------------|
| `grafana_provisioning_synced`      | false            | Ensure no previously provisioned dashboards are kept if not referenced anymore. |
| `grafana_instance`                 | {{ ansible_fqdn \| default(ansible_host) \| default(inventory_hostname) }} | Grafana instance name |
| `grafana_logs_dir`                 | /var/log/grafana | Path to logs directory |
| `grafana_data_dir`                 | /var/lib/grafana | Path to database directory |
| `grafana_address`                  | 0.0.0.0 | Address on which grafana listens |
| `grafana_port`                     | 3000 | port on which grafana listens |
| `grafana_cap_net_bind_service`     | false | Enables the use of ports below 1024 without root privileges by leveraging the 'capabilities' of the linux kernel. read: http://man7.org/linux/man-pages/man7/capabilities.7.html |
| `grafana_url`                      | "http://{{ grafana_address }}:{{ grafana_port }}" | Full URL used to access Grafana from a web browser |
| `grafana_api_url`                  | "{{ grafana_url }}" | URL used for API calls in provisioning if different from public URL. See [this issue](https://github.com/cloudalchemy/ansible-grafana/issues/70). |
| `grafana_domain`                   | "{{ ansible_fqdn \| default(ansible_host) \| default('localhost') }}" | setting is only used in as a part of the `root_url` option. Useful when using GitHub or Google OAuth |
| `grafana_server`                   | { protocol: http, enforce_domain: false, socket: "", cert_key: "", cert_file: "", enable_gzip: false, static_root_path: public, router_logging: false } | [server](http://docs.grafana.org/installation/configuration/#server) configuration section |
| `grafana_security`                 | { admin_user: admin, admin_password: "" } | [security](http://docs.grafana.org/installation/configuration/#security) configuration section |
| `grafana_database`                 | { type: sqlite3 } | [database](http://docs.grafana.org/installation/configuration/#database) configuration section |
| `grafana_welcome_email_on_sign_up` | false | Send welcome email after signing up |
| `grafana_users`                    | { allow_sign_up: false, auto_assign_org_role: Viewer, default_theme: dark } | [users](http://docs.grafana.org/installation/configuration/#users) configuration section |
| `grafana_auth`                     | {} | [authorization](http://docs.grafana.org/installation/configuration/#auth) configuration section |
| `grafana_ldap`                     | {} | [ldap](http://docs.grafana.org/installation/ldap/) configuration section. group_mappings are expanded, see defaults for example |
| `grafana_session`                  | {} | [session](http://docs.grafana.org/installation/configuration/#session) management configuration section |
| `grafana_analytics`                | {} | Google [analytics](http://docs.grafana.org/installation/configuration/#analytics) configuration section |
| `grafana_smtp`                     | {} | [smtp](http://docs.grafana.org/installation/configuration/#smtp) configuration section |
| `grafana_alerting`                 | {} | [alerting](http://docs.grafana.org/installation/configuration/#alerting) configuration section |
| `grafana_log`                      | {} | [log](http://docs.grafana.org/installation/configuration/#log) configuration section |
| `grafana_metrics`                  | {} | [metrics](http://docs.grafana.org/installation/configuration/#metrics) configuration section |
| `grafana_tracing`                  | {} | [tracing](http://docs.grafana.org/installation/configuration/#tracing) configuration section |
| `grafana_snapshots`                | {} | [snapshots](http://docs.grafana.org/installation/configuration/#snapshots) configuration section |
| `grafana_image_storage`            | {} | [image storage](http://docs.grafana.org/installation/configuration/#external-image-storage) configuration section |
| `grafana_dashboards`               | [] | List of dashboards which should be imported |
| `grafana_dashboards_dir`           | "dashboards" | Path to a local directory containing dashboards files in `json` format |
| `grafana_datasources`              | [] | List of datasources which should be configured |
| `grafana_environment`              | {} | Optional Environment param for Grafana installation, useful ie for setting http_proxy |
| `grafana_plugins`                  | [] |  List of Grafana plugins which should be installed |
| `grafana_user_gid`                 | 984 | grafana user GID |
| `grafana_user_uid`                 | 990 | grafana user UID |
| `grafana_user_home`                | /usr/share/grafana | grafana user HOME |


Security note:

The role is always overwriting the admin password with the one defined in `default/main.yml` file.
For better security, it is advised to put it encoded in this file: [Please refer to Ansible for implementation details](https://docs.ansible.com/ansible/latest/user_guide/vault.html#creating-encrypted-variables)

Datasource example:

```yaml
grafana_datasources:
  - name: prometheus
    type: prometheus
    access: proxy
    url: 'http://{{ prometheus_web_listen_address }}'
    basicAuth: false
```

Dashboards example:

* Import dashboards from `https://grafana.com/api/dashboards` by ID/revision:

```yaml
grafana_dashboards:
  - dashboard_id: 111
    revision_id: 1
    datasource: prometheus
  - ...
```

* Alternatively, you can put dashboard json files directly in the `grafana_dashboards_dir` local directory, and they will be imported.

### Playbook

The UI password is randomly generated by default, in case you want this behovior, just do:

```yaml
- hosts: all
  roles:
    - role: grafana
```

If you want to enforce you own password or update any other variables in defaults/main.yml, you can pass them when calling the role:

```yaml
- name: managements playbook
  hosts: "mg_managements"
  vars:
    start_services: true
    enable_services: true
  roles:
    - role: prometheus
      vars:
        prometheus_server: true
    - role: grafana
      vars:
        grafana_port: 9080
        grafana_security: {admin_user: admin, admin_password: testtest}
        grafana_plugins:
          - raintank-worldping-app
        grafana_dashboards:
          - dashboard_id: '4323'
            revision_id: '3'
            datasource: 'prometheus'
        grafana_datasources:
          - name: "prometheus"
            type: "prometheus"
            access: "proxy"
            url: "http://127.0.0.1:9090"
            isDefault: true
```

If you need to install a specific version of Grafana
```yaml
ansible-playbook /etc/bluebanquise/playbooks/grafana.yml --limit management1 -e"grafana_packages_to_install='grafana-7.2.0'"
```

Note: if you try to add dashboards, the role will alwats at checking if the datasource is accessible. Thus, make sure all datasources are installed before Grafana.

## Changelog

* 2.0.4: Fix log permissions and firewall check. Thiago Cardozo <thiago.cardozo@yahoo.com.br>
* 2.0.3: Update to fully qualified module name. Matthieu Isoard
* 2.0.2: Add OpenSUSE support. Neil Munday <neil@mundayweb.com>
* 2.0.1: Add Ubuntu support. Matthieu Isoard
* 2.0.0: Role enhancements. Matthieu Isoard
* 1.0.0: Role creation. Bruno Travouillon <devel@travouillon.fr>
