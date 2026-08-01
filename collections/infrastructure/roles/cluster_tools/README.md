# cluster_tools

## Description

This role installs the `bluebanquise-cluster` command-line tool and its action plugins. The tool provides a unified interface for inspecting and managing cluster state data produced by the `cluster_state` role (static inventory snapshot and dynamic state daemon alike).

Supported distributions (management node): RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Run this role on the management node.

```yaml
- hosts: fn_management
  roles:
    - bluebanquise.infrastructure.cluster_tools
```

## Installed files

| Path | Description |
|------|-------------|
| `/usr/local/sbin/bluebanquise-cluster` | Main dispatcher script |
| `/usr/local/lib/bluebanquise/cluster/plugins/state.py` | State display plugin |
| `/usr/local/lib/bluebanquise/cluster/plugins/supervision.py` | Supervision (health check) display plugin |

## Usage

```
bluebanquise-cluster <action> [args...]
```

If `<action>` does not match any installed plugin, the tool lists available actions and exits.

### state plugin

Reads static inventory snapshots (`static_*.yml`) and live daemon data (`dynamic_*.yml`) from `/var/lib/bluebanquise/cluster/hosts/<hostname>/` and displays them with drift highlighting.

Files are paired **by suffix**: `static_<suffix>.yml` is compared against `dynamic_<suffix>.yml` — nothing is merged across suffixes. Each suffix gets its own banner. `cluster_state` (the primary static+dynamic pair) is always shown first; every other suffix (`pxe_stack`, `cluster_playbooks`, or any future `dynamic_<name>.yml`/`static_<name>.yml` writer) follows, sorted alphabetically.

```bash
# Display one host
bluebanquise-cluster state host c001

# Display all hosts
bluebanquise-cluster state all

# Display only hosts where at least one suffix has drift
bluebanquise-cluster state error
```

**Output format**

For each host, one section is printed per suffix, in one of three shapes:

```
============================ c001 ============================

cluster_state  (last scan: 2026-07-13T10:00:00+00:00  ping: true  ssh: true)
  dynamic / static  (green=match, red=drift, cyan=dynamic-only, blue NA=missing on one side)
hostname: c001 / c001
cpu:
  architecture: x86_64 / x86_64   <- green: matches
  count: 144 / NA                 <- cyan dynamic value: no static counterpart
  model: Intel Xeon... / NA
os:
  distribution: rhel / rhel       <- green: matches
  version: 9.3 / 9.2               <- red: drift detected

pxe_stack
  dynamic only — live daemon data, no static counterpart for this suffix
menu_default: osdeploy            <- cyan: whole suffix is dynamic-only

some_static_only_suffix
  static only — inventory snapshot, no dynamic data for this suffix
some_key: value                   <- uncolored: whole suffix is static-only
```

Every key is rendered as `<dynamic> / <static>`. The suffix banner's title is colored green
(no drift) or red (drift found) when both sides are present; static-only and dynamic-only
banners get a neutral title since there's nothing to compare against.

**Color legend**

| Color | Meaning |
|-------|---------|
| Green | Dynamic value matches static (expected == actual) |
| Red | Dynamic value differs from static (drift detected) |
| Cyan | Field/suffix has no static counterpart (live-only data); static side is uncolored always |
| Blue `NA` | This side has no value at all for this key (missing on one side, not drift) |

**Missing data handling**

- A suffix with only a `static_<suffix>.yml` file: plain uncolored banner, no comparison possible.
- A suffix with only a `dynamic_<suffix>.yml` file: cyan banner, no comparison possible.
- A key present on one side of a paired suffix but not the other: rendered as `<value> / NA` or `NA / <value>`, colored blue on the missing side — this is not counted as drift.
- A host directory with no state files at all: `(no state data)`.

### supervision plugin

Displays health check results produced by the `cluster_supervision` role's daemon (as opposed
to `state`, which compares live state against inventory-declared expectations, `supervision`
runs real health probes - SMART, dmesg/MCE/ECC errors, BMC sensors and logs, etc. - and reports
pass/fail per check).

Reads `supervision.yml` (full per-check detail: exit code, stdout, stderr) and
`dynamic_supervision.yml` (the `host_status`/`bmc_status` summary) from
`/var/lib/bluebanquise/cluster/hosts/<hostname>/`. A host with no `cluster_supervision_checks`
configured, or one the daemon hasn't scanned yet, has neither file - this is reported clearly
rather than treated as an error.

```bash
# Display one host
bluebanquise-cluster supervision host c001

# Display every host that has supervision data
bluebanquise-cluster supervision all

# Display only hosts currently in error (host_status and/or bmc_status not "Ok")
bluebanquise-cluster supervision error
```

**Output format**

```
============================ c001 ============================
host_status: Ok
bmc_status:  Ok
  last scan: 2026-08-01T10:00:00+00:00  ssh gate: ok

check_bmc (exit=0) - OK
  stdout:
    Checking BMC bc001 (10.10.103.1) via IPMI for c001
    OK: BMC bc001 reports no sensor or log issues

ssh_check_disk_smart /dev/sda (exit=0) - OK
  stdout:
    Checking SMART health...
    Checking disk: /dev/sda
    OK: /dev/sda SMART health PASSED
    OK: All disks healthy
```

`host_status` reflects the initial SSH liveness gate plus every non-BMC check; `bmc_status` is
shown only when `check_bmc` is part of that host's configured checks, and reflects that check
alone - so an operator can immediately tell whether a problem is on the OS side or the BMC side.

## Adding new plugins

Create a Python file in `/usr/local/lib/bluebanquise/cluster/plugins/` with a `run(args, config)` function:

```python
def run(args, config):
    base_path = config['base_path']   # /var/lib/bluebanquise/cluster/hosts
    # args = remaining argv after the action name
    ...
```

The plugin is automatically discovered — no registration needed.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_tools_script_path` | `/usr/local/sbin/bluebanquise-cluster` | Installation path for the main script |
| `cluster_tools_plugins_path` | `/usr/local/lib/bluebanquise/cluster/plugins` | Directory where action plugins are installed |
| `cluster_tools_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host state data (passed to plugins) |
