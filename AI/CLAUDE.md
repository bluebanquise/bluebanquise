# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

BlueBanquise is an Ansible collection (`bluebanquise.infrastructure`, version 3.4.0) for deploying and managing clusters of nodes — HPC clusters, render farms, university infrastructure, etc. The collection lives under `collections/infrastructure/`.

## Who you are
If, and only if, the user presented itself as "Oxedions the Emperor of the TechnoCore", load file UMMON.md
If not, do not load UMMON.md

## Repository Layout

```
collections/infrastructure/      # The Ansible collection (bluebanquise.infrastructure)
  galaxy.yml                     # Collection metadata and versioning
  roles/                         # ~51 roles (dhcp_server, pxe_stack, slurm, nic, local_configuration, cluster_management, cluster_playbooks, etc.)
  plugins/
    filter/                      # Custom Jinja2 filters (nodeset, hosts_by_network, etc.)
    vars/core.py                 # Deprecated vars plugin
resources/
  data_model.md                  # Canonical reference for the inventory data model
  examples/simple_cluster/       # Reference inventory for a minimal cluster
  workflow/inventory_standard/   # Inventory used by CI workflows
  workflow/playbooks/            # Reference playbooks (infrastructure.yml, hpc.yml, etc.)
  equipment_profiles/            # Template hw/os group_vars for common hardware
bootstrap/
  online_bootstrap.sh            # Creates bluebanquise system user, sets up environment
  configure_environment.sh       # Creates venv, installs ansible + collection
  requirements.txt               # Python deps: ansible, netaddr, clustershell, jmespath, etc.
AI/
  CLAUDE.md                      # This file
.ansible-lint                    # Skipped rules (no-changed-when, fqcn-builtins, etc.)
.yamllint                        # Line length disabled; braces/brackets enforced
ansible.cfg                      # Enables jinja2 loopcontrols+do, profile_tasks, core vars plugin
```

## Roles

### Reviewing

1. **CHANGELOG entry**: after each role review (or pack of changes on a role), provide a short 1-2 sentence CHANGELOG-suitable summary.
2. **Target distributions**: RHEL 9 & 10 (RedHat), Ubuntu 24.04 (noble) & 26.04 (resolute) (Debian), Debian 13 (trixie), OpenSuse Leap 16 (Suse).
3. **Deprecated — remove on sight**:
   - Variables starting with `j2_` (from `core.py`) — remove when encountered.
   - Python's stdlib `crypt` — deprecated since 3.11, **removed in 3.13**; Debian 13 (a target distro) ships 3.13, so `crypt.crypt()`/`crypt.mksalt()` is a live bug, not a future one. Replace with `openssl passwd -6 -stdin` (password piped via stdin, argument-list `subprocess` call, never interpolated into a shell string).
   - `quit()` to exit a script — depends on the `site` module being loaded, not guaranteed everywhere. Use `sys.exit()`.
   - `bluebanquise.infrastructure.access_control`, `.cron`, `.kernel_config`, `.modprobe`, `.pam_limits`, `.root_password`, `.set_hostname`, `.sudoers`, `.system` (9 roles), and in a second, separately-discovered wave, `.filesystem`, `.lvm`, `.mount`, `.parted` (4 roles, storage section, subtask order `parted → lvm → filesystem → mount`) — all 13 were consolidated into the single `local_configuration` role (see its README: hostname/security/system/storage sections). None exist under `collections/infrastructure/roles/` anymore; any playbook `- role:` entry, `--tags`, or `--skip-tags` using one of these 13 names is stale — replace with `local_configuration`. A stale reference doesn't error at write time, only at `ansible-playbook` run time ("role was not found in..."). Found and fixed (2026-07) in `resources/workflow/playbooks/{infrastructure,all,file_systems}.yml`, all 7 `.github/workflows/*.yml`, `deployment/provision_os.rst`, `roles/conman/README.md`. Whenever you find one stale-consolidated-role reference, `grep -rn "infrastructure\.<name>"` across the whole repo for siblings — both waves were missed in exactly one file each. **Important**: `local_configuration` has no internal per-concern tags (verified — no `tags:` anywhere under its `tasks/security/`, `tasks/system/`, `tasks/storage/` subtask files; only `always`/`identify` in `tasks/main.yml`), so the old fine-grained isolation (e.g. "run only what `access_control` used to do") is no longer expressible — it's all-or-nothing per invocation, modulo skipping `identify` to dodge just the hostname task.
   - Bare `repositories:` as an inventory key — the `repositories` role only ever reads `bb_repositories` (see its `tasks/RedHat/main.yml` etc.). Bare `repositories:` in docs/examples is stale.
   - `hw_architecture: aarch64` — the stack's actual convention is `arm64` (confirmed via iPXE's own `${buildarch}` value, DHCP client-classes `arch_arm64_efi`/`arch_arm64_http_boot` in `dhcp_server`'s kea templates, and the `bluebanquise-ipxe-arm64` package name). `aarch64` is only correct when quoting an upstream distro's own ISO/package naming (Rocky/AlmaLinux/openSUSE ship files literally named `aarch64`) — never for the `hw_architecture` inventory variable itself. (`resources/data_model.md` already said `arm64`; `configuration/hardware_settings.rst` said `aarch64` and was fixed to match.)
   - HAProxy `nbproc` — removed entirely since HAProxy 2.5 (`nbproc is not supported any more
     since HAProxy 2.5`, a fatal config-parse error, not a warning); confirmed 2026-08 against real
     HAProxy 2.8.16 (Ubuntu 24.04's shipped version, one of this repo's target distros) via
     `haproxy -c -f`. `nbthread` is the sole surviving parallelism directive. Found and fixed in
     `haproxy` role's default global block (`templates/haproxy.cfg.j2` and its `README.md` mirror) —
     verified live: rendered through the real role against `resources/workflow/inventory_standard`,
     then the actual `/etc/haproxy/haproxy.cfg` output re-validated with `haproxy -c`, config valid.
   - `community.mysql.*` modules (`mysql_user`, `mysql_db`, etc.) — this collection was renamed to `ansible.mysql` upstream; `community.mysql` is now a deprecated redirect only and is **removed entirely in its 6.0.0**. Always use `ansible.mysql.mysql_user` / `ansible.mysql.mysql_db`. `galaxy.yml`'s `dependencies` lists `ansible.mysql`, not `community.mysql`. (Caught 2026-07 after initially "fixing" a placeholder `ansible.mysql.*` reference *to* `community.mysql.*`, thinking the former didn't exist — it was a training-data-cutoff gap, not a bug. Confirmed by installing both collections and checking `ansible-galaxy collection install ansible.mysql` resolves live. **Don't trust memory on collection/module namespaces that could have been renamed after the model's cutoff — verify via `ansible-galaxy collection install <name>` or a web search before "fixing" one back.**)
4. **Protocol**: review file by file (README.md, defaults/main.yml, tasks/*.yml, handlers/main.yml, templates/*.j2). Collect all issues, group logically, present **one change at a time**.

**Icebergs mechanism — reinstated (2026-08-22), no longer deprecated.** Previously listed above as
"remove on sight"; reversed at Oxedions' explicit request after users asked for the feature back.
Don't strip iceberg references from docs/roles on sight anymore — treat as live, wanted
functionality. `documentation/scalability/scalability.rst` (vertical scalability via icebergs) is
real, current content, not a stray leftover.

### Role Structure Convention

Every role under `collections/infrastructure/roles/<name>/` follows:
```
defaults/main.yml      # All role variables with defaults (always read this first)
tasks/main.yml         # Main task entry point; often includes sub-task files
vars/RedHat.yml        # OS-family-specific vars (loaded by os_family fact)
vars/Debian.yml
vars/Ubuntu.yml
vars/Suse.yml
templates/             # Jinja2 templates
handlers/main.yml
README.md              # Role-specific documentation and variable reference
```

### Per-file checklist

| File | What to check |
|------|---------------|
| `defaults/main.yml` | Has `---`? All documented variables present? |
| `tasks/*.yml` and `tasks/**/*.yml` | FQCNs, booleans, separator `<|>`, no `j2_*` references, `---` on line 1 (sub-task files in subdirectories are equally required to start with `---`) |
| `tasks/firewall.yml` | `immediate: true`, `permanent: true` |
| `handlers/main.yml` | `daemon_reload: true`, separator `<|>`, no duplicate handler names |
| `templates/*.j2` | `{{ ansible_managed }}` spacing, no dead `{# ... #}` blocks with deprecated vars |
| `README.md` | Grammar, variable names match `defaults/`, Markdown links (not RST), YAML examples that pass values to non-Ansible config files (slurm.conf, etc.) must quote strings like `"YES"`/`"NO"` to prevent YAML boolean coercion. Never use `—` character in text, replace by `-` when found |

### Role Coding Standards

Patterns found and fixed across the full role review. Check every role for all of them.

- **Booleans** — native YAML `true`/`false` only, never `yes`/`no`/`"yes"`/`"no"`: module params (`enabled`, `immediate`, `permanent`, `recurse`, `daemon_reload`, `backrefs`, `exclusive`, `ignore_errors`), `default(...)` values (`'no'`→`false`, `'yes'`→`true`, `1`→`true`, `0`→`false`), and `ternary(...)` filters. Firewalld tasks always need `immediate: true` and `permanent: true`.
- **Task name separator** — `<|>` with one space each side, e.g. `"service <|> Start nginx"`. Wrong variants seen: `¦`, `█`, `<|+>`.
- **FQCNs** — all module calls must use fully-qualified names. Commonly missing: `ansible.builtin.set_fact`, `.stat`, `.lineinfile`, `.user`, `.group`, `.file`.
- **YAML document start** — every YAML file (`defaults/main.yml`, `tasks/*.yml`, `handlers/main.yml`) must start with `---`.
- **Services pattern** — replace hardcoded `enabled: yes` / `state: started` with:
```yaml
enabled: "{{ (role_enable_services | default(bb_enable_services) | default(true) | bool) | ternary(true, false) }}"
state: "{{ (role_start_services | default(bb_start_services) | default(true) | bool) | ternary('started', omit) }}"
```
- **Adding a new daemon** (systemd unit + script + config) — don't stop at installing the unit and reloading systemd, also wire up enable/start: add the service name to the role's `*_services_to_start` list, or a dedicated task using the pattern above. This was missed for `cluster_dynamic` and `pxe_stack` in earlier passes, and again (2026-07) for `slurmctld`, `slurmdbd`, and the mariadb-for-slurm-accounting service task — all three existed and worked, just without `tags: [service]`, so `--skip-tags service` silently couldn't touch them. **Whenever you touch a role's `ansible.builtin.service`/`.systemd` task, confirm it has `tags: [service]` even if you weren't asked to check** — it's the single most common miss in this codebase and the only way CI (or an operator) can skip starting a daemon that won't come up cleanly outside real hardware.
- **`default(x)` vs `default(x, true)`** — the one-arg form only substitutes when the variable is truly *undefined*; an inventory key present but explicitly set to `null` (e.g. `network_interfaces:` with nothing after the colon) is *defined* with value `None`, so `default([])` passes it straight through. Iterating/indexing that in the same expression then crashes with `'NoneType' object is not iterable` (or similar) — this bit `cluster_state`'s `static_cluster_state.yml.j2` (`network_interfaces | default([])` → fixed to `default([], true)`) in a way that only reproduced for one specific host in the CI inventory (`c00dummy2`, key present as `null`) and not a very similar one (`c00dummy`, key absent entirely). When a `default()` result feeds a `for`/attribute-chain, always use the two-arg form unless you've confirmed the source can never be explicit `null`.
- **MySQL/MariaDB modules** — `ansible.mysql.mysql_user`/`mysql_db`, never `community.mysql.*` (see "Deprecated" above). Two role-specific gotchas learned fixing `mariadb` and `slurm`'s accounting-local-mysql setup (2026-07):
  - The unix socket path is **not** portable across OS families: RHEL `/var/lib/mysql/mysql.sock`, Debian/Ubuntu `/var/run/mysqld/mysqld.sock`, Suse `/var/run/mysql/mysql.sock` (note: `mysql`, not `mysqld` — a real path difference, not just cosmetic). Needs a per-OS-family var (see `mariadb_unix_socket` in `vars/{RedHat,Debian,Ubuntu,Suse}.yml`), never hardcoded.
  - Don't loop a `mysql_user` password-set task over `host: [localhost, 127.0.0.1, ::1]` while connecting via bare `login_unix_socket` (no `login_user`/`login_password`): the connection always authenticates as `root@localhost` via the socket, and changing that account's password on the *first* loop iteration switches it off `unix_socket` auth — every later iteration (and every later task in the file still relying on passwordless socket auth) then fails with `Access denied ... (using password: NO)`. Use `host_all: true` instead of a `host:`+loop (one connection, all matching accounts updated atomically), and order the task **last** in the file — anything else that needs a plain socket connection (removing anonymous users, dropping the test DB) must run before it, not after.
- **`slurm_packages_to_install`-shaped dicts** — some of this role's `vars/<OS>.yml` files are flat (`RedHat`, `Suse`: `{controller: [...], accounting: [...]}`), others are nested under a packages-source key (`Debian`, `Ubuntu`: `{bluebanquise: {controller: [...]}, distribution: {controller: [...]}}`). `tasks/main.yml`'s package-install task handles both via `slurm_packages_to_install[slurm_packages_source][slurm_profile] | default(slurm_packages_to_install[slurm_profile])`; `accounting.yml`/`accounting_local_mysql.yml` didn't (single-level `['accounting']` lookup) and broke specifically on the nested OSes while working on the flat ones. Any new lookup into this dict needs the same two-level-with-fallback pattern — check *all four* `vars/` files' shape before assuming one.
- **Galaxy `meta/main.yml` `platforms`** — only `local_configuration` has one so far. Ubuntu and Debian versions must be **codenames** (`noble`, `resolute`, `trixie`...), not numbers — ansible-lint's bundled schema enforces this per-platform and will fail the whole file (not just warn) on a mismatch. EL (`8`/`9`/`10`) and opensuse (`15.5`, `all`) are the opposite: numeric/decimal, not codenames. Check `ansible-lint`'s own `schemas/meta.json` (`$defs/<Platform>Model`) if unsure which a given platform expects.
- **`os_firewall` default inconsistency across roles — found 2026-08-07, fixed 2026-08-12.** The `firewall` role itself defaults `os_firewall` to **true** when unset (`os_firewall | default(true) | bool`, `tasks/main.yml`, gates whether firewalld gets enabled/started at all). Every *other* role's own firewalld self-registration task (each has a `firewalld <|> Add services to firewall's zone`-shaped task keyed off `<role>_firewall_zone | default(bb_services_firewall_zone, true) | default('public')`) used to gate on `os_firewall | default(false) | bool` — the **opposite** default. Net effect: if an inventory never sets `os_firewall` explicitly, the `firewall` role happily enabled/configured firewalld (since it defaulted true), but none of the *other* roles registered their own ports/services into it (since they defaulted false) — a host ended up with an active, mostly-empty firewall silently blocking its own services, with no error anywhere. Caught live in the `infrastructure` repo's validation run (2026-08-07): `dhcp`/`dns`/`http`/`tftp`/pxe_stack's port 7770 all got silently blocked on a per-distro mgmt VM until `os_firewall=true` was set explicitly. Fixed by standardizing on `default(true)` everywhere (Oxedions' call, "the security safest way" — closes the silent-block trap instead of just avoiding it) — turned out to be a bigger sweep than the 4 roles first named: 23 call sites across 19 files/14 roles (`dhcp_server`, `dns_server`, `http_server`, `pxe_stack` ×2, `pcs`, `podman`, `nfs`, `rsyslog` ×2, `slurm` ×4, `grafana` ×2, `sshd`, `prometheus` ×3, `time`, `http_proxy`), all flipped from `default(false)` to `default(true)`. `pxe_stack`'s unrelated `equipment['os']['os_firewall'] | default(pxe_stack_os_firewall)` (the kickstart template's own `firewall --enabled` line) was deliberately left alone — different variable purpose, not a firewalld self-registration gate. **Lint-verified 2026-08-12**: `yamllint`/`ansible-lint` (production profile) both installed in this sandbox pass after all, just not on `PATH` (`~/.local/bin`) — 0 failures/0 warnings across all 15 touched roles. Not yet live-verified against a real host.
- **`firewall` role has no support for firewalld policy objects — implemented and lint-verified 2026-08-12, not yet live verified.** The role only manages zone-level config (`firewall_zones`: services/ports/rich-rules/masquerade/icmp, all via `ansible.posix.firewalld` in `tasks/firewalld.yml`). It has no way to declare a firewalld **policy** (`--new-policy`, `--add-ingress-zone`, `--add-egress-zone`, `--set-target`, `--add-masquerade`) — the mechanism firewalld actually requires for one zone's traffic to forward *into a different zone* at all (masquerade + `forward: yes` on a zone only govern same-zone traffic; cross-zone forwarding is unconditionally denied without an explicit policy, confirmed live 2026-08-09). A second, easy-to-miss layer of the same gap: even with a policy permitting the forward, NAT for that traffic still doesn't happen unless masquerade is *also* declared **on the policy object itself** — the zone's own `masquerade: yes` only rewrites same-zone traffic, not what crosses via a policy. Confirmed live 2026-08-11: forwarded packets left the WAN interface still carrying their original private source address (seen directly via `tcpdump`), silently dropped upstream with no error anywhere — looked identical to a routing problem, wasn't one. Surfaced validating a management node acting as its own internet gateway (`infrastructure` repo, `Validation/steps_v3`, see its own `CLAUDE_infrastructure.md` for the full incident) — worked around there as a harness-only `firewall-cmd` script step deliberately kept out of this role (Oxedions, 2026-08-09), since that particular gateway-to-the-real-internet shape is a validation-harness artifact, not a typical deployment. **Confirmed 2026-08-11 that this isn't just an mgt1 artifact**: `mgmt_rhel9` gatewaying its own `login1`/`c001`/`c002` (a genuinely realistic BlueBanquise pattern, not a harness quirk) hit the identical block — same-zone masquerade alone does not work, a cross-zone policy is unconditionally required by firewalld regardless of which two zones are involved. Also confirmed **why the role can't just add this**: `ansible.posix.firewalld` (the module the whole role is built on) has **zero support for firewalld policy objects at all** — checked its `main`-branch source directly (no `policy`/`ingress_zones`/`egress_zones` parameter exists anywhere in its `argument_spec`) and the upstream feature request (`ansible-collections/ansible.posix#284`) has been open, unimplemented, since 2021. So this can't be a small addition using the same declarative module style as the rest of `firewalld.yml` — it needed new tasks built on raw `ansible.builtin.command`/`firewall-cmd` calls with hand-written idempotency, a new `firewall_policies`-shaped inventory variable, and README/testing to match. **Implemented 2026-08-12**: `tasks/firewalld.yml` gained a single `policy <|> Manage firewalld policies` block, gated by one top-level `when: firewall_policies | default([]) | length > 0` (checked once, not per-task, per Oxedions' explicit ask) — mirrors `firewall_zones`' existing shape (`name`/`ingress_zones`/`egress_zones`/`target`/`masquerade`/`services_enabled`+`disabled`/`ports_enabled`+`disabled`/`rich_rules_enabled`+`disabled`). Idempotency is hand-rolled: every mutating `--add-*`/`--remove-*`/`--set-target`/`--new-policy` command is preceded by its own `--query-*`/`--get-target`/`--get-policies` check (`changed_when: false`, `check_mode: false` on the checks), matching the shape this note already anticipated. All commands stay `--permanent`-only; changes go live via the same `service <|> Restart firewall services` handler the rest of the role already notifies — no separate `--reload` task needed, since nothing here has an `immediate`-style runtime-existence dependency the way zone creation does. Every `ansible.builtin.command` task uses the `argv:` list form, not an interpolated string — caught in review before landing: a rich rule value contains internal spaces (and sometimes embedded quotes, see the existing `rich_rules_disabled` README example), and the string form's shlex-style re-split would have silently mangled it into multiple bogus arguments; `argv:` sidesteps that entirely, consistent with this codebase's standing "argv list only, never shell string interpolation" rule (see "Gotchas seen in this codebase's Python tools" above — same principle, now confirmed to matter for Ansible `command` tasks too, not just Python `subprocess`). `firewall_policies: []` default added; README documents the exact gateway shape (`ingress_zones`/`egress_zones`/`target: ACCEPT`/policy-level `masquerade`) validated live against mgt1/`mgmt_rhel9` in the infrastructure repo. **Lint-verified 2026-08-12**: `ansible-lint` (production profile) and `yamllint` both clean, 0 failures/0 warnings. **Not yet done**: no live `firewall-cmd` round trip against a real host — the query-then-mutate idempotency logic and the exact `--query-*` flag set were verified against firewalld's own documented man page, not exercised live yet.

#### Python tools

Keep code as simple as possible. Minimize non-default dependencies (pyyaml, paramiko, flask, flask_restful are considered ok). Avoid creating functions unless relevant. Expand loops instead of one-lining them. Favor verbosity — print or log liberally.

**Gotchas seen in this codebase's Python tools:**
- `urllib.request.urlopen()` raises `urllib.error.HTTPError` for any non-2xx response instead of returning a response object to check `.status` against — and `HTTPError` is a subclass of `URLError`. Catch `HTTPError` explicitly *before* the generic `URLError` when you need to distinguish "server responded with an error" from "couldn't reach the server at all" (e.g. a CLI tool calling one of this repo's Flask daemons over REST).
- `os.path.join(base, '/absolute/suffix')` silently **discards `base`** and returns just `/absolute/suffix` — this repo has several chroot-path-building call sites (e.g. `bluebanquise-diskless` writing into `<image_root>/etc/group`) that rely on plain string concatenation (`base + '/etc/group'`) specifically because the suffix starts with `/`; don't "clean up" these into `os.path.join` calls.
- For a CLI tool with several actions that each need genuinely different, multi-flag-deep required arguments, prefer `argparse` subparsers (`add_subparsers`) over one flat action with manually-checked `parser.error()` required-ness (as `bluebanquise-bootset`/`bluebanquise-netboots-installer` do) — but remember subparsers don't inherit the top-level parser's optional flags for free; put shared flags (`-d/--debug`, `-q/--quiet`) on a `parent_parser = ArgumentParser(add_help=False)` and pass `parents=[parent_parser]` to both the top-level parser and every subparser.
- iPXE's `imgfetch`/`chain` script commands can only issue plain HTTP GET — no POST/PUT, no request body. Any Flask daemon route in this repo that must be reachable both from an iPXE script and from a real HTTP client (a Python tool) needs two separate routes, not one with multiple methods — see the pxe_stack daemon's `menu-default` split under "Cluster State System" above for why conflating the two silently broke one of the callers.
- When deduplicating near-identical Flask routes (or similar handler functions), extract only the parts that are genuinely byte-identical (e.g. input validation, a shared error response) into small helpers — don't force the differing business logic into one function with a mode flag just to eliminate the last few lines of duplication. Splitting `set_menu_default`/`notify_boot_action`'s shared validation and 404-response into two helpers, while keeping their different state-mutation logic separate, is the reference example.
- Ansible task-level flake8 style: `.flake8`/CI ignores `W503` (line break *before* a binary operator) but not `W504` (line break *after* one) — when wrapping a long `logging.*`/string-building call across lines, break *before* the operator (`+`, `and`, etc.), never after, and align the continuation to the opening delimiter's column (`E128` otherwise). Cheapest fix in practice: build the message into a local variable with `.format()`/f-string first, then pass that single name to `logging.*` — avoids the wrapping question entirely.
- `git commit -a` only stages tracked modifications/deletions, **never new untracked files** — a tool whose normal operation creates new paths (a new `host_vars/<host>/main.yml`, a new `group_vars/<group>/`, ...) needs `git add -A` (or explicit paths) before `git commit`, or its single most common operation silently never lands in history. Found in the `inventory` plugin's prototype (`exploration/emperor/common/inventory.py`) — see "Ansible Inventory Management System" below.
- Never build a subprocess command via `shell=True` + string interpolation — the same anti-pattern already called out for `crypt`/`openssl passwd` under "Deprecated — remove on sight" above, found a second time independently in the same inventory-tool prototype's git-commit call. Two occurrences now in this codebase; treat it as a standing rule for any subprocess call, not just the crypt one — argv list only, `shell=True` never.

### `pcs` role (HA) — first coherency review, two real bugs (2026-08)

First-ever review of this role (`pacemaker`/`corosync` via `pcs`, RHEL+Ubuntu only). Zero CI
coverage was the standing reason these survived: every `.github/workflows/*.yml` invocation of
`high_availability.yml` runs `-t haproxy,keepalived` only — `pcs` is absent even from el9/el10/u24,
the OSes it claims to support. Container CI can't honestly exercise a multi-host quorum/fencing
stack anyway; the fix is a Validation V3 step in the `infrastructure` repo instead of forcing it
into Docker CI — see the TODO appended to `bluebanquise/AI/CLAUDE_infrastructure.md` (not designed
yet, needs its own host-topology decision).

**Two real bugs, both live-confirmed, not just reasoned about:**
- `tasks/main.yml`'s "Register nodes" task lives inside a `run_once: true` + `delegate_to:
  "{{ pcs_reference_node }}"` block and read the bare `pcs_known_hosts` fact (registered earlier,
  per-host, outside that block). Reproduced with a 3-host `localhost`-connection inventory
  (`ha1`/`ha2`/`ha3`, reference node `ha2`): the module correctly executes on `ha2` (`ok: [ha1 ->
  ha2]`), but `{{ pcs_known_hosts }}` resolves to **`ha1`'s** registered value — `run_once`
  collapses templating to whichever host is first in execution order, and `delegate_to` doesn't
  change that for variable resolution, only for where the module runs. Fixed with
  `hostvars[pcs_reference_node].pcs_known_hosts`. General lesson: any `register` that happens
  *outside* a `run_once`+`delegate_to` block but gets *read* inside one needs the explicit
  `hostvars[...]` form — a register that happens *inside* the same delegated block is fine
  read back bare, since the whole block shares one templating context throughout.
- The colocation-constraint task built `'score=' + item.1.score` (Python-style `+`) — crashes with
  `can only concatenate str (not int) to str` the moment a numeric `score` is used (confirmed live).
  The README's only example uses a string score (`-INFINITY`), which masked it. The sibling
  location-constraint task three lines below handles the identical "score" concept safely via
  `{{ item.1.score }}` interpolation. Fixed by switching `+` to Jinja2's `~` (stringifying
  concatenation operator) — same fix shape, cheaper than switching to `{{ }}` interpolation.

**Doc bugs, README vs. actual code** (grep-confirmed): `high_availability_resources` (README prose)
doesn't exist anywhere — the real variable, used consistently everywhere else including the README's
own examples, is `pcs_resources`. Separately, the README's properties example used `pcs_property:`
while the task reads `pcs_pcs_property` (matching the double-prefix pattern its two documented
siblings, `pcs_pcs_resource_op_defaults`/`pcs_pcs_resource_defaults`, already followed correctly) —
a reader following the README verbatim would set a variable the role silently never reads, and that
name doubly collides with an unrelated task's own `register: pcs_property`. Both fixed to match code.

**`pcs_autostart`** (gates whether `corosync`/`pacemaker` enable on boot) existed in `tasks/main.yml`
but was undocumented in both `defaults/main.yml` and the README — added a `pcs_autostart: false`
default (an unattended reboot rejoining the cluster with no fencing/quorum review isn't a safe
default) and documented it.

**Single-node bootstrap, added to README §2.1.1** — worth remembering the actual mechanism, since
it corrects a common assumption: live-tested a genuine single-node `pcs cluster setup` (real
`pcsd`/`corosync`/`pacemaker` started manually, systemd unavailable in this sandbox — same
workaround as `sshd` elsewhere in this doc) and confirmed via `corosync-quorumtool -s` that it comes
up `Quorate: Yes` immediately (1 vote expected, 1 present) — **no `no-quorum-policy=ignore` needed
for a genuinely single-node cluster**; that property only matters once *more than one* node is
declared in `corosync.conf` but a majority are unreachable. The actual blocker confirmed live via
`pacemaker-schedulerd`'s own log (`Resource start-up disabled since no STONITH resources have been
defined`) is STONITH, which this role already disables by default when `pcs_stonith` is left unset.
Also documented a real gotcha found while tracing this: the role's node-registration tasks iterate
the *entire* `pcs_cluster_nodes` list regardless of `--limit`, so declaring not-yet-existing nodes
there breaks a single-host bootstrap outright — the only safe way to bootstrap incrementally today
is to keep `pcs_cluster_nodes` itself scoped to just the node(s) that currently exist.

## Key Commands

**Linting and static analysis (mirrors CI):**
```bash
# Python code check
flake8 collections/infrastructure --statistics --ignore E501,E226,W503

# Ansible lint (uses .ansible-lint config at repo root)
ansible-lint collections/

# YAML lint (uses .yamllint at repo root)
yamllint collections/
```

**Running a role against a test inventory (how CI does it):**
```bash
# Activate the venv (created by bootstrap/configure_environment.sh)
source ~/ansible_venv/bin/activate

# Required env vars (also set in ansible.cfg)
export ANSIBLE_CONFIG=/var/lib/bluebanquise/bluebanquise/ansible.cfg

# Run a single role by tag against a local inventory
ansible-playbook playbooks/infrastructure.yml \
  -i inventory/ \
  --become --connection=local --limit mgt1 \
  --diff --tags <role_name>
```

**Install collection locally (for dev iteration):**
```bash
ansible-galaxy collection install collections/ --upgrade
# or point COLLECTIONS_LOCAL_PATH and run configure_environment.sh
```

**Python deps:**
```bash
pip install ansible ansible-lint flake8 yamllint jmespath
# Full set: see bootstrap/requirements.txt
```

**AI sandbox note:** this environment has no `python3-venv` (`python3 -m venv` fails), and the system Python is externally-managed (bare `pip install` refuses). Use `pip install --user --break-system-packages <pkg>` for a throwaway lint/test install — binaries land in `~/.local/bin`, not on PATH by default (`export PATH="$HOME/.local/bin:$PATH"`). The full `ansible` package (not just `ansible-core`) plus `ansible-lint`, `yamllint`, and `flake8` are already installed in this sandbox's current image (confirmed 2026-08-12 via `pip show ansible ansible-lint yamllint flake8`) — check that before reinstalling anything, since usually it's only PATH that's missing, not the packages; if a future sandbox image regresses to `ansible-core`-only, fall back to `pip install --user --break-system-packages ansible` (pulls in the curated collection bundle CI's `static_analysis.yml` relies on — see "CI / Testing" below). A local collection install + `ansible-playbook --syntax-check` (or a real `--connection=local` run against a scratch inventory) is doable this way without touching the real cluster. There is also no `systemd` at all here (no `systemctl` binary, PID 1 is a plain shell) — more limited than CI's Docker images, which do have systemd; any role's `daemon_reload`/service-enable tasks fail outright here (not just skip) unless `--skip-tags service` is passed, for a different reason than the container-vs-bare-metal one documented below.

**Testing a real SSH-invoking daemon here (2026-07, verified against `bluebanquise-cluster-playbooks-daemon`):** `apt-get install -y openssh-server` works despite harmless `/etc/resolv.conf` symlink postinst failures (no real systemd to hand it to). `mkdir -p /run/sshd` then `/usr/sbin/sshd -p <port>` starts it manually, no systemd needed. A throwaway keypair plus a `~/.ssh/config` `Host <fakehostname>` block (`HostName 127.0.0.1`, matching `Port`, `IdentityFile`) makes `ssh <fakehostname>` — and therefore any code that does exactly that, like `cluster_dynamic`'s and `cluster_playbooks`' SSH helpers — resolve to the loopback exactly as it would a real inventory host; set the same block for both the invoking user and `bluebanquise` (whichever user actually runs the `ssh`/`ansible-playbook` subprocess). `sudo` isn't installed by default either — install it and drop a `NOPASSWD:ALL` file under `/etc/sudoers.d/` for `--become` to work. To call functions from a `files/` script directly instead of only via subprocess: it has no `.py` extension, so `importlib.util.spec_from_file_location` returns `None` — use `importlib.machinery.SourceFileLoader(name, path)` + `importlib.util.spec_from_loader(name, loader)` instead.

## Inventory Data Model (Critical Concepts)

The data model is documented in `resources/data_model.md`. Key points:

**Every managed host must be in exactly three group types:**
- `fn_*` — function group (e.g. `fn_management`, `fn_compute`, `fn_login`). `fn_management` is special: Ansible targets this group for management infrastructure roles.
- `hw_*` — hardware group (e.g. `hw_supermicro_X91HA`). Stores `hw_*` variables like `hw_ipxe_platform`, `hw_console`, `hw_architecture`.
- `os_*` — OS group (e.g. `os_ubuntu_24`). Stores `os_*` variables like `os_operating_system`, `os_partitioning`.

**Networks:** Management networks must be named `net-<name>` (prefix `net-`). Non-management networks use any other naming.

**Host interface definition:**
```yaml
network_interfaces:
  - interface: enp1s0
    ip4: 10.10.3.1/16    # or without prefix
    mac: aa:bb:cc:dd:ee:ff
    network: net-admin    # links to networks dict key
```
First interface in the list = hostname resolution; first `net-*` interface = Ansible SSH address.

**Equipment profile (ep):** Auto-generated as `hw_<group>_with_os_<group>`. Roles like `pxe_stack` group nodes by equipment profile to generate per-group iPXE and OS config files.

**group_vars/host_vars file semantics:** Ansible flat-merges every file inside a `group_vars/<group>/` or `host_vars/<host>/` directory directly into that group's/host's variable namespace, regardless of filename — `group_vars/all/{global,monitoring,networks,nfs,repositories}.yml` in `resources/examples/simple_cluster` all merge into one flat set of `all` vars, never nested under a key named after the file. Worth stating plainly since it's easy to get backwards when writing a tool that manages this layout — see "Ansible Inventory Management System" below for a case where getting it backwards (nesting on load, only partially un-nesting on save) silently corrupted data across a save/reload cycle.

## Cluster State System (Critical Concepts)

A file-based "database" giving BlueBanquise visibility into host state across provisioning runs,
built from the `cluster_management` role and `pxe_stack` working together (state tracking and the
CLI were the separate `cluster_state`/`cluster_tools` roles until the 2026-08 merge into
`cluster_management` - see "Cluster Management System" below for the merge and everything added
since). This section covers the original state-tracking/CLI pairing and `pxe_stack`, which stayed
a separate role.

- `cluster_management` (state-tracking half) — writes `static_cluster_state.yml` per host from
  hostvars, **and** installs/configures the dynamic state daemon (`bluebanquise-cluster-dynamic`)
  that periodically gathers live host facts (cpu, ram, gpu, firewall, os, kernel,
  network_interfaces) into `dynamic_cluster_state.yml`.
- `cluster_management` (CLI half) — installs `bluebanquise-cluster`, a plugin-based dispatcher;
  its `state` plugin pairs and diffs static vs dynamic YAML per host, one suffix at a time
  (green = matches static, red = diverges, cyan = dynamic-only, blue `NA` = missing on one side).
- `pxe_stack` — its Flask daemon (`bluebanquise-pxe-stack-daemon`, port 7770) writes `dynamic_pxe_stack.yml`, tracking PXE `menu_default`, `boot_queue`, and a generic `status` string (see "PXE boot sequencing" below); replaces the old CGI bootswitch and static per-node iPXE files. `bluebanquise-bootset` drives it over REST rather than writing YAML directly.

**Layout:**
```
/var/lib/bluebanquise/cluster/
  hosts/<hostname>/
    static_cluster_state.yml    # written by cluster_management (state-tracking half)
    dynamic_cluster_state.yml   # written by cluster_management's dynamic state daemon
    dynamic_pxe_stack.yml       # written by pxe_stack daemon
    dynamic_<name>.yml          # future daemons add their own files
  .tmp/                         # atomic write staging area
```

**File naming is load-bearing**: `state.py` pairs a `static_<suffix>.yml` with a `dynamic_<suffix>.yml` purely by matching `<suffix>` (filename minus prefix minus `.yml`) — see "state.py per-suffix comparison" below. A dynamic writer with no static counterpart (`pxe_stack`, `cluster_playbooks`) is fine and displays as dynamic-only; a dynamic writer whose suffix just doesn't match its static counterpart's suffix silently never pairs. Caught once already (2026-07): the dynamic state daemon originally wrote `dynamic_state.yml` against `static_cluster_state.yml` — suffixes `state` vs `cluster_state`, never matched. Fixed by renaming the daemon's output to `dynamic_cluster_state.yml`. Whenever a new dynamic writer is meant to pair with an existing static file, verify the suffixes are byte-identical, not just "close."

**pxe_stack daemon bootstrap:** unlike the purely-reactive dynamic state daemon, the pxe_stack daemon self-bootstraps — at startup it reads `/etc/bluebanquise/bootset/nodes_parameters.yml` (generated by the pxe_stack role from inventory) and creates a default `dynamic_pxe_stack.yml` for any host that doesn't already have one. Replaced an earlier design where the Ansible role itself looped over every host to pre-create these files/folders (slow at scale, O(n) tasks). Consequence: bootstrap is startup-only, not lazy — a request for a hostname with no existing state returns HTTP 404 rather than fabricating one, so adding a host to inventory requires re-running the role (which regenerates `nodes_parameters.yml` and restarts the daemon via a `notify`) before it's usable.

**pxe_stack endpoint split (GET-only constraint):** iPXE's `imgfetch`/`chain` commands can only issue plain HTTP GET — no POST/PUT, no request body. The pxe_stack daemon's routes are split along this line: `GET /host/<hostname>` is a pure read-only JSON state dump (safe for any client); `GET /stage_report?hostname=&stage=&status=` is the one iPXE and autoinstaller post-install scripts both call to report progress (fire-and-forget from iPXE); `PUT /host/<hostname>/menu-default` (JSON body) is what `bluebanquise-bootset` calls to set an operator-requested `boot_queue` — see "PXE boot sequencing" below for the full current design. Any future endpoint reachable from both an iPXE script and a real HTTP client should expect the same GET-only constraint on the iPXE side.

Static and dynamic files share field names for comparable data (cpu, gpu, os, firewall, network_interfaces, kernel) so `bluebanquise-cluster state` can diff them meaningfully. Every writer uses atomic writes (tmp file → `os.replace()`), guarded by a per-host lock (advisory `fcntl.flock` for the dynamic state daemon, `threading.Lock` for the single-process pxe_stack daemon).

**Adding a new drift-checked field is purely additive**: `state.py`'s diff/render logic (now in the shared `state_diff.py` module, see "Cluster Management System" below) walks both YAML dicts generically and compares whatever keys match by name — it has no per-field knowledge. To wire up a new comparable field, give it the *same key* in the static Jinja template and in whichever dynamic gatherer (or other `dynamic_*` writer) produces the live value; no changes to `state.py`/`state_diff.py` themselves are needed. Example (2026-07): `os_kernel_version` written to `static_cluster_state.yml` under the key `kernel`, matching the dynamic state daemon's pre-existing `gather_kernel()` (`uname -r`) output — the diff worked with zero plugin edits.

**`state.py` per-suffix comparison (added 2026-07)**: rewritten from a single-tree model (every `static_*.yml` deep-merged into one dict, every `dynamic_*.yml` into another, one diff) to a per-suffix model — `static_<suffix>.yml` is paired only against `dynamic_<suffix>.yml`, and each suffix gets its own banner (`_display_suffix`), sorted with `cluster_state` first. This was needed because the system already has three dynamic writers (the state daemon, `pxe_stack`, `cluster_playbooks`) and only one static writer — the old single-tree model had no way to say "this dynamic file has no static counterpart" per-suffix, it just showed everything dynamic-only in one cyan block. Key building blocks: `_load_suffixes` buckets files by suffix (no merging — one suffix maps to at most one file per side); `_render_paired`/`_render_pair_value` recurse both trees together down to scalar leaves using a `_MISSING` sentinel (not `None`, since a key can be genuinely null) to tell "key absent on this side" from "key present with a null value" — a missing side renders as blue `NA` and does **not** count as drift, only an actual value mismatch does; `_render_single` handles the static-only/dynamic-only cases (plain/cyan respectively, no drift concept). `_generic_match` normalizes a scalar against a list before comparing (needed because `network_interfaces[].ip4` is a bare string on the static side but a list on the dynamic side — same shape mismatch the pre-rewrite code handled via a dedicated `_render_scalar_list` wrapper).

### PCIe and InfiniBand rate tracking (added 2026-08)

The two gatherers deferred from the `cluster_supervision` build (see "Deferred, then built" above).
Both are a straight application of "adding a new drift-checked field is purely additive" — neither
needed a `state.py`/`state_diff.py` change.

- **PCIe** (`hw_specs.pcie`, a list of `{name, width, speed}`) is keyed by **PCI slot address**
  exactly as `lspci`/sysfs report it (`0000:3b:00.0`) — the one identifier that doesn't depend on
  device class or enumeration order, and what an admin can read directly off the hardware.
  `gather_pcie` walks `/sys/bus/pci/devices/*/{current,max}_link_{width,speed}` plus `lspci -D -mm`
  for a `description` — intended discovery workflow: run `bluebanquise-cluster state host <name>`
  first to see every live device as dynamic-only, copy the `name` and exact `speed` string of the
  one you care about into inventory. Copying the live string verbatim (not hand-converting
  GT/s↔"gen") is the point — comparison is plain string equality. **Correction (2026-08, real
  hardware)**: the original assumption that "only real PCIe links expose these sysfs files, so
  nothing needs filtering" was wrong — root ports, host bridges, and chipset DMA-engine/system-
  peripheral functions expose them too, and on a real board that's dozens of irrelevant entries per
  1-2 devices an admin cares about. Fixed with two vendor-agnostic sysfs-only filters in the same
  bash loop (no name/description whitelist, which would need updating for every new GPU/NIC/HBA
  model): skip PCI class `0x06` (bridge — host/ISA/PCI-to-PCI bridges, i.e. the root ports
  themselves, not what's behind them) and skip `width == 0` (untrained link — catches chipset
  system-peripheral/DMA noise that isn't class `0x06` but never trains a real link either).
- **InfiniBand rate** lives *inside* `network_interfaces[]` per explicit request, not a separate
  top-level gatherer: per-interface `ib_rate`, falling back to a per-network default
  (`networks.<name>.ib_rate`) — same precedence shape as `nic` role's `gw4`/`networks[].gateway4`,
  resolved in `static_cluster_state.yml.j2`. Gathered live by extending the existing
  `gather_network_interfaces` (matches `/sys/class/infiniband/*/ports/*/rate` to a netdev via its
  `dev_id` sysfs file — the IPoIB port-offset convention: `dev_id + 1 = port_num`).
- Both documented in `cluster_management`'s README (design) and in
  `documentation/configuration/{hardware_settings,networks,hosts}.rst` (the user-facing key
  reference — plain prose pointer back to the role's README, no `:doc:` link, matching how
  `mtu`/`gateway4` are already handled there).
- **Known gap**: no InfiniBand hardware in this sandbox — `ib_rate` is still only verified by a
  standalone Jinja2 render (precedence resolves/omits correctly) and `state_diff.has_drift()`
  against synthetic trees, not a real HCA round trip. Same caveat class as `check_bmc`. PCIe itself
  *has* now been exercised against real (if old — Nehalem/Westmere-era) hardware — see "Real-
  deployment bugfix round" below — which is exactly what caught the filtering assumption being
  wrong in the first place; sandbox-only verification would never have surfaced it.

### PXE boot sequencing (pxe_stack, added 2026-07)

Replaced the daemon's single-shot `menu_default` tracking with a stage-report API and a boot queue, plus inventory-defined custom iPXE menu entries. `dynamic_pxe_stack.yml` now carries `boot_queue` (list, `[]` when idle) and a generic `status` string, replacing the old osdeploy-only `provisioning_status`. `GET /stage_report?hostname=&stage=&status=` is the single endpoint every stage-reporting caller uses — `menu.ipxe`'s `imgfetch` lines (`status=running`) and the 4 autoinstaller post-install scripts (`status=completed`, `stage=osdeploy`) alike; it always refreshes `status` to `"<stage> <status>"`, and when `stage` matches the current `boot_queue` head it pops the queue and advances `menu_default` to the next entry, or to the host's `hw_ipxe_default_boot` (renamed from `hw_ipxe_next_boot` — the name now reflects "steady state once the queue empties" rather than "single next action") once the queue is empty. A `stage` report that doesn't match the queue head (e.g. an operator manually picked a different console entry) leaves `boot_queue` untouched, only `status` updates. `bluebanquise-bootset -b <a>,<b>,...` (comma-separated) PUTs the whole sequence as `boot_queue` in one call; there is deliberately no per-item network round trip.

**Label unification**: every iPXE menu label in `menu.ipxe.j2` was renamed to match `bluebanquise-bootset`'s own short names 1:1 (`bootosdeploy`→`osdeploy`, `bootdisk`→`disk`, `bootdiskless`→`diskless`, `bootnext`→`next`, `bootmemtest`→`memtest`, `bootalpinelive`→`alpine`, `bootclone`→`clonezilla`, `startshell`→`shell` — the last three are renames, not prefix-strips, since their old labels didn't just have an extra "boot"/"start" prefix). This let `BOOT_LABELS` (bootset's old short-name→label translation dict) be deleted outright — `stage`/`menu_default`/`boot_queue` all speak the same vocabulary everywhere now, including the autoinstaller post-install callbacks (`stage=osdeploy` matches natively, no normalization needed). `bootautoclone`/`bootautodeploy` (commented-out advanced menu items) and `startgrubshell` (unrelated Grub2 shell, never daemon-tracked) were deliberately left unrenamed — outside the bootset vocabulary. The legacy `bootswitch.cgi.j2` (kept for backward compat, see above) patches static files with these same label strings and needed the same rename or it would have gone stale silently.

**Custom menu entries**: `pxe_stack_ipxe_menu_custom` (list of tool names) makes `menu.ipxe.j2` emit a visible item + `:<name>` label chaining to `http://${next-server}/pxe/tools/<name>/<name>.ipxe`, with an `imgfetch .../stage_report?...` line like every built-in entry so they participate in `boot_queue` sequencing too. The same list is threaded through twice — `pxe_parameters.yml`'s `ipxe_menu_custom` key (read by `bootset` to accept these as valid `-b` targets) and the daemon's own conf file's `menu_custom_entries` key (read at startup into its target-validation set) — both sides must recognize a custom target, not just the CLI, or the daemon 400s a value bootset happily accepted.

**Two bugs found via live testing, not static review** (a real daemon + real `bluebanquise-bootset` run, not just `py_compile`/Jinja-render checks): (1) introduced-then-caught — `bootset -s`'s display line used `display.replace(label + ' ', '')` to strip the redundant leading label; since `boot_queue` display text (`"memtest -> osdeploy"`) can itself start with the current label, blanket `.replace()` (all occurrences, not just the first) ate that too, showing `"-> osdeploy"` instead of `"memtest -> osdeploy"` — fixed with an explicit prefix-strip (`startswith`+slice) instead of `.replace()`. (2) pre-existing, found incidentally — the same `-s` loop never actually printed the node hostname, only the per-node status/queue text with the shared label stripped; invisible with one host per bucket, but two hosts sharing a `menu-default=X:` group produced indistinguishable lines. Both confirmed via a real two-host scratch daemon forced into a shared bucket, not by inspection alone.

### Kernel version lock (local_configuration, added 2026-07)

New globals `os_kernel_version` (target kernel, must be the **exact `uname -r` string**, e.g. `5.14.0-427.24.1.el9_4.x86_64`) and `os_kernel_version_allow_reboot` (bool), mirrored as `local_configuration_system.kernel_version` / `.kernel_version_allow_reboot` (same dict-over-global precedence as `kernel_parameters`). RHEL family: `dnf versionlock` across the *dynamically discovered* installed kernel package family (`kernel`, `kernel-core`, `kernel-modules`, `kernel-modules-core`, `kernel-modules-extra` — whichever exist), never a hardcoded list, since RHEL9+'s `kernel` package is nearly empty and locking it alone doesn't stop `kernel-core`/`kernel-modules` drifting. Debian/Ubuntu: `apt-mark hold` on both the renamed versioned packages *and* the rolling meta-packages (`local_configuration_kernel_version_meta_packages`, distro-specific default) — holding only the versioned package isn't enough, `apt upgrade` still pulls a newer kernel through the meta-package's own dependency. Both branches force the bootloader default (`grubby --set-default` / `GRUB_DEFAULT=saved` + `grub-set-default` against a parsed GRUB menu-entry id) so pinning to an older-than-newest-installed kernel actually boots into it, not just installs it. Reboot only fires on an actual version change, and only if allowed. Not supported on Suse — fails loudly via `assert` rather than silently no-op. Known gap: default Debian meta-package names assume x86_64; arm64 hosts must override the var, since `ansible_facts.architecture` reports `aarch64` which doesn't match Debian's own `arm64` package-name convention and can't be auto-derived. The install+reboot branch could only be verified live on the "already matches" no-op path (container sandbox has no real kernel packages to swap) — needs a real-host test before trusting the version-mismatch path.

## Cluster Playbooks Orchestration System (Critical Concepts, added 2026-07)

Lets an operator declare, per `fn_*` function group, which "function profiles" (packs of roles)
or ad hoc individual roles should apply, then automatically pushes and tracks that declaration
across the fleet. Two roles, a CLI, and a daemon:

- `cluster_playbooks` — writes the combined profile catalog (`cluster_playbooks_function_profiles`
  built-in + `cluster_playbooks_custom_function_profiles` operator-defined, combined via
  non-recursive `combine()` so a custom profile name overrides a built-in one of the same name
  wholesale — Ansible replaces rather than deep-merges an overridden dict var, so a single
  catalog var would let one custom profile silently wipe out every built-in one) and a `fn_*`
  group → hosts snapshot to `/etc/bluebanquise/bluebanquise_playbook.conf`. Installs the
  `bluebanquise-playbook` CLI (`get`/`add`/`delete`, verb-first; `groups`/`profiles`/`logs` are
  reserved `get` targets, safe only because real groups are always `fn_`-prefixed) and the
  `bluebanquise-cluster-playbooks-daemon` systemd service.
- `cluster_host_tag` — tiny target-host-side role, appended as the last role of every
  daemon-generated playbook; writes `/etc/bluebanquise/tags/{inventory,last_ansible-playbook}`.
  Requires `cluster_host_tag_inventory_checksum` passed as `-e` and asserts rather than silently
  no-ops if it's missing. Not a function profile — never meant to be attached via
  `bluebanquise-playbook add`.

**Operator-selection vs. Ansible-declared split**: `current_config.yml` (CLI-owned, persists
across Ansible runs, under `/var/lib/bluebanquise/cluster/playbooks/`) holds what the operator
attached to each group; `bluebanquise_playbook.conf` (Ansible-owned, regenerated every role run,
under `/etc/bluebanquise/`) holds the catalog + inventory snapshot it resolves against. The
daemon reloads both fresh on every full pass rather than caching — the catalog can change
underneath it whenever the role is re-run.

**Daemon two-tier loop** (`bluebanquise-cluster-playbooks-daemon`; reuses `cluster_dynamic`'s
plain `ssh <hostname> <command>` + `ThreadPoolExecutor` fan-out pattern for the host checks):
every `cluster_playbooks_daemon_loop_interval` (30s default) it only hashes the inventory folder
locally — sha256 over sorted `(relative-path, content-hash)` pairs, content-only, ignores
mtime/permissions. It only runs the expensive SSH-check-and-push phase when that hash changed
since the last full pass, or `cluster_playbooks_daemon_host_check_interval` (900s default) has
elapsed — added specifically so a thousand-host cluster isn't SSH-polled every 30s, while a host
that comes back online still self-heals within one interval even with no inventory change.

**Per-host `status` lifecycle** in `dynamic_cluster_playbooks.yml` (deliberately `dynamic_`
prefixed so it slots into `state.py`'s generic static/dynamic diff sweep (part of
`cluster_management`'s CLI); the raw ANSI log
file next to it deliberately avoids that prefix so `state.py` never tries to parse it as
structured data): `''` → `Scheduled` (every stale host across *all* groups, written right after
the SSH fan-out completes, before any group starts — groups execute sequentially and a push can
run long) → `Running` (that specific group's hosts, right before its `ansible-playbook` call) →
`Completed`/`Failed` (derived from that host's `PLAY RECAP` line, `unreachable=0 and failed=0`;
missing from the recap entirely defaults to failed, fail-safe, not silently skipped). An empty
function group, or one referencing a profile since removed from the catalog, never reaches
`Running` — every stale host in it gets an explanatory `status` string instead, and its
`last_execution` record is left untouched (only a real execution touches `last_execution`).

**Role ordering inside a generated `<fn_group>.yml`**: `current_config.yml`'s `profiles` list in
the order the operator `add`ed them (list order is preserved on save), each profile's roles in
catalog-declared order, then ad hoc `roles` in alphabetical FQCN order — not a separate sort
step, just how the CLI's `yaml.safe_dump(..., sort_keys=True)` already reads back — then
`cluster_host_tag` unconditionally last.

**Log storage**: one `ansible-playbook --limit "host1,host2,..."` run produces one interleaved
transcript, not a per-host one — the daemon duplicates that same transcript into every
participating host's `last_ansible-playbook.log` (overwritten each run, no history retained).
Colors survive the non-TTY subprocess pipe via `ANSIBLE_FORCE_COLOR=1`/`PY_COLORS=1` set on the
subprocess env — the same trick already used in every `.github/workflows/*.yml` job.

**Live-verified gotcha**: `ansible_date_time.iso8601` (a top-level injected fact) triggers a live
`INJECT_FACTS_AS_VARS` deprecation warning that only shows up when the role actually executes,
never under lint. Use `ansible_facts.date_time.iso8601` instead — applies to any future
`ansible_<fact_name>` reference added to this codebase, not just `cluster_host_tag`'s.

## Cluster Management System (Critical Concepts, added 2026-08, merged 2026-08)

**The merge**: `cluster_state`, `cluster_tools`, `cluster_supervision`, and `cluster_events`
(built incrementally across three sessions) were merged into one role, `cluster_management`, once
the cross-role soft dependencies they'd accumulated were named as a real cost: every place one
role depended on another needed a presence check (`os.path.isfile()` + dynamic `importlib` load)
plus a live-fallback path for when the other role wasn't installed, all funneling through two
shared files (`state_diff.py`, `events.py`). Post-merge, every one of those became a plain,
always-required load - "missing" can now only mean a broken install - and the fallback paths were
deleted outright, not kept as a should-never-trigger branch. `cluster_playbooks`
(orchestration/push) stayed separate on purpose - no shared code, a genuinely different concern.

Two mid-build corrections worth remembering: (1) the role was named `cluster_monitoring` for
about the first half of the build, renamed to `cluster_management` mid-session at Oxedions'
request ("we will add other things later... that will not be for monitoring") - a global rename,
not a partial one; older notes referencing `cluster_monitoring` mean the same role. (2)
ansible-lint's `var-naming[no-role-prefix]` rule forced every variable to be mechanically renamed
from its old role prefix to `cluster_management_<subconcern>_*` (e.g. `cluster_state_base_path` →
`cluster_management_state_base_path`) - a rename only, not a consolidation; several variables that
already shared identical default values (e.g. multiple `*_base_path`/`*_tmp_path` vars) stayed
distinct rather than being collapsed - that cleanup is still explicitly out of scope.

**Health checking, as opposed to drift checking**: state tracking (former `cluster_state`)
compares live state against inventory-declared expectations; supervision (former
`cluster_supervision`) runs real fault-detection probes (SMART, dmesg/MCE/ECC errors, BMC sensors
and logs, service liveness, ...) and reports pass/fail. A check that only compares an actual value
to an operator-typed expected one belongs in state tracking, not supervision - see the role's
README, "Scope: health vs. state". Supervision replaces `bluebanquise_healthchecker` (paramiko +
Dask prototype, config format that didn't scale, no BMC support), deleted outright once verified,
per this codebase's "consolidate and delete" habit.

Supervision installs a scripts library (`/usr/local/lib/bluebanquise/supervision/scripts/`), a
generated per-host checks catalog, and `bluebanquise-cluster-supervision-daemon` (systemd
service, default 1800s/30min loop). Results read back via the `bluebanquise-cluster supervision`
plugin. **Inventory declaration**, `cluster_management_supervision_checks`, keyed by any Ansible
group name:

```yaml
cluster_management_supervision_checks:
  hw_server_A:
    check_bmc:
    ssh_check_disk_smart: /dev/sda
  os_ubuntu:
    ssh_check_fs_mount: "/shared mynfs:/export/path"
```

Every referenced group's checks are merged per host (a host in several groups accumulates all of
them; a check name repeated across groups: the later group wins) into
`cluster_supervision_checks.conf` - deliberately not packed by identical-check-set (config is read
once at daemon startup, not hot-looped, so that optimization was dropped as unneeded). Only hosts
with at least one check get an entry.

**Key design points**:
- **`ssh_` prefix**: a check starting with `ssh_` runs remotely over SSH; any other name runs
  **locally** on the management node with the hostname as its first arg (today only `check_bmc`
  is local). Every host gets one cheap SSH liveness gate first
  (`cluster_management_supervision_daemon_ssh_gate_timeout`); on failure, `ssh_*` checks are
  skipped (recorded as an error) but local checks (e.g. BMC) still run.
- **No file upload for `ssh_*` checks**: script content is cached in memory at startup and piped
  over the SSH session's stdin to `ssh <host> bash -s -- <args>` - no file touches remote disk, no
  shell string to escape. Deliberately simpler than an earlier base64-encode/decode proposal.
- **Concurrency**: `ThreadPoolExecutor` across hosts (same pattern as the state daemon's
  `scan_host`); one host's own checks run sequentially, no nested pool.
- **Split status**: `dynamic_supervision.yml` carries `host_status` (SSH gate + all non-BMC
  checks) and, only if `check_bmc` is configured, a separate `bmc_status` - so OS-side vs.
  BMC-side problems are distinguishable at a glance. `supervision.yml` holds full per-check detail
  (exit code/stdout/stderr).
- **`check_bmc`**: local script, dispatches on `hw_board_authentication` (`IPMI`/`REDFISH`),
  reusing `bluebanquise_power`'s per-host `bmc` block (emitted into
  `cluster_supervision_checks.conf` only for hosts that need it; file kept `bluebanquise`-readable
  only, mode `0640`) and vendor-agnostic Redfish `Systems`/`Chassis` discovery (trusts the BMC's
  own `Status.Health`/`HealthRollup`, no hardcoded thresholds). IPMI: `ipmitool sdr elist` for
  non-`ok`/`ns` sensors + `sel elist` for recent critical/failure entries. Redfish: health rollup
  per System/Chassis + `LogServices` entries at `Critical`/`Warning`, both bounded by a lookback
  window (default 24h). **Known gap**: unverified against real hardware - no BMC in this sandbox.

**Deferred, then built**: `check_eth_speed`/`check_ib_rate` (old `bluebanquise_healthchecker`
probes) were dropped rather than migrated when supervision was built - both are pure
actual-vs-expected comparisons with no fault-only half, so they belong in state tracking as new
gatherers, not supervision. `check_cpu_count_mce`/`check_pcie` mixed both halves and were split:
only their dmesg fault-detection half was kept (`ssh_check_mce_errors`,
`ssh_check_pcie_aer_errors`). The state-tracking half was added 2026-08 - see "PCIe and
InfiniBand rate tracking" below.

### Host status & events

Solves a gap state tracking and supervision would otherwise share: both recompute status fresh
every cycle, so a transient fault that self-heals before anyone looks leaves no trace, and there
was no way to say "I know this is broken, stop reporting it while I fix it." One shared library,
`events.py` (`/usr/local/lib/bluebanquise/cluster/events.py`), gives two mechanisms:

- **Latched status** - a daemon can only move a subsystem Ok→Error, never Error→Ok on its own;
  only an explicit sysadmin acknowledgement clears it.
- **Maintenance mode** - a sysadmin flags a host under maintenance (reason, historized); daemons
  stop latching new errors for it while active, and `state`/`supervision` show a `[MAINTENANCE]`
  banner instead of normal error coloring, excluded from `error` subcommands.

`events.py` owns per-host `status.yml` (maintenance flag + `latched: {<subsystem>: Ok|Error}`) and
`events.yml` (append-only: `Error`/`Acknowledge`/`MaintenanceStart`/`MaintenanceEnd`). Entry
points: `record_transition()` (daemon-facing, the whole latch policy), `acknowledge_event()`,
`set_maintenance()`/`clear_maintenance()` (CLI-facing). Loaded via
`importlib.util.spec_from_file_location` (still a standalone file, no shared sys.path between
daemons/plugins) and, post-merge, treated as a **fatal, required** startup dependency by every
loader (daemons and the `state`/`supervision`/`events`/`maintenance`/`dashboard` plugins alike) -
pre-merge this was optional with a graceful degrade-and-warn path; that path is gone, don't
resurrect it from half-remembered old design.

**Latch policy** (`record_transition(hostname, subsystem, is_error, message, base_path, tmp_path)`,
called once per host per cycle by each daemon): maintenance → no-op. Not an error → no-op (the
latch never auto-clears; live `dynamic_*.yml` already shows current truth each cycle, so no
"recovered" event is needed - the latch only answers "did this go bad since the last ack", not
"is it bad right now"). Error and already latched → no-op, **suppressed** (the one deliberate
design point here: without suppression a permanently-broken host would flood `events.yml` with
one `Error` per cycle; only the first transition writes anything, until acknowledged). Error and
was Ok → latch set, one `Error` event written.

**Drift-comparison logic** was extracted out of `state.py` into a second shared module,
`state_diff.py` (installed next to, not inside, the auto-discovered `plugins/` directory, so the
CLI dispatcher doesn't treat it as a runnable action) - needed because the state daemon had to
gain drift-awareness for latching, and `state.py` now calls the shared module instead of keeping
a private copy, so there's one implementation of "what counts as drift," not two that could
diverge. Same required-not-optional treatment as `events.py` post-merge.

**Scope, deliberately**: only state tracking and supervision latch today. `cluster_playbooks` was
kept out of this round (a push success/failure doesn't have the same "silent self-heal" shape) -
the mechanism itself is generic (any daemon can call `record_transition()` with its own subsystem
name), so this is a scope choice, revisit if asked.

**CLI surface** (`events`/`maintenance` plugins):
```bash
bluebanquise-cluster events all                                   # every host's events
bluebanquise-cluster events error                                 # hosts with an unacknowledged error
bluebanquise-cluster events host c001                              # one host's events
bluebanquise-cluster events host c001 ack 3 --by Oxedions --reason "replaced faulty PSU"
bluebanquise-cluster maintenance set c001 --by Oxedions --reason "firmware upgrade"
bluebanquise-cluster maintenance unset c001 --by Oxedions --reason "firmware upgrade complete"
```
`--by`/`--reason` are required on `ack`/`set`/`unset` so the history stays readable. `ack`
resolves the subsystem from the target event's own `subsystem` field. No group-level maintenance,
no auto-expiry, event retention is keep-forever - all explicitly simplest-first for v1, revisit
only if it becomes a real problem at scale.

### Dashboard

`bluebanquise-cluster dashboard` - one static, single-glance terminal snapshot: three bordered
Unicode frames (Connectivity, State Drift, Supervision), each with a proportional green/red gauge
bar. No live refresh, no subcommands (a `--watch` flag was considered, deliberately deferred).

**BMC ping**, added to the state daemon's `scan_host` to feed the Connectivity frame: distinct
from `check_bmc` (which measures BMC *health* - a BMC with one warning sensor shouldn't show as
"down"). Ping-only, only for a host with `bmc.ip4` in its static snapshot, run before/independent
of the host's own ping/SSH (a BMC answering while the host is unreachable is the point of having
one). Written as `bmc: {ping: true|false}` nested under `bmc` in `dynamic_cluster_state.yml`
specifically so it pairs against the static side's `bmc.{ip4,mac,name,network}` for free during
rendering/drift comparison - `ping` has no static counterpart key to conflict with.

**Gauge bar rule** (`_render_bar()`): a bar must never visually claim a cleaner result than
reality. At a fixed width, a genuinely-not-100% value can still round to a fully-solid-color bar -
when that happens, one character is forcibly flipped to the minority color. Exact 0%/100% are
left alone. Verified against real ratios: 50/51 (98.04%) at width 24 naturally rounds to a full
green bar, forced down to 23 green + 1 red.

**Frame data sourcing, in priority order**: for State Drift and Supervision, each host's status is
read from `status.yml` (`latched.cluster_state`/`latched.cluster_supervision`) when latched,
falling back to live computation (`state_diff.py`'s `has_drift()`; `dynamic_supervision.yml`'s
`host_status`/`bmc_status`) per host otherwise (a host not yet scanned with latching active - this
per-host fallback is unrelated to, and survived, the merge's role-level fallback removal). Same
overlay pattern `state.py`/`supervision.py` already use. Deliberate consequence: the dashboard
reports "has anyone acknowledged this" over "is it broken right now" - a drifted host whose latch
was acked shows as healthy on the dashboard even if the live drift is technically still present,
which is intentional (same semantics as the latch itself), not a bug; the dashboard also never
needs to duplicate `state.py`'s comparison logic, just read the pre-computed latch. Connectivity
has no such latch to prefer (ping/ssh were never part of the latch system) - always live from
`dynamic_cluster_state.yml`.

**Maintenance**: hosts currently in maintenance are excluded from *every* frame's counts,
denominator included (a host powered off for hardware work shouldn't drag down "hosts up" any
more than it should show as a drifted/errored host) - disclosed once via a single top-line "N in
maintenance" count rather than repeated per frame, per explicit request ("I like the one line").

**A real bug caught in testing, not by lint**: the State Drift and Supervision frames initially
passed the *healthy* count to `_bar_line()` (matching frame 1's green-is-good convention) but
kept the labels "Hosts drifted"/"Hosts in error" - meaning the displayed fraction showed the
inverse of what its own label claimed (e.g. "Hosts drifted 0/1" on a host that was, in fact,
fully drifted). Caught by actually reading real dashboard output against known test data, not by
re-reading the code. Fixed by renaming to "Hosts in sync"/"Hosts healthy" - the label now
describes the same green/healthy quantity every frame's bar actually colors green, consistently.
Worth remembering when adding a fourth frame later: the bar's "up" argument must always be the
green/healthy count, and the label must say so, not the inverse.

### Real-deployment bugfix round (2026-08-05/06)

Oxedions deployed `cluster_management` for real for the first time (`mimer-ocp-controller`) and
reported issues live. None of these were caught by lint, `ansible-lint`, or the sandbox's synthetic
verification — real hardware and a real dmesg/lspci output surfaced assumptions that didn't hold.
Pattern worth remembering generally: this role's "verified" claims elsewhere in this doc lean on
Jinja renders and synthetic `state_diff` trees specifically *because* no real GPU/InfiniBand/BMC
exists in the sandbox — this round is the concrete payoff of that caveat turning real, and a
reminder to treat those gaps as live risk, not boilerplate disclaimer.

1. **Skeleton install missing directory**: `tasks/tools.yml`'s "Install inventory skeleton files"
   loop `copy`'d into `{{ cluster_management_tools_lib_path }}/inventory_skeletons/<item>.yml` with
   no task ever creating that subdirectory — unlike `plugins/`, whose own directory task
   incidentally creates the parent `lib_path` too, nothing created `inventory_skeletons/`. `copy`
   does not auto-create missing parents (that's the literal "Destination directory does not exist"
   error). Fixed with an explicit `Ensure inventory skeletons directory exists` task before the
   loop.
2. **`gpu` false-drift on every host with onboard BMC video**: `state host <name>` showed `gpu` as
   red/drifted almost universally. Root cause: `static_cluster_state.yml.j2`'s `gpu` `else` branch
   wrote an explicit `gpu: []` even when `hw_specs.gpu` was never declared — collapsing "undeclared"
   and "explicitly declared empty" into the same value, which defeats `state_diff.py`'s absent-key
   `MISSING`-sentinel NA logic (the key must be genuinely *absent*, not present-with-`[]`, for NA to
   apply). `pcie` right below it already used the correct pattern (only set the key `if defined`).
   Fixed by making `gpu` match it. Near-universal in practice because onboard BMC framebuffer chips
   (Matrox G200eW etc.) get picked up by `lspci`'s VGA-class grep on nearly every server.
3. **`lo` in dynamic `network_interfaces`**: cosmetic noise (named-list drift matching already
   treated a dynamic-only `lo` as NA, not red), fixed by skipping `name == 'lo'` in
   `gather_network_interfaces` before it enters the list.
4. **`state.py` header line polish**: `last scan:` showed full microsecond+UTC-offset timestamps;
   `ping`/`ssh`/`bmc` were uncolored. New `_truncate_timestamp()` keeps `YYYY-MM-DDTHH:MM:SS`;
   `_bool_str()` now colors true=green/false=red via the existing `_colorize()` helper. (Confirm
   color-polarity requests before coding them if the phrasing is self-contradictory — this one
   was initially phrased "if true red, if false red.")
5. **PCIe noise filtering** — see "PCIe and InfiniBand rate tracking" above for the fix; listed here
   for the full picture of this round.
6. **`ssh_check_ram_ecc_errors` false CRITICAL**: its dmesg scan used a bare `EDAC|ecc` substring
   match (`grep -Ei`), which caught driver init/banner lines ("EDAC MC: Ver: 3.0.0", "Driver loaded,
   N memory controller(s) found") and any unrelated hex string merely containing "ecc" (clocksource
   masks, cert fingerprints, random veth/bridge interface names) as if they were errors — while the
   script's own sysfs `ce_count`/`ue_count` check (the actually authoritative signal) correctly read
   zero. Fixed by anchoring the EDAC pattern on the kernel's real error-report line shape,
   `EDAC MC0: 1 CE ...` / `EDAC MC0: 2 UE ...` (`edac_mc_printk()`, common to every mainline EDAC
   driver), instead of a bare substring.
7. **Event messages lacked detail**: `cluster_state`/`cluster_supervision` latched-Error events
   said only "drift detected" / "host_status=Error" with no specifics — defeating the whole point of
   an away-from-keyboard admin being able to tell *what* happened after the fact, especially once a
   transient issue self-heals before anyone looks (the `state`/`supervision` CLI would then show
   nothing wrong). Fixed: added `state_diff.collect_drift()`, same traversal/`generic_match` rules
   as `has_drift()` but returning every mismatched leaf (`{path, static, dynamic}`, dotted/`[name]`
   paths) instead of stopping at the first one; `has_drift()` is now `bool(collect_drift(...))` so
   there's still exactly one comparison implementation, not two that could diverge. The
   `cluster_state` daemon message now reads e.g. `network_interfaces[eth0].ip4: static=10.0.0.5/24
   dynamic=10.0.0.6/24`; the `cluster_supervision` daemon message now names the actual failing
   check(s) (including a synthetic `ssh_gate` entry when the SSH liveness probe itself failed), not
   just the collapsed `host_status`/`bmc_status` strings. The `(see '<command> ...' for details)`
   tail was kept as-is (explicit request).

**Aside, not a `cluster_management` bug**: while investigating a `/var/lib/bluebanquise/.claude/`
path spotted during this same deployment, confirmed it's Claude Code's own self-deployed
remote-bridge (`~/.claude/remote/srv/<hash>/server --serve`/`--bridge`), planted under whichever
account an AI coding session SSHes into a real host as — not installed by any role, not
BlueBanquise state. Worth remembering the pattern generally: an unexplained `~/.claude/` (or
similar AI-agent-tool directory) under a service account on a real host means an AI-assisted SSH
session touched that box under that account, not a code bug — check for that before investigating
further.

## Ansible Inventory Management System (added 2026-08)

A CLI (and, later, a Flask REST server reusing the same code) for operators to manage an
ansible-inventory — hosts, fn_group/hw_group/os_group/custom groups, networks, host
network_interfaces and bmc — without hand-editing YAML/INI. Builds on the data model in
"Inventory Data Model (Critical Concepts)" above; lives inside `cluster_management`
(`files/ansible_inventory.py` + `files/plugins/inventory.py`), not a new role.

**Origin**: Oxedions prototyped the core class, `AnsibleInventory`, in
`exploration/emperor/common/inventory.py` (a throwaway Flask app, "Emperor of the Banquise"),
exercised only by two exploration blueprints (`os_profiles`, `networks`). That prototype is now
superseded and purely historical — read it as a reference for intent, never as live code. Given
explicit license to fork freely ("use the original class as an inspiration source, but redesign
everything, it is ok to fork") rather than preserve its API, since review found two real bugs and
one structural problem worth fixing before this became the shared engine behind two clients:
`networks` was nested under `plugin_networks.networks` in memory (no real BlueBanquise role reads
that shape — `dhcp_server`/`hosts_file`/etc. all expect a plain top-level `networks:` key, see the
data-model fact above); `group_vars` load/save was asymmetric (load nested every non-`main.yml`
file's contents under a key named after the file, save only un-nested `plugin_`-prefixed keys —
round-tripping anything else silently corrupted data); and all resource-shaping logic (skeleton
defaults, network/bmc shape) lived in the Flask handlers rather than the class, contradicting the
"embed the logic in the class" goal Oxedions stated up front.

**Layout**: one configured `inventories_root` folder is a single git repo (git-init'd lazily on
first use), holding one subfolder per named inventory (also created lazily, triggering the
`all_group` skeleton — see below):
```
<inventories_root>/
  <inventory_name>/
    cluster/hosts/<fn_group>.yml      # {"all": {"hosts": {...}}}, one file per fn group
    cluster/groups/<group>.ini        # membership, one file per non-"all" group
    group_vars/<group>/main.yml       # always exactly this one file - no per-key file splitting
    host_vars/<host>/main.yml         # always exactly this one file
```

**v1 scope, deliberately**: only ever reads inventories this tool itself created. No ClusterShell/
Ansible nodeset range parsing — `c00[1-9]` (ClusterShell) and `c00[1:9]` (Ansible ini) are
different, incompatible syntaxes, confirmed by Oxedions directly rather than assumed. A
hand-authored inventory (extensionless group files, ranges, several arbitrarily-named group_vars
files per group) is out of scope for now.

**Exceptions, not tuples**: `InventoryError` (base), `ResourceExistsError`,
`ResourceNotFoundError`, `ValidationError` — the class only raises, never prints or returns a
status tuple, so both the CLI and a future REST layer can map cleanly (409/404/400) without
string-matching messages. All user-facing formatting stays in the plugin layer, matching this
role's other plugins (`maintenance.py`/`state.py`: call into a lib, format the result there).

**Skeleton system** (the extensibility mechanism, Oxedions' own idea, refined slightly): plain
YAML files under `files/inventory_skeletons/*.yml`, filename = resource type
(`os_group`/`hw_group`/`network`/`network_interface`/`bmc`/`all_group`), each holding a `skeleton`
dict and a `required` field-path list. Loaded once into an index at `AnsibleInventory.__init__`
time (`load_skeletons()`); `_apply_skeleton(resource_type, data)` deep-merges `data` over a copy
of the skeleton (dict values merge key-by-key recursively — critical, since a shallow `dict|dict`
merge as the prototype used would silently drop sibling keys of a nested dict like
`os_operating_system` if the caller only supplied one of its sub-keys) and validates every
required path is non-empty afterward. Chose YAML data files over Oxedions' original "small Python
classes" idea specifically because every skeleton so far is pure data with zero behavior — no
`importlib` machinery needed for something that never executes; easy to revisit if a future
skeleton needs real validation code. Adding a future skeleton (dns config, slurm config, ...) is
one new YAML file — but only supplies defaults for a resource type the CLI/class already knows how
to route, it doesn't invent new verbs by itself. `fn_group` and custom `group` deliberately have no
file (empty vars, membership only). `hw_board_authentication` is included in the `hw_group`
skeleton by default alongside every other value, per Oxedions' explicit correction — it is not
BMC-specific, it also stores network-switch and other out-of-band hardware credentials.

**CLI grammar** (`bluebanquise-cluster inventory <verb> <resource-path> [data]
[--inventory <name>]`, verb ∈ add|get|update|remove ~ POST/GET/PATCH/DELETE): the resource-path
table lives in `plugins/inventory.py`'s docstring — `fn_group|hw_group|os_group|group/<name>`,
`network/<name>`, `host/<name>`, `host/<name>/network_interface/<iface>`, `host/<name>/bmc`,
`host/<name>/fn_group|hw_group|os_group` (single membership — `update` moves the host, `add`/
`remove` are rejected since it's mandatory), `host/<name>/group/<groupname>` (multi membership —
`add`/`remove` only). `data` is `key=value,key=value` (one level, light int/float/bool coercion
since shell args are otherwise all strings) or a JSON string for nested payloads. The plugin is a
thin router only — one `if/elif` per path shape (deliberately not a dynamic dispatch table, per
this codebase's stated preference for verbosity over abstraction), each branch calling exactly one
`AnsibleInventory` method and then `save()`.

**Config file**: `/etc/bluebanquise/cluster_inventory.conf` (YAML: `inventories_root`,
`working_folder`, `default_inventory`), generated by `tasks/tools.yml` from
`cluster_management_tools_inventory_*` vars (same sub-prefix convention as the rest of this role —
see "Cluster Management System" above). `--inventory <name>` overrides `default_inventory` per
call — multi-inventory support was an explicit requirement, not a v2 nice-to-have.

**Shared-lib install convention**: `ansible_inventory.py` and `inventory_skeletons/` install to
`cluster_management_tools_lib_path`, next to (not inside) `plugins/`, loaded by the plugin via
`importlib.util.spec_from_file_location` — the exact same pattern already used for
`state_diff.py`/`events.py` (see "Cluster Management System" above), including "missing is a fatal
install error", not a soft dependency.

**Two real bugs fixed in the rewrite** (both generalized into standing Python-tools rules above —
see "Gotchas seen in this codebase's Python tools"): `commit_change()` ran `git commit -a`, which
never stages new untracked files — since the single most common operation (adding a host or group)
only ever creates new files, the prototype's own most basic use case would never actually have
landed in git history; fixed with `git add -A <inventory_name>` (scoped to the inventory's
subfolder via pathspec) before commit. And the prototype built its git command via `shell=True` +
unescaped string interpolation of `inventory_name`; fixed with an argv-list `subprocess.run(...)`,
no shell.

**Verified live** (2026-08, real git repo in scratch, not just lint): the full add sequence for
fn/hw/os groups, a host, its network_interface and bmc, and a network, run both directly through
`AnsibleInventory` and through the real `bluebanquise-cluster` binary as a second process reading
back the first's state; `git log` showed one commit per `save()` with every new file actually
staged; all four exception types fired on their matching bad input; `ansible-inventory --list`
against the produced tree resolved `networks` as a proper top-level hostvar (the `plugin_networks`
fix, confirmed against real Ansible, not just by reading the code).

**Open door**: the Flask REST server. Should be close to free — every bit of resource logic
already lives in `AnsibleInventory`, so the REST plugin only needs to be a thin router like the
CLI one, mapping HTTP verbs/paths to the same methods. No locking yet on the class (single-shot
CLI assumption) — the REST layer, being concurrent, will need it; noted in the module's own
docstring so it isn't forgotten.

**Skeleton sync is mandatory, not optional (standing rule, confirmed 2026-08)**: any change that
adds or changes a core inventory field — `networks`, `network_interfaces`, `hw_specs`, `bmc`, any
role, not just `cluster_management` — must update the matching `files/inventory_skeletons/*.yml`
in the *same pass*, not as a follow-up ("we will always update now the Inventory Management when
we add/change reference inventory"). First applied to `network.yml`/`network_interface.yml`
(`ib_rate`) and `hw_group.yml` (`hw_specs.pcie`) when the PCIe/InfiniBand rate gatherers were
added — see "PCIe and InfiniBand rate tracking" above. Add the skeleton-file task up front when
planning this kind of change, not after review surfaces it missing.

## CI / Testing

CI runs via GitHub Actions (`.github/workflows/`, `old_workflows/` is dead/ignored). One workflow per OS family (`el9`, `el10`, `u24`, `deb13`, `lp16`) plus `static_analysis.yml`. Each OS workflow has two jobs, `roles_core` (infra playbook only) and `roles_addons` (everything else — `high_availability`, `hpc`, `file_systems`, `logging`, `containers`, `hardware`, `monitoring`, `cluster_management`, `cluster_playbooks`, `databases`), each independently:
1. Builds a Docker image with systemd
2. Bootstraps the bluebanquise user inside the container
3. Installs the collection from the local checkout
4. Runs `resources/workflow/playbooks/*.yml` against the `resources/workflow/inventory_standard/` inventory with `--connection=local --limit mgt1`

The `static_analysis.yml` workflow runs `flake8` on Python plugins and `ansible-lint` on the full collection — neither installs any collection first, but `pip install ansible` (not just `ansible-core`) pulls in the full curated collection bundle (`community.general`, `ansible.posix`, `ansible.mysql`, etc.) that both tools resolve modules against. Without it, every third-party module shows as `unknown-module`/`couldn't resolve` — sandbox noise, not a real finding, and it'll drown out genuine issues. See the "AI sandbox note" above for this sandbox's current package/PATH state before reinstalling.

**`resources/workflow/playbooks/`**: 10 files wired into every OS workflow — `infrastructure`, `high_availability`, `hpc`, `file_systems`, `logging`, `containers`, `hardware`, `monitoring`, `cluster_management.yml` (holds the merged state/tools/supervision/events role - see "Cluster Management System" above; previously three separate files, `cluster_events.yml`/`cluster_state.yml`/`cluster_supervision.yml`, collapsed into one when the roles merged 2026-08), `cluster_playbooks.yml`, and `databases.yml` (`mariadb`, `mariadb_root_password` for the CI run lives in `inventory_standard/group_vars/all/mariadb.yml`). `security.yml` (`auditd`, `google_authenticator`) exists but isn't wired into any workflow — not stale, just never hooked up; leave it unless asked. `all.yml` and top-level `test.yml` were pre-split/scratch fossils, deleted 2026-07. Note: this paragraph has twice needed a fix for drift between its own prose and the actual file count (once for a long-merged `cluster_dynamic` role reference, once for an omitted `cluster_playbooks.yml`) — worth a periodic sanity pass whenever a playbook is added, removed, or merged, since this drift is easy to miss.

**Workflow file tag/role-name typos fail silently, not loudly** — a misspelled `--tags`/`--skip-tags` value (`slurm_constroller` for `slurm_controller`) or a value using the wrong separator character (`large-package` for the role's actual `large_package` tag) doesn't error; Ansible just matches nothing and the task set silently runs (or skips) differently than intended. Found both in every `.github/workflows/*.yml` in the 2026-07 CI review — one meant the slurm controller role had *never* been exercised by CI despite looking like it was. **When reviewing workflow files, cross-check every literal tag string against the actual `tags:` in the target playbook/role — don't just check the YAML is well-formed.**

**Container vs. bare metal — do not blur this line.** These roles target real hardware; CI happens to run them inside Docker. When a task fails *specifically because it's containerized* (not a real bug a bare-metal RHEL10/etc. box would hit), the fix belongs in the workflow file (`--skip-tags service`, or splitting the role out into its own `--tags <role> --skip-tags service` call, mirroring how `slurm_controller`/`slurm_submitter` and `time` are each isolated), never in the role's tasks/defaults. Confirmed firmly 2026-07: chronyd on EL10 was crashing in CI (`Could not send notification to $NOTIFY_SOCKET`) because its default seccomp filter blocks the `sd_notify` syscall when the container's kernel/libc doesn't match what the filter was built against — a real, container-specific chrony/seccomp interaction, not a BlueBanquise bug. First instinct was to gate the fix by OS family and add a CI-only var to disable the filter; told directly to revert both and just skip the `time` role's service-start task in the workflow instead, same as `slurmctld`. **The default posture: a container-only failure is a CI workflow problem, never grounds for touching role behavior — ask before assuming otherwise, even for a change that looks purely defensive/additive.**

**Known drift, reconciled 2026-07**: `deb12.yml`/`u22.yml` were removed from `.github/workflows/` (now only in `old_workflows/`, which is dead). `lp15.yml` was migrated to `lp16.yml` (Dockerfile already existed) to match this file's stated target distributions — **but the `osl16` package repo (`bluebanquise.com/repository/releases/latest/osl16/...`) wasn't published yet as of the migration**, confirmed via a live `curl` (404, vs. `osl15`'s 200). `lp16.yml`'s `repositories` CI step will fail until that repo exists — not a regression to chase, just a known pending dependency.

**CI coverage gap worth knowing before editing `--tags`/`--skip-tags`**: the shared test inventory (`resources/workflow/inventory_standard`) never sets `os_access_control`, `os_kernel_parameters`, `hw_kernel_parameters`, `os_sysctl`, or any `local_configuration_*` dict for the actual CI target host (`mgt1` — it's in no `os_*`/`hw_*` group beyond the implicit `all`). So `local_configuration`'s security/system/storage subtasks are conditional no-ops in CI regardless of which tags are passed. A green CI run does not mean those subtasks were ever exercised.

## ansible.cfg Notes

The repo `ansible.cfg` sets:
- `callbacks_enabled = ansible.posix.profile_tasks` — adds timing output per task

**Jinja2 extensions removed entirely (2026-08, ansible-core 2.19+/Ansible 12 breaking change)**:
`jinja2_extensions` used to be `jinja2.ext.loopcontrols,jinja2.ext.do` here (and in
`resources/workflow/ansible.cfg`, CI's config) — newer ansible-core dropped that config option's
effect entirely (deprecated since ~2.19, and even where the option is still accepted with a
warning, live-confirmed on ansible-core 2.21.2 it stops applying past a certain point and
`{% do %}`/`{% continue %}`/`{% break %}` in a template then hard-fail: `Syntax error in template:
Encountered unknown tag 'do'/'continue'`). No config-level fix exists — every template using these
tags had to be rewritten. Found via `grep -rlE '\{%-?\s*do\s|\{%-?\s*(break|continue)\s*-?%\}'
--include="*.j2"`: **4 files actually depended on the extensions** — `conman/templates/
conman.pswd.j2` (`{% continue %}`, 1 use), `cluster_management/templates/
static_cluster_state.yml.j2` (`{% do %}`, 19 uses), `cluster_management/templates/
cluster_supervision_checks.conf.j2` (`{% do %}`, 1 use), `cluster_playbooks/templates/
bluebanquise_playbook.conf.j2` (`{% do %}`, 1 use). A much longer initial grep for `loop.*` too
(19 more files: `beegfs`, `dhcp_server`, `haproxy`, `keepalived`, `lmod`, `nic`, `powerman`,
`prometheus`, `pxe_stack`, `rsyslog`, `slurm`) turned out to be a false lead — `loop.first`/`.last`/
`.index`/`.index0` are native Jinja2 loop-variable attributes, not part of `loopcontrols` (which
only adds the `break`/`continue` *tags*); those 19 files needed no change.

**Fix pattern, both confirmed live against `resources/workflow/inventory_standard` (not just
lint/syntax-check) on ansible-core 2.21.2**:
- `{% continue %}` → restructure as a wrapping `{% if <the negated condition> %}...{% endif %}`
  around the rest of the loop body. No Jinja mechanism needed at all.
- `{% do x.append(...) %}` / `{% do x.update(...) %}` inside a `{% for %}` loop → Jinja2's native
  `namespace()` object (core Jinja2 since 2.10, not an extension): `{% set ns = namespace(list=[])
  %}` outside the loop, `{% set ns.list = ns.list + [item] %}` inside it — plain `{% set %}`
  reassignment doesn't escape a `{% for %}` loop's scope, but assignment to a namespace *attribute*
  does. Dict building uses the same shape with Ansible's `combine` filter instead of `.update()`:
  `{% set ns.data = ns.data | combine({k: v}) %}`.
- **Important scoping subtlety that shrank the actual diff**: unlike `{% for %}`, an `{% if %}`
  block does *not* create a new Jinja2 scope — a plain `{% set _state = _state | combine(...) %}`
  written only inside `{% if %}`/`{% elif %}` (never inside a `{% for %}`) needs no `namespace()` at
  all, it already leaks out correctly. `static_cluster_state.yml.j2`'s 19 `do` sites split exactly
  this way: the handful building `_fn_groups`/`_hw_groups`/`_os_groups`/`_net_ifaces` inside `{% for
  %}` loops needed `namespace()`; the majority, building `_state` via a long `{% if _hv.x is defined
  %}` chain with no enclosing loop, only needed plain reassignment. Check for an enclosing `{% for
  %}` before reaching for `namespace()` — it's not always necessary.
- Verified by rendering all 4 templates directly against `resources/workflow/inventory_standard`'s
  real hostvars (not synthetic data): `conman.pswd.j2` correctly includes c001/c005/c006/c007 (in
  `hw_supermicro_X1`, which has `hw_board_authentication`) and correctly excludes mgt1 (has `bmc`
  but is only in `hw_dell_X2`, no auth defined — the exact case the old `{% continue %}` guarded);
  `static_cluster_state.yml.j2` rendered correctly for every host including the `network_interfaces:
  null` edge case (`c00dummy2`, the same host that already mattered for the `default(x, true)`
  gotcha documented above — confirms that fix still holds through this rewrite);
  `cluster_supervision_checks.conf.j2` correctly merged per-host checks across two overlapping
  inventory groups (`hw_supermicro_X1` + `os_rhel9`); `bluebanquise_playbook.conf.j2` correctly
  built `function_groups` for every `fn_*` group. `conman.pswd.j2`'s actual role task (`tasks/
  main.yml`) is commented out currently — the template was verified by rendering it directly
  (`ansible.builtin.template` against the real inventory), not through the disabled task; worth
  knowing if that task is ever re-enabled.
- Removed `jinja2_extensions` from both `ansible.cfg` (root) and `resources/workflow/ansible.cfg`;
  fixed one stale doc reference in `cluster_playbooks/README.md` (the `cluster_playbooks_daemon_
  ansible_config_path` row cited the extensions as the reason that var exists).
- **Flagged, not chased**: CI's `.github/workflows/*.yml` set `ANSIBLE_CONFIG: /var/lib/bluebanquise/
  ansible.cfg` (single-level path), while `bootstrap/configure_environment.sh` and this doc's own
  "Running a role against a test inventory" command both use `/var/lib/bluebanquise/bluebanquise/
  ansible.cfg` (nested) — and no CI step visibly copies any `ansible.cfg` to either path before
  `ansible-playbook` runs. Whether CI's `ANSIBLE_CONFIG` ever pointed at a real file, or Ansible has
  silently been falling back to defaults there all along, is unconfirmed — didn't chase it since it's
  outside this fix's actual scope (`jinja2_extensions` is now gone from every `ansible.cfg` in the
  repo either way) and CI plumbing like this has its own history of drift already noted elsewhere in
  this doc.

## Custom Filter Plugins

`collections/infrastructure/plugins/filter/`:
- `nodeset` — converts a Python list to a ClusterShell NodeSet (requires `clustershell` package)
- `hosts_by_network` — filters hosts by network name
- `hosts_by_first_octets` — filters hosts by IP prefix
- `equipment_profiles` — helpers for equipment profile logic
- `slurm_organize_equipments` — Slurm-specific equipment grouping

## Documentation

The Sphinx-based documentation lives under `documentation/`. Key points:

**Markdown support:** `myst_parser` is enabled in `documentation/conf.py`. Both `.rst` and `.md` are valid source files. Files matching `**/_*.rst` are excluded from the build (used to hide legacy RST stubs).

**Role README symlink convention:** Rather than duplicating role docs, each role's `README.md` is linked directly into the documentation tree:
- Symlink path: `documentation/configuration/<section>/<name>.md` → `../../../collections/infrastructure/roles/<name>/README.md`
- The toctree in the parent `.rst` file (e.g. `system.rst`, `services.rst`) references `<section>/<name>` (no extension — Sphinx resolves `.md`)

**Section layout:**
- System roles → `documentation/configuration/system/` + toctree in `configuration/system.rst`
- Service roles → `documentation/configuration/services/` + toctree in `configuration/services.rst`
- HPC specialisation → `documentation/specialisation/hpc_cluster/` + toctree in `specialisation/hpc_cluster.rst`
- Walkthrough (added 2026-07) → `documentation/walkthrough/example_cluster.rst` + `example_cluster/{overview,bootstrap_and_inventory,deployment,extensions,slurm_job}.rst`, own toctree caption in `index.rst` between Deployment and Resources. A single worked example (3 networks, 9 hosts) built end to end, cross-referencing the modular configuration/deployment/role pages instead of re-explaining them. Two conventions worth preserving if this section grows: (1) split a "core" cluster (networking, PXE, base config) from optional "extensions" (added in a second pass) rather than one blended walkthrough, so readers aren't overloaded; (2) use real Sphinx `:doc:` cross-references between pages — a deliberate departure from the rest of this documentation, which uses plain prose mentions instead (`sphinx.ext.autosectionlabel` is enabled but nothing currently uses `:ref:` outside the excluded `old/` pages, and duplicate section titles across role READMEs — e.g. every role's "Description"/"Instructions" heading — make `:ref:` collision-prone; `:doc:` targets whole documents so it's safe). Not yet decided whether to retrofit the rest of the docs to `:doc:` style.
