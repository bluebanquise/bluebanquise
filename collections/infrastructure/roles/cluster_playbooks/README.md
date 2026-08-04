# cluster_playbooks

## Description

This role writes a catalog of "function profiles" (packs of roles) and a snapshot of the
inventory's `fn_*` function groups to `/etc/bluebanquise/bluebanquise_playbook.conf`, and
installs two tools:

- `bluebanquise-playbook`, a CLI letting an operator associate function profiles, or specific
  individual roles, to function groups, persisting that selection to
  `/var/lib/bluebanquise/cluster/playbooks/current_config.yml`.
- `bluebanquise-cluster-playbooks-daemon`, a systemd service that watches the inventory folder
  and each host's tag file, and automatically generates and runs the playbook needed to bring
  any out-of-date host back in line with `current_config.yml`.

Together they form BlueBanquise's playbook orchestration system: the CLI manages the
*selection* of what should run where, the daemon actually applies it.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Run this role on the management node. It reads from `hostvars`/`groups` and writes files
locally - no SSH connection to target hosts is required.

```yaml
- hosts: fn_management
  roles:
    - bluebanquise.infrastructure.cluster_playbooks
```

Re-run whenever the inventory's `fn_*` groups or the function profile catalog changes, to
refresh `/etc/bluebanquise/bluebanquise_playbook.conf`.

## Output structure

```
/etc/bluebanquise/
  bluebanquise_playbook.conf     # Ansible-owned, regenerated every run
  cluster_playbooks_daemon.conf  # Ansible-owned, daemon settings
/var/lib/bluebanquise/cluster/playbooks/
  current_config.yml             # CLI-owned, persists across Ansible runs
  <fn_group>.yml                 # daemon-generated, one playbook per function group
/var/lib/bluebanquise/cluster/hosts/<hostname>/
  last_ansible-playbook.log      # daemon-owned, raw (colored) output of the last push to this host
  dynamic_cluster_playbooks.yml  # daemon-owned, structured record of the last push / current status
```

### bluebanquise_playbook.conf

```yaml
function_profiles:
  cluster_management:
    bluebanquise.infrastructure.dns_server: {}
    bluebanquise.infrastructure.time:
      vars:
        time_profile: server

function_groups:
  fn_management:
    - mgt1
  fn_workers:
    - c001
    - c002
```

`function_profiles` is `cluster_playbooks_function_profiles` (built-in catalog) combined with
`cluster_playbooks_custom_function_profiles` (operator-defined). If a profile name is defined
in both, the custom definition wins entirely for that profile. `function_groups` lists every
`fn_*` group in the current inventory with its member hosts.

### current_config.yml

Written and maintained by the `bluebanquise-playbook` CLI, not by this role:

```yaml
function_groups:
  fn_workers:
    profiles:
      - nfs_client
    roles:
      community.general.some_role:
        vars:
          foo: bar
```

## bluebanquise-playbook CLI

Installed to `/usr/local/sbin/bluebanquise-playbook`. Run as root or as the `bluebanquise`
system user (needs write access to `cluster_playbooks_storage_path`).

```bash
# List known function groups / function profiles
bluebanquise-playbook get groups
bluebanquise-playbook get profiles

# Show what is currently attached to a group
bluebanquise-playbook get fn_workers

# Attach a function profile to a group
bluebanquise-playbook add fn_workers nfs_client

# Attach a specific role not covered by any function profile, with vars
bluebanquise-playbook add fn_workers community.general.some_role --vars '{"foo": "bar"}'

# Detach a profile or role from a group
bluebanquise-playbook delete fn_workers nfs_client

# Show the raw log of the last playbook execution pushed to a host
bluebanquise-playbook get logs c001
```

Notes:
- `add` auto-detects whether `ITEM` is a known function profile name or a specific role: if it
  matches a profile in the catalog, it is attached as a profile (any `--vars` is ignored and a
  warning printed, since profiles carry their own vars); otherwise it is treated as an ad hoc
  role FQCN, which is always accepted even if unknown to the catalog (e.g. a role from another
  collection, or a custom role).
- Re-`add`ing a role already attached to a group updates its `vars` in place. Re-`add`ing an
  already-attached profile is a no-op.
- `get`/`add`/`delete` all fail with a non-zero exit code if the given group is not a known
  `fn_*` group. `delete` also fails if the given profile or role is not currently attached to
  the group. `get logs` fails clearly if no execution has been recorded yet for that host.
- Pass `-q`/`--quiet` to suppress informational logging and only show warnings/errors, or
  `-v`/`--verbose` to also print debug-level tracing (parsed `--vars`, resolved group entries,
  etc.) when troubleshooting.

## bluebanquise-cluster-playbooks-daemon

Installed to `/usr/local/sbin/bluebanquise-cluster-playbooks-daemon`, runs as a systemd service
(`bluebanquise-cluster-playbooks-daemon.service`) under the `bluebanquise` system user, same as
`cluster_management`'s dynamic state daemon. **Not started automatically in this repo's CI/container
test path** (`--skip-tags service` is used there, same reasoning as `cluster_management`) -
start it manually, or let `bb_start_services` start it on real hardware:

```bash
systemctl start bluebanquise-cluster-playbooks-daemon
systemctl enable bluebanquise-cluster-playbooks-daemon  # optional: start on boot
journalctl -u bluebanquise-cluster-playbooks-daemon -f   # follow its own operational logging
```

### How it works

Each tick (`cluster_playbooks_daemon_loop_interval`, default 30s) it hashes the inventory folder
locally - cheap, no SSH. It only runs the expensive phase - SSH-checking every configured
group's hosts and pushing to stale ones - when that hash has changed since the last full pass,
or `cluster_playbooks_daemon_host_check_interval` (default 900s / 15 minutes) has elapsed since
the last one. This keeps a quiet, large cluster from being SSH-polled every 30 seconds, while
still catching a host that comes back online, or is newly added, within one interval even with
no inventory change.

When a full pass runs, it first computes every stale host across *all* configured groups
(checksum in `/etc/bluebanquise/tags/inventory` on the host doesn't match the current inventory
checksum, or is missing/unreadable) and immediately marks all of them `status: "Scheduled"` in
their `dynamic_cluster_playbooks.yml` - visible before any group has actually started, since
groups execute one at a time and a push can take a long time. Then, for each function group with
at least one stale host:

1. Regenerate `<fn_group>.yml` from `current_config.yml`: the group's `profiles` in the order
   they were added, each profile's roles in catalog order, then its ad hoc `roles` (alphabetical
   FQCN order, since the CLI always saves that way), then `cluster_host_tag` appended last.
2. Mark that group's stale hosts `status: "Running"`, then run
   `ansible-playbook <fn_group>.yml --limit "host1,host2,..."` against just them, with
   `ANSIBLE_FORCE_COLOR=1`/`PY_COLORS=1` set so the captured output keeps its colors (the same
   trick this repo's own CI workflows use).
3. Parse the `PLAY RECAP` to determine per-host success (`unreachable=0 and failed=0`; a host
   missing from the recap entirely is treated as failed).
4. Write the full captured output to every involved host's `last_ansible-playbook.log`
   (overwritten each run - the same batch's output is duplicated across all of them, since one
   `ansible-playbook` run produces one combined transcript, not a per-host one), and update its
   `dynamic_cluster_playbooks.yml` with `status: "Completed"` or `"Failed"`, the execution time,
   exact command, success, and the inventory checksum/path used.

A function group with no profiles or roles configured, or one referencing a profile that's since
been removed from the catalog, isn't run - instead every stale host in that group gets a
`status` explaining why instead of `"Running"`. Full lifecycle per host:
`""` (never touched) -> `"Scheduled"` -> `"Running"` -> `"Completed"`/`"Failed"` -> back to
`"Scheduled"` next time it's found stale again (or the explanatory message, if that's what's
blocking it instead). `last_execution` always reflects the most recent real run and is left
untouched by `"Scheduled"`/`"Running"`/explanatory status updates.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_playbooks_conf_path` | `/etc/bluebanquise/bluebanquise_playbook.conf` | Where the combined function profile catalog and function group snapshot are written |
| `cluster_playbooks_script_path` | `/usr/local/sbin/bluebanquise-playbook` | Install path for the CLI tool |
| `cluster_playbooks_storage_path` | `/var/lib/bluebanquise/cluster/playbooks` | Directory holding `current_config.yml`, owned by the `bluebanquise` system user |
| `cluster_playbooks_function_profiles` | see `defaults/main.yml` | Built-in catalog of function profiles. Not meant to be overridden directly - use `cluster_playbooks_custom_function_profiles` to add or override profiles instead, since Ansible replaces (rather than merges) an overridden dict variable |
| `cluster_playbooks_custom_function_profiles` | `{}` | Operator-defined function profiles, combined on top of the built-in catalog. A profile name defined here overrides the built-in profile of the same name entirely |
| `cluster_playbooks_hosts_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host log/metadata files, shared with `cluster_management` |
| `cluster_playbooks_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Shared temporary directory for atomic writes |
| `cluster_playbooks_log_filename` | `last_ansible-playbook.log` | Per-host filename for the raw captured output of the last push |
| `cluster_playbooks_metadata_filename` | `dynamic_cluster_playbooks.yml` | Per-host filename for the structured execution record |
| `cluster_playbooks_daemon_conf_path` | `/etc/bluebanquise/cluster_playbooks_daemon.conf` | Path to the daemon's generated configuration file |
| `cluster_playbooks_daemon_script_path` | `/usr/local/sbin/bluebanquise-cluster-playbooks-daemon` | Installation path for the daemon script |
| `cluster_playbooks_daemon_loop_interval` | `30` | Seconds between cheap inventory-checksum ticks |
| `cluster_playbooks_daemon_host_check_interval` | `900` | Max seconds between full SSH-check-and-push passes, even without an inventory change |
| `cluster_playbooks_daemon_thread_pool_size` | `100` | Maximum concurrent SSH host-tag checks |
| `cluster_playbooks_daemon_ssh_timeout` | `10` | Seconds before an SSH host-tag check times out |
| `cluster_playbooks_daemon_log_level` | `INFO` | Daemon logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `cluster_playbooks_daemon_inventory_path` | `/var/lib/bluebanquise/inventory` | Inventory folder the daemon hashes and passes to `ansible-playbook -i` |
| `cluster_playbooks_daemon_ansible_playbook_bin` | `/var/lib/bluebanquise/ansible_venv/bin/ansible-playbook` | `ansible-playbook` binary the daemon shells out to |
| `cluster_playbooks_daemon_ansible_config_path` | `/var/lib/bluebanquise/bluebanquise/ansible.cfg` | `ANSIBLE_CONFIG` set on every `ansible-playbook` subprocess (needed for the `jinja2.ext.do`/`loopcontrols` extensions used by other roles' templates) |
| `cluster_playbooks_daemon_host_tag_path` | `/etc/bluebanquise/tags` | Remote path the daemon reads over SSH and passes to `cluster_host_tag` as `cluster_host_tag_path` |
