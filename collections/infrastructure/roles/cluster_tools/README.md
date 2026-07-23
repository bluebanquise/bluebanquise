# cluster_tools

## Description

This role installs the `bluebanquise-cluster` command-line tool and its action plugins. The tool provides a unified interface for inspecting and managing cluster state data produced by the `cluster_state` and `cluster_dynamic` roles.

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

## Usage

```
bluebanquise-cluster <action> [args...]
```

If `<action>` does not match any installed plugin, the tool lists available actions and exits.

### state plugin

Reads static inventory snapshots (`static_*.yml`) and live daemon data (`dynamic_*.yml`) from `/var/lib/bluebanquise/cluster/hosts/<hostname>/` and displays them with drift highlighting.

```bash
# Display one host
bluebanquise-cluster state host c001

# Display all hosts
bluebanquise-cluster state all

# Display only hosts where live state differs from inventory
bluebanquise-cluster state error
```

**Output format**

For each host, two sections are printed:

```
==================== c001 =======================

STATIC  (inventory snapshot)
hostname: c001
cpu:
  architecture: x86_64
  sockets: 2
  ...

DYNAMIC  (last scan: 2026-07-13T10:00:00+00:00  ping: true  ssh: true)
hostname: c001          <- green:  matches static
cpu:
  architecture: x86_64  <- green:  matches static
  count: 144            <- cyan:   dynamic-only field
  model: Intel Xeon...  <- cyan:   dynamic-only field
os:
  distribution: rhel    <- green:  matches static
  version: 9.3          <- red:    differs from static (static says 9.2)
  pretty_name: ...      <- cyan:   dynamic-only field
```

**Color legend**

| Color | Meaning |
|-------|---------|
| Green | Dynamic value matches static (expected == actual) |
| Red | Dynamic value differs from static (drift detected) |
| Cyan | Dynamic field has no static counterpart (live-only data) |

Static fields with no dynamic counterpart (`ansible_groups`, `bmc`, `os_partitioning`, `network_interfaces[].mac/network`) are displayed as plain YAML without coloring.

**Missing data handling**

- No `dynamic_*.yml` files: static is shown normally; dynamic section prints `(no dynamic data yet)`.
- No `static_*.yml` files: static section prints `(no static data)`; dynamic is shown fully in cyan.
- Multiple `dynamic_*.yml` files (e.g. from future daemons): all are deep-merged before display; later files win on key conflicts.

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
