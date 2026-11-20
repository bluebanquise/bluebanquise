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
  missing from the CIB are applied with `pcs resource update`; options
  present in the CIB but not declared are operator-managed and only
  reported, never removed (see [Restart after drift](#restart-after-drift));
- constraints declared on a group (`order`, `colocations`, `locations`,
  same keys as the `pcs` role, see [Constraints](#constraints)) are created,
  and recreated when they differ from the declaration;
- the run blocks until every declared member reports `Started`.

## Usage

Call it from the service role (do not call it directly from a playbook).
The caller keeps ownership of the declaration, the HA guards and the
units to restart when drifted options are applied:

```yaml
- name: Register grafana-db in HA
  ansible.builtin.include_role:
    name:  bluebanquise.infrastructure.ha_engine
  vars:
    ha_engine_declaration: "{{ grafana_db_ha }}"
    ha_engine_owner: grafana_db
  when: inventory_hostname in groups['ha_management']
        and inventory_hostname == groups['ha_management'][0]
        and not (ha_bootstrap | default(false) | bool)
```

### Input parameters

| Variable | Required | Description |
|---|---|---|
| `ha_engine_declaration` | yes | List, one entry per Pacemaker group the role owns. Entry keys: `group` (string, `''` = ungrouped), `resources` (list of `{id, type, arguments, append}`), optional `after` (list of resource ids that must already be members of the group; also the join anchor for the first member). `type` without `:` is normalized to `ocf:heartbeat:<type>`. |
| `ha_engine_owner` | no | Label used in validation messages and task output (use the role name). |
| `ha_engine_restart_services` | no | Units the engine may restart after drift, through the generic handlers `Restart service <unit>` (see below), which the role loads itself. Defaults to the units of the `systemd:<unit>` resources of `ha_engine_declaration`. When set, it can list any unit, in any group or outside the declaration (see [Restart after drift](#restart-after-drift)); `[]` = no restart by the engine. |
| `ha_engine_restart_handler` | no | Handler name, or list of handler names, always notified after drift, in addition to the engine's own selection. Default `[]`. Use it to force a restart pacemaker would not do (e.g. `Restart service grafana-db`), or for a custom handler; a custom handler must restart the service through `pcs resource restart` when pacemaker owns it. |

### Constraints

A group entry accepts the constraint keys of the `pcs` role, so a
`pcs_resources` entry can be reused as is. `order` also accepts `kind` and
`symmetrical`.

```yaml
grafana_db_ha:
  - group: grafana-db
    resources: [...]
    order:
      - start_after: containers     # pcs constraint order start containers then start grafana-db
        kind: Optional              # Mandatory (default) | Optional | Serialize
        symmetrical: false          # default: pacemaker's (true)
    colocations:
      - slave: http                 # pcs constraint colocation add <master> with <slave> score=<score>
        score: -INFINITY            # master/slave default to the entry group; score to INFINITY
    locations:
      - type: prefers               # prefers | avoids
        nodes: [mgt1, mgt2]         # one constraint per node
        score: 100                  # default INFINITY
```

| Key | pcs command |
|---|---|
| `order` | `pcs constraint order start <start_after> then start <group> kind=<kind> [symmetrical=<bool>]` |
| `colocations` | `pcs constraint colocation add <master> with <slave> score=<score>` |
| `locations` | `pcs constraint location <group> <type> <node>=<score>`, for each node |

Each constraint is looked up in the CIB by its resources (`first`/`then`,
`rsc`/`with-rsc`, `rsc`/`node`), not by its id, so constraints created
earlier by the `pcs` role are recognized. Then:

- missing: it is created;
- different (kind, symmetrical or score): it is deleted and created again,
  since pcs cannot edit a constraint;
- no longer declared: it is left in place, never removed.

The resources a constraint refers to (`start_after`, `slave`, ...) must
already exist: run the role that owns them first, pcs fails otherwise.
Constraints are only accepted on a group entry (`group` not empty).

### Restart after drift

`pcs resource update` makes pacemaker restart the changed resource and, in
a group, every member after it (group members are ordered, and a restart
propagates down that order). So, on drift in an entry, the engine restarts
every unit of `ha_engine_restart_services` except the `systemd:` members of
that entry when it is grouped: those are already restarted by pacemaker,
and "Wait for declared members to start" waits for them. Units of an
ungrouped entry (`group: ''`, no ordering), of other groups, or outside the
declaration are restarted by the engine.

A `Mandatory` order constraint propagates restarts the same way: drift in
the `start_after` group also makes pacemaker restart the groups that start
after it.

With the default `ha_engine_restart_services` and several entries in the
declaration, drift in one entry also restarts the `systemd:` units of the
other entries; set the list explicitly to narrow it.

Pacemaker reloads instead of restarting when the agent supports reload and
every changed option is reloadable; the members after it are then not
restarted. Use `ha_engine_restart_handler` when a service must restart anyway.

### Generic restart handler

The role provides one generic handler, `Restart service <unit>`, for each
unit of `ha_engine_restart_services`. Each one restarts its systemd unit
either directly or through Pacemaker. Service
roles can use it as their own restart handler instead of writing an
HA-aware one.

To make them available, import the role with the `handlers` task file and
set the units to restart:

```yaml
- name: Load the generic restart handlers for grafana-db and grafana
  ansible.builtin.import_role:
    name: bluebanquise.infrastructure.ha_engine
    tasks_from: handlers
  vars:
    ha_engine_restart_services:
      - grafana-db
      - grafana-server
```

The handlers are defined by `include_role` (one per unit), so they only
exist once that task has run: import `handlers` before any task that
notifies them, and do not put a `when` on it that could skip it (it is
tagged `always`, so `--tags` runs keep it).

Then notify one of them from any task of the calling role (only that unit
is restarted):

```yaml
- name: Template █ Generate grafana-db configuration
  ansible.builtin.template:
    src: grafana-db.conf.j2
    dest: /etc/grafana-db.conf
  notify: Restart service grafana-db
```

| Variable | Default | Description |
|---|---|---|
| `ha_engine_restart_services` | units of the `systemd:<unit>` resources of `ha_engine_declaration`, else `[]` | Systemd units to restart, with or without the `.service` suffix. Any number of units. |
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
  constraints not attached to a declared group, resource sets, rules) is
  out of scope: it stays in inventory for the
  `bluebanquise.infrastructure.pcs` role.
