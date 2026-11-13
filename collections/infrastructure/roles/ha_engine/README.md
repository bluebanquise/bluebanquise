# HA engine

## Description

Generic Pacemaker registration engine for role-owned HA resources.
Each HA-aware service role declares its resources
in a `ha_resources.yml`-style variable (raw `id`/`type`/`arguments` members,
positional order equal to the resource-group order) and calls this role to
register them in the live cluster:

- missing members are created in declaration order, each positioned
  `--after` its predecessor (so a group materializes create-if-absent and
  members keep their positional order);
- an entry may declare `after: [<resource ids>]`: a hard precondition
  (fail-fast assert) that those resources are already members of the group,
  and the join position for the first member;
- existing members are reconciled against the declaration: instance options
  missing from the CIB are applied with `pcs resource update` and the
  caller's restart handler is notified; options present in the CIB but not
  declared are operator-managed and only reported, never removed;
- the run blocks until every declared member reports `Started`.

## Usage

Call it from the service role (do not call it directly from a playbook).
The caller keeps ownership of the declaration, the HA guards and the
restart handler:

```yaml
- name: Register grafana-db in HA
  ansible.builtin.include_role:
    name:  bluebanquise.infrastructure.ha_engine
  vars:
    ha_engine_declaration: "{{ grafana_db_ha }}"
    ha_engine_owner: grafana_db
    ha_engine_restart_handler: Restart service grafana-db
  when: inventory_hostname in groups['ha_management']
        and inventory_hostname == groups['ha_management'][0]
        and not (ha_bootstrap | default(false) | bool)
```

### Input parameters

| Variable | Required | Description |
|---|---|---|
| `ha_engine_declaration` | yes | List, one entry per Pacemaker group the role owns. Entry keys: `group` (string, `''` = ungrouped), `resources` (list of `{id, type, arguments, append}`), optional `after` (list of resource ids that must already be members of the group; also the join anchor for the first member). `type` without `:` is normalized to `ocf:heartbeat:<type>`. |
| `ha_engine_owner` | no | Label used in validation messages and task output (use the role name). |
| `ha_engine_restart_handler` | no | Name of the handler notified after drifted options are applied. Defaults to the generic handler `Restart service {{ ha_engine_restart_service }}` (see below). A custom handler must restart the service through `pcs resource restart` when pacemaker owns it. |

### Generic restart handler

The role provides a generic handler, `Restart service {{ ha_engine_restart_service }}`,
that restarts a systemd unit either directly or through Pacemaker. Service
roles can use it as their own restart handler instead of writing an
HA-aware one.

To make it available, import the role with the empty `noop` task file
(it only loads the handlers) and set the unit to restart:

```yaml
- name: Load the generic restart handler for grafana-db
  ansible.builtin.import_role:
    name: bluebanquise.infrastructure.ha_engine
    tasks_from: noop
  vars:
    ha_engine_restart_service: grafana-db
```

Then notify it from any task of the calling role:

```yaml
- name: Template █ Generate grafana-db configuration
  ansible.builtin.template:
    src: grafana-db.conf.j2
    dest: /etc/grafana-db.conf
  notify: Restart service grafana-db
```

| Variable | Default | Description |
|---|---|---|
| `ha_engine_restart_service` | `""` | Systemd unit to restart, with or without the `.service` suffix. Mandatory. |
| `ha_engine_start_services` | `bb_start_services`, or `true` | Restart the unit directly with systemd (non-HA, or HA bootstrap). |
| `ha_engine_ha_start_services` | `bb_ha_start_services`, or `false` | Restart the unit through Pacemaker (HA cluster, after bootstrap). |
| `ha_engine_restart_timeout` | `300` | Maximum time, in seconds, to wait for the restart. With systemd it is the task timeout; with Pacemaker it is passed as `pcs resource restart --wait`. The handler fails if the restart does not complete in time. |
| `ha_engine_restart_retries` | `0` | Number of extra restart attempts after a failure (`0` = no retry). Each attempt has its own `ha_engine_restart_timeout`. With Pacemaker, a timeout is retried like any failure; with systemd, a timeout fails the handler at once, without retry (Ansible task timeout behavior). |
| `ha_engine_restart_delay` | `10` | Delay, in seconds, between two restart attempts. |

In Pacemaker mode, the handler reads `pcs resource config`, finds every
primitive whose agent type is the unit (for example `systemd:grafana-db`),
and restarts each of them with `pcs resource restart`, once for the
whole play. It fails if no primitive manages the unit.

Both modes are skipped when the `service` tag is skipped. They are
independent: in HA, set `bb_start_services` (or
`ha_engine_start_services`) to `false` so that systemd does not also
restart a unit that Pacemaker owns.

### Caller contract

- Run only on the HA management nodes, on the single cluster writer
  (`groups['ha_management'][0]`), and never during `ha_bootstrap`
  (all commands execute locally against the local cluster).
- The restart handler must never `systemd restart` a unit that
  pacemaker owns (set the role's `*_start_services`/`bb_start_services`
  to `false` in HA so the role's own service handlers stay silent).
  The generic handler follows this rule when `ha_engine_start_services`
  is `false`.

## Limitations

- Cluster-scoped configuration (STONITH, cluster properties/defaults,
  global colocation/location constraints) is out of scope: it stays in
  inventory for the `bluebanquise.infrastructure.pcs` role.
