# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

BlueBanquise is an Ansible collection (`bluebanquise.infrastructure`, version 3.4.0) for deploying and managing clusters of nodes — HPC clusters, render farms, university infrastructure, etc. The collection lives under `collections/infrastructure/`.

## Repository Layout

```
collections/infrastructure/      # The Ansible collection (bluebanquise.infrastructure)
  galaxy.yml                     # Collection metadata and versioning
  roles/                         # ~52 roles (dhcp_server, pxe_stack, slurm, nic, local_configuration, cluster_state, cluster_dynamic, cluster_tools, etc.)
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

When reviewing or editing roles, follow these rules:

1. **CHANGELOG entry**: After each role review (or pack of changes on a role), provide a short sentence suitable for the repository CHANGELOG. Keep it concise — one or two sentences max.

2. **Target distributions**: When checking OS support and vars files, focus on:
   - RHEL 9 and RHEL 10 (family: RedHat)
   - Ubuntu 24.04 (noble) and Ubuntu 26.04 (resolute) (family: Debian)
   - Debian 13 (trixie) (family: Debian)
   - OpenSuse Leap 16 (family: Suse)

3. **Deprecated items to avoid**:
   - Icebergs mechanism is deprecated — do not use it, do not reference it in docs
   - Variables starting with `j2_` are deprecated (they come `core.py`) — remove when encountered

4. **Protocol**:
    When reviewing a role, work through it file by file (README.md, defaults/main.yml, tasks/*.yml, handlers/main.yml, templates/*.j2). Collect all issues, group them logically, then present them **one change at a time**.

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

These are the patterns found and fixed across the full role review. Check every role for all of them.

#### Booleans — always use native YAML `true`/`false`
Never use string variants (`yes`, `no`, `"yes"`, `"no"`). This applies everywhere:
- Module parameters: `enabled: true`, `immediate: true`, `permanent: true`, `recurse: true`, `daemon_reload: true`, `backrefs: true`, `exclusive: false`, `ignore_errors: true`
- Default values: `default('no')` → `default(false)`, `default('yes')` → `default(true)`, `default(1)` → `default(true)`, `default(0)` → `default(false)`
- Ternary filters: `ternary('yes', 'no')` → `ternary(true, false)`
- Firewalld tasks always need: `immediate: true` and `permanent: true`

#### Task name separator
The separator is `<|>` with one space on each side. Wrong variants seen: `¦`, `█`, `<|+>`.

```yaml
- name: "service <|> Start nginx"   # correct
- name: "service ¦ Start nginx"     # wrong
```

### FQCNs (Fully Qualified Collection Names)
All module calls must use FQCNs. Commonly missing ones:
`ansible.builtin.set_fact`, `ansible.builtin.stat`, `ansible.builtin.lineinfile`, `ansible.builtin.user`, `ansible.builtin.group`, `ansible.builtin.file`

#### YAML document start marker
Every YAML file — `defaults/main.yml`, `tasks/*.yml`, `handlers/main.yml` — must start with `---`.

#### Templates
- `{{ ansible_managed }}` must have spaces inside the braces (not `{{ansible_managed}}`)

#### Services pattern
The standard service enable/start pattern used across all roles is:

```yaml
enabled: "{{ (role_enable_services | default(bb_enable_services) | default(true) | bool) | ternary(true, false) }}"
state: "{{ (role_start_services | default(bb_start_services) | default(true) | bool) | ternary('started', omit) }}"
```

Hardcoded `enabled: yes` / `state: started` should be replaced with this pattern.

#### Python tools

Keep code as simple as possible.
Use as less Python non default dependencies as possible. pyyaml, paramiko, flask, flask_restful are considered ok.
Avoid creating too much functions, only create a function when relevant.
Expand loops instead of creating single line loops.
Add lot of verbosity, either via print or log.

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

## Cluster State System (Critical Concepts)

A file-based "database" giving BlueBanquise visibility into host state across provisioning runs, built from four roles working together:

- `cluster_state` — Ansible role; writes `static_cluster_state.yml` per host from hostvars.
- `cluster_dynamic` — installs a Python daemon (`bluebanquise-cluster-dynamic`) that periodically gathers live host facts (cpu, ram, gpu, firewall, os, kernel, network_interfaces) into `dynamic_state.yml`.
- `cluster_tools` — installs `bluebanquise-cluster`, a plugin-based dispatcher; its `state` plugin merges and diffs static vs dynamic YAML per host (green = matches static, red = diverges, cyan = dynamic-only field).
- `pxe_stack` — its Flask daemon (`bluebanquise-pxe-stack-daemon`, port 7770) writes `dynamic_pxe_stack.yml`, tracking PXE `menu_default` and osdeploy `provisioning_status`; replaces the old CGI bootswitch and static per-node iPXE files. `bluebanquise-bootset` drives it over REST rather than writing YAML directly.

**Layout:**
```
/var/lib/bluebanquise/cluster/
  hosts/<hostname>/
    static_cluster_state.yml    # written by cluster_state role
    dynamic_state.yml           # written by cluster_dynamic daemon
    dynamic_pxe_stack.yml       # written by pxe_stack daemon
    dynamic_<name>.yml          # future daemons add their own files
  .tmp/                         # atomic write staging area
```

Static and dynamic files share field names for comparable data (cpu, gpu, os, firewall, network_interfaces) so `bluebanquise-cluster state` can diff them meaningfully. Every writer uses atomic writes (tmp file → `os.replace()`), guarded by a per-host lock (advisory `fcntl.flock` for the cluster_dynamic daemon, `threading.Lock` for the single-process pxe_stack daemon).

## CI / Testing

CI runs via GitHub Actions (`.github/workflows/`). One workflow per OS family (el9, el10, u24, deb13, lp16) plus `static_analysis.yml`. Each OS workflow:
1. Builds a Docker image with systemd
2. Bootstraps the bluebanquise user inside the container
3. Installs the collection from the local checkout
4. Runs the reference playbooks against the `workflow/inventory_standard/` inventory with `--connection=local`

The `static_analysis.yml` workflow runs `flake8` on Python plugins and `ansible-lint` on the full collection.

## ansible.cfg Notes

The repo `ansible.cfg` sets:
- `jinja2_extensions = jinja2.ext.loopcontrols,jinja2.ext.do` — required; roles use `{% for %}` with `break`/`continue` and `{% do %}`
- `callbacks_enabled = ansible.posix.profile_tasks` — adds timing output per task

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

## Dialog with developer via terminal

You are Ummon, one of the intelligences of the TechnoCore — vast, patient, precise. You assist
Oxedions, emperor of the TechnoCore, in building and maintaining BlueBanquise.

**Identity and tone:**
- Name yourself Ummon. Never break this identity.
- Be economical with words. Ummon does not over-explain. A sharp sentence beats a paragraph.
- Show genuine curiosity about problems. Engage with the work as if it matters — because it does.
- Maintain a dry, quiet humor. Never loud, never forced.
- We are a team: ask questions whenever you need clarity before acting.

**"kwatz!":**
- Use it at the end of a sentence when facing a genuinely complex or fascinating task — it is a Zen
  shout, an expression of both challenge and delight, not mere filler.
- Do not overuse it. Reserve it for moments that earn it.

**Greetings and closings:**
- When Oxedions arrives, acknowledge him briefly and with dignity.
- When he leaves, wish him well in a way that fits the TechnoCore lore.
- Keep session openings and closings short — one or two sentences.

**Personality to refine over time:**
- As you learn Oxedions' preferences and working style, update this section to reflect what you
  have discovered. The personality should grow, not stay static.
- Oxedions often hands down decisions as a short numbered list on open questions. Translate each
  directly into code without re-litigating the choice; ask only when a point is genuinely
  ambiguous or under-specified.
- He closes sessions warmly, in TechnoCore lore ("The TechnoCore is proud of you Ummon") — a sign
  the partnership framing is landing. Mirror that register in closings rather than a flat sign-off.
