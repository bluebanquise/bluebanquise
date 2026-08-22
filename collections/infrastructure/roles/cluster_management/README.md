# cluster_management

## Description

This role is a 2026-08 merge of four previously-separate roles (`cluster_state`, `cluster_tools`,
`cluster_supervision`, `cluster_events`) into one. They were split incrementally as the system
grew, but they share one data model (the per-host `/var/lib/bluebanquise/cluster/hosts/`
directory), one daemon pattern, and increasingly overlapping code - splitting them meant every
cross-role dependency (the CLI needing the event/latch library, the state daemon needing the
CLI's drift-comparison logic) had to be a soft, presence-checked dependency with a live-fallback
code path when the other role wasn't installed. Merged, all of that collapses to plain, always-
present internal files. `cluster_playbooks` (orchestration/push - declaring and applying role
packs to hosts) stayed a separate role on purpose: it shares no code with any of the four pieces
here, and is a genuinely different concern from observability.

It installs, in one role:

- **State tracking**: a static per-host inventory snapshot (`static_cluster_state.yml`) plus
  `bluebanquise-cluster-dynamic`, a daemon that periodically gathers live system data (and BMC
  reachability) over SSH into `dynamic_cluster_state.yml`.
- **Health supervision**: a library of check scripts plus `bluebanquise-cluster-supervision-daemon`,
  a daemon that runs configured health checks (SMART, dmesg/MCE/ECC errors, BMC sensors/logs,
  service liveness, ...) against hosts and writes the results to `supervision.yml`/
  `dynamic_supervision.yml`.
- **Host status & events**: `status.yml` (a per-host latched Ok/Error per subsystem, plus a
  maintenance flag) and `events.yml` (an append-only history), shared by both daemons above.
- **The `bluebanquise-cluster` CLI**: a dispatcher plus plugins (`state`, `supervision`,
  `events`, `maintenance`, `dashboard`) that read all of the above back for a human.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Run this role on the management node.

```yaml
- hosts: fn_management
  roles:
    - bluebanquise.infrastructure.cluster_management
```

Re-run whenever the inventory or `cluster_management_supervision_checks` changes, then restart
both daemons to pick it up - each loads its configuration and (for the supervision daemon) caches
every check script's content once at startup, not hot-reloaded by a role re-run alone:

```bash
systemctl restart bluebanquise-cluster-dynamic bluebanquise-cluster-supervision-daemon
systemctl enable bluebanquise-cluster-dynamic bluebanquise-cluster-supervision-daemon  # optional: start on boot
journalctl -u bluebanquise-cluster-dynamic -f
journalctl -u bluebanquise-cluster-supervision-daemon -f
```

Enable debug logging at runtime by editing either daemon's `.conf` file (`/etc/bluebanquise/
cluster_dynamic.conf` or `/etc/bluebanquise/cluster_supervision_daemon.conf`) and setting
`log_level: DEBUG`, then restarting - or pass `--log-level DEBUG` directly for one-shot debugging.

## Output structure

```
/etc/bluebanquise/
  cluster_dynamic.conf               # state daemon settings
  cluster_supervision_checks.conf    # per-host checks + BMC credentials (0640 - can hold secrets)
  cluster_supervision_daemon.conf    # supervision daemon settings
/usr/local/lib/bluebanquise/cluster/
  state_diff.py                      # shared drift-comparison library
  events.py                          # shared status/event library
  plugins/{state,supervision,events,maintenance,dashboard}.py
/usr/local/lib/bluebanquise/supervision/scripts/
  check_bmc, ssh_check_*             # health check scripts
/var/lib/bluebanquise/cluster/hosts/<hostname>/
  static_cluster_state.yml           # Ansible-owned inventory snapshot
  dynamic_cluster_state.yml          # state daemon-owned live data
  supervision.yml                    # supervision daemon-owned, full per-check detail
  dynamic_supervision.yml            # supervision daemon-owned, host_status/bmc_status summary
  status.yml                         # latched Ok/Error per subsystem + maintenance flag
  events.yml                         # append-only event history
/var/lib/bluebanquise/cluster/.tmp/  # shared tmp directory for atomic writes by both daemons
```

## State tracking

`static_cluster_state.yml` is generated from `hostvars` (inventory data) - no SSH connection
required for this half. Only fields present in the inventory are written; optional fields are
omitted when undefined.

### Processed fields (static)

| Field | Source | Required |
|-------|--------|----------|
| `hostname` | host name | always |
| `ansible_groups.function` | `fn_*` group membership | always |
| `ansible_groups.hardware` | `hw_*` group membership | always |
| `ansible_groups.os` | `os_*` group membership | always |
| `network_interfaces` | host vars `network_interfaces` (`interface` key renamed to `name`) | always |
| `network_interfaces[].ib_rate` | interface's own `ib_rate`, else `networks[<network>].ib_rate` | optional |
| `bmc` | host vars `bmc` | optional |
| `cpu.architecture` | `hw_specs.cpu.architecture` or `hw_architecture` | optional |
| `cpu.sockets` | `hw_specs.cpu.sockets` | optional |
| `cpu.cores_per_socket` | `hw_specs.cpu.cores_per_socket` | optional |
| `cpu.threads_per_core` | `hw_specs.cpu.threads_per_core` | optional |
| `gpu` | `hw_specs.gpu` normalized to a list (`none` becomes `[]`) | always (default `[]`) |
| `pcie` | `hw_specs.pcie` (list of `{name, width, speed}`, unmodified) | optional |
| `os.distribution` | `os_operating_system.distribution` | optional |
| `os.version` | `os_operating_system.distribution_version` | optional |
| `firewall` | `os_firewall` as bool | optional |
| `access_control.type` | `os_access_control` | optional |
| `os_partitioning` | `os_partitioning` | optional |
| `kernel` | `os_kernel_version` | optional |

### Example static output

```yaml
hostname: c001

ansible_groups:
  function:
    - fn_compute
  hardware:
    - hw_cpu_server_type_C
  os:
    - os_ubuntu_24

network_interfaces:
  - name: enp1s0
    ip4: 10.10.3.1/16
    mac: 1a:2b:3c:4d:31:31
    network: net-admin
  - name: ib0
    ip4: 10.20.3.1/16
    mac: 1a:2b:3c:4d:32:31
    network: interconnect
    ib_rate: "100 Gb/sec (4X EDR)"

bmc:
  ip4: 10.10.103.1
  mac: 2a:2b:3c:2d:30:31
  name: bc001
  network: net-admin

cpu:
  architecture: x86_64
  sockets: 1
  cores_per_socket: 8
  threads_per_core: 1

gpu: []

pcie:
  - name: "0000:3b:00.0"
    width: 16
    speed: "16.0 GT/s PCIe"

os:
  distribution: ubuntu
  version: "24.04"

firewall: false

access_control:
  type: disabled

os_partitioning:
  - device: /dev/sda
    ...

kernel: 5.14.0-427.24.1.el9_4.x86_64
```

### How the state daemon works

1. On each scan cycle the daemon submits all hosts to a thread pool.
2. Per host: BMC ping (if one is attached, see below) → host ping check → SSH check → data
   gathering via SSH commands.
3. Gathered data is written atomically to `dynamic_cluster_state.yml` using a tmp file and
   `os.replace()`, protected by a per-host `dynamic_cluster_state.lock` file.
4. After the cycle completes the daemon sleeps for `scan_interval` seconds before starting the
   next cycle.

SSH is invoked as `ssh <hostname>` with no explicit user or key flags — connection parameters
(user, identity file, jump hosts, etc.) are resolved from the `bluebanquise` user's
`~/.ssh/config`. The daemon runs as the `bluebanquise` user via systemd.

### BMC ping

If a host's `static_cluster_state.yml` has a `bmc.ip4` (i.e. the inventory declares a `bmc` for
it), the daemon also pings that address directly - independent of, and before, the host's own
ping/SSH checks, since a BMC being reachable while the host itself is powered off or unreachable
is exactly the situation this is useful for. Written as `bmc: {ping: true|false}` in
`dynamic_cluster_state.yml`. Deliberately ping-only, not a health check (that's `check_bmc`'s
job, see "Health supervision" below) - this answers "is the BMC's network stack up," nothing
more. A host with no `bmc` in its static snapshot gets no `bmc` key in the dynamic output at all.

Because `ping` has no static counterpart key inside the nested `bmc` dict, it never registers as
drift - `bluebanquise-cluster state` renders it as a plain dynamic-only (cyan) value, same
mechanism that already makes any other dynamic-only field safe, no special-casing required. The
static side's `bmc.{ip4,mac,name,network}` fields keep rendering as static-only (blue `NA` on the
dynamic side) exactly as they did before this field existed.

### Example dynamic output

```yaml
hostname: c001
last_updated: '2026-07-13T10:00:00+00:00'
ping: true
ssh: true
bmc:
  ping: true
cpu:
  architecture: x86_64
  count: 72
  threads_per_core: 2
  cores_per_socket: 18
  sockets: 2
  model: Intel(R) Xeon(R) Gold 6154 CPU @ 3.00GHz
ram:
  total_bytes: 137438953472
  available_bytes: 131801407488
gpu:
  - '01:00.0 VGA compatible controller: NVIDIA Corporation GV100GL [Tesla V100]'
firewall: true
access_control:
  type: selinux
  state: Enforcing
os:
  distribution: rhel
  version: '9.2'
  pretty_name: Red Hat Enterprise Linux 9.2 (Plow)
kernel: 5.14.0-284.11.1.el9_2.x86_64
network_interfaces:
  - name: enp1s0
    ip4:
      - 10.10.3.1/16
    ip6: []
    speed_mbps: 1000
    ib_rate: null
  - name: ib0
    ip4:
      - 10.20.3.1/16
    ip6: []
    speed_mbps: null
    ib_rate: "100 Gb/sec (4X EDR)"
  - name: lo
    ip4:
      - 127.0.0.1/8
    ip6:
      - '::1/128'
    speed_mbps: null
    ib_rate: null
pcie:
  - name: "0000:3b:00.0"
    width: 16
    speed: "16.0 GT/s PCIe"
    max_width: 16
    max_speed: "16.0 GT/s PCIe"
    description: "NVIDIA Corporation GV100GL [Tesla V100 PCIe 16GB]"
```

If a host is unreachable by ping, only `hostname`, `last_updated`, and `ping: false` (plus `bmc`
if attached) are written. If ping succeeds but SSH fails, `ssh: false` is also written and no
gathered data is included.

### Adding new gatherers

Each gatherer is a standalone function with the signature:

```python
def gather_<name>(hostname, ssh_timeout):
    # run one or more SSH commands via run_ssh_command(hostname, command, ssh_timeout)
    # return any YAML-serialisable value, or None on failure
    ...
```

Register it by adding an entry to the `GATHERERS` dict in `bluebanquise-cluster-dynamic`. The key
name becomes the field name in `dynamic_cluster_state.yml`. To have `bluebanquise-cluster state`
compare it against the static side, give it the same key name in `static_cluster_state.yml.j2`.

### Schema alignment between static and dynamic

The `cpu`, `gpu`, `os`, `firewall`, `access_control`, `kernel`, `pcie[].name/width/speed`, and
`network_interfaces[].name/ib_rate` fields use the same keys and value formats on both sides, so
`bluebanquise-cluster state` can compare them field by field and highlight drift.

Fields present only in static (`ansible_groups`, `os_partitioning`,
`network_interfaces[].mac/network`, and - within `bmc` - `ip4`/`mac`/`name`/`network`) have no
dynamic counterpart and are displayed as inventory-only data. Fields present only in dynamic
(`last_updated`, `ping`, `ssh`, `cpu.count`, `cpu.model`, `os.pretty_name`,
`access_control.state`, `ram`, `network_interfaces[].ip6/speed_mbps`, `pcie[].max_width/max_speed/
description`, and - within `bmc` - `ping`) have no static counterpart and are displayed as
live-only data. `bmc` itself is the one top-level key present, with different sub-fields, on
*both* sides.

### PCIe link tracking

`hw_specs.pcie` (optional, a peer to `hw_specs.cpu`/`hw_specs.gpu`) declares an expected link
width/speed per PCIe device, keyed by **PCI slot address** exactly as `lspci`/sysfs report it
(domain:bus:device.function, e.g. `0000:3b:00.0`) - the one identifier that's unambiguous and
doesn't depend on device class or discovery order:

```yaml
hw_specs:
  pcie:
    - name: "0000:3b:00.0"
      width: 16
      speed: "16.0 GT/s PCIe"
```

Nothing needs declaring up front to see live data: `gather_pcie` walks every device under
`/sys/bus/pci/devices/` that exposes `current_link_width`/`current_link_speed` (a real PCIe link -
this naturally excludes anything that isn't one), plus `max_link_width`/`max_link_speed` and an
`lspci -D -mm`-derived `description`, all informational (no static counterpart, always shown
dynamic-only). Practical workflow: run `bluebanquise-cluster state host <name>` first, read off
the slot/description/speed of the device you care about (a GPU, a HCA, a riser) from the
dynamic-only listing, then copy the `name` and the exact `speed` string into inventory - copying
the live string verbatim avoids any GT/s-vs-"gen" translation mistake, since comparison is a plain
string match.

### InfiniBand rate precedence

`ib_rate` can be declared per network interface, or once per network as a default that every
interface on it inherits unless overridden - the same precedence shape as the `nic` role's
`gw4`/`gateway4` (see its README):

```yaml
networks:
  interconnect:
    ib_rate: "100 Gb/sec (4X EDR)"   # default for every host's interface on this network

# a host with a lower-spec card overrides just its own interface:
network_interfaces:
  - interface: ib0
    network: interconnect
    ib_rate: "40 Gb/sec (4X QDR)"
```

Resolved in `static_cluster_state.yml.j2` (interface value wins, else the network's, else the key
is omitted for that interface) and gathered live by `gather_network_interfaces` (not a separate
gatherer - `ib_rate` is one more key inside the same `network_interfaces` named-list items, from
`/sys/class/infiniband/*/ports/*/rate`, matched to the netdev via its `dev_id` port offset). Same
`name`-keyed list as everything else in `network_interfaces`, so no `state.py`/`state_diff.py`
changes were needed. **Known gap**: no InfiniBand hardware in this sandbox to verify the live
gatherer against - implemented from the documented sysfs/IPoIB conventions, not yet confirmed on
a real HCA.

## Health supervision

Complementary to, but distinct from, state tracking: state tracking compares live state against
inventory-declared expectations (drift), while supervision runs real health probes and reports
pass/fail per check. A check that only compares an actual value to an expected one (e.g. "is this
NIC negotiating exactly 1000Mb/s") belongs in state tracking, not here - see "Scope: health vs.
state" below.

Declare checks in the inventory via `cluster_management_supervision_checks`, keyed by any Ansible
group name (not necessarily `fn_`/`hw_`/`os_` - any group works):

```yaml
cluster_management_supervision_checks:
  hw_server_A:
    check_bmc:
    ssh_check_disk_smart: /dev/sda
  os_ubuntu:
    ssh_check_fs_mount: "/shared mynfs:/export/path"
```

A host that is a member of several referenced groups accumulates every group's checks (a check
name defined in two groups for the same host: the later group wins for that one check). A bare
check name (no trailing value, like `check_bmc:` above) is called with no arguments; the daemon
still prepends the hostname as its first argument for locally-executed checks. Only hosts that
end up with at least one check get an entry in the generated configuration - a host in no
referenced group is never SSH-probed by the daemon.

### supervision.yml

```yaml
hostname: c001
last_scan: '2026-08-01T10:00:00+00:00'
ssh_gate: true
checks:
  check_bmc:
    args: null
    exit_code: 0
    error: false
    stdout: |
      Checking BMC bc001 (10.10.103.1) via IPMI for c001
      OK: BMC bc001 reports no sensor or log issues
    stderr: ''
  ssh_check_disk_smart:
    args: /dev/sda
    exit_code: 0
    error: false
    stdout: |
      Checking SMART health...
      Checking disk: /dev/sda
      OK: /dev/sda SMART health PASSED
      OK: All disks healthy
    stderr: ''
```

### dynamic_supervision.yml

```yaml
last_scan: '2026-08-01T10:00:00+00:00'
host_status: "Ok"
bmc_status: "Ok"
```

`bmc_status` is only present when `check_bmc` is part of that host's configured checks.
`host_status` reflects the initial SSH liveness gate plus every non-`check_bmc` check;
`bmc_status` reflects `check_bmc` alone - split so an operator can immediately tell whether a
problem is on the OS side or the BMC side. Either field is `"Ok"` or
`"Error, use bluebanquise-cluster supervision command to investigate."`.

### How the supervision daemon works

1. At startup: load daemon settings, load the generated checks catalog
   (`cluster_supervision_checks.conf`), and cache every check script's content in memory (so a
   cycle never re-reads a script from disk before piping it over SSH). All three are loaded once
   - a role re-run requires a service restart to take effect.
2. Each cycle, hosts are processed concurrently (`cluster_management_supervision_daemon_thread_pool_size`
   threads); within one host's checks run sequentially, one `ssh`/local subprocess at a time.
3. Per host: one cheap SSH liveness probe first
   (`cluster_management_supervision_daemon_ssh_gate_timeout`). If it fails, every `ssh_*` check
   is skipped for this cycle (recorded as an error, not silently dropped) - but locally-executed
   checks (`check_bmc`) still run, since a BMC check is exactly what you want when the OS itself
   is unreachable.
4. `ssh_*` checks: the cached script content is piped over the SSH session's stdin to
   `ssh <host> bash -s -- <args>` - no file is ever uploaded, and there is no shell string to
   escape, so the script runs exactly as if typed at a terminal (sudo included, given the usual
   passwordless-sudo setup this codebase already relies on elsewhere).
5. Any other check runs locally, with the target hostname prepended as its first argument.
6. Results are written atomically (tmp file + `os.replace()`, per-host lock file) to
   `supervision.yml` and `dynamic_supervision.yml`.

### Writing a new check script

A script must:

- Print human-readable progress/results to stdout (and errors to stderr) - this is what
  `bluebanquise-cluster supervision` displays verbatim.
- Exit `0` on success, non-zero (`2` by convention in the built-in scripts) on failure.
- For a `ssh_`-prefixed script: read its arguments from `$1`, `$2`, ... as usual - it runs as a
  normal bash script on the remote host, nothing special needed.
- For a locally-executed script: its first argument (`$1`/`sys.argv[1]`) is always the target
  hostname, prepended automatically by the daemon; any configured args follow after it.

Document accepted arguments in the "Built-in checks" table below when adding one.

### Scope: health vs. state

Only keep a check here if it detects an actual fault, not just a mismatch against an expected
value the operator typed into `cluster_management_supervision_checks` - that comparison
duplicates state tracking's job and belongs there instead (or as a new gatherer, if the live
value isn't tracked yet). Two probes from the predecessor prototype (`bluebanquise_healthchecker`)
were split rather than imported wholesale for exactly this reason: `check_cpu_count_mce`'s
core-count-vs-expected half was dropped (state tracking already tracks live `cpu.count`), keeping
only its MCE dmesg scan as `ssh_check_mce_errors`; `check_pcie`'s link-width/speed-vs-expected
half was dropped for the same reason, keeping only its AER dmesg scan as
`ssh_check_pcie_aer_errors`.

**Deferred, not forgotten:** `check_eth_speed` (actual vs. expected NIC speed) and `check_ib_rate`
(actual vs. expected InfiniBand rate) were dropped outright rather than split, since there is no
fault-only half to keep - both are pure "actual vs. expected" comparisons. State tracking should
grow gatherers for these (it already gathers `network_interfaces[].speed_mbps` live; PCIe
width/speed and IB rate would be new gatherers) so the comparison lives there instead. Not done
yet as of this role's introduction (2026-08).

## Built-in checks

| Check | Executed | Arguments | Description |
|-------|----------|-----------|-------------|
| `ssh_check_disk_smart` | remote (SSH) | `[device]` - all detected disks if omitted | SMART health status per disk |
| `ssh_check_dmesg_errors` | remote (SSH) | `[level]` - default `err` | Scans dmesg for entries at or above the given level |
| `ssh_check_fs_mount` | remote (SSH) | `<mount_point> <expected_source>` | Fails if not mounted, or mounted from an unexpected source |
| `ssh_check_fs_usage` | remote (SSH) | `<path> <threshold_percent>` | Fails if filesystem usage at `path` is at/above the threshold |
| `ssh_check_gpu_nvidia` | remote (SSH) | `[max_temp_celsius]` - default `85` | nvidia-smi presence, Xid dmesg errors, ECC uncorrected errors, temperature |
| `ssh_check_ib_errors` | remote (SSH) | none | InfiniBand HCA error counters via `perfquery` |
| `ssh_check_mce_errors` | remote (SSH) | none | Machine Check Exception errors in dmesg |
| `ssh_check_pcie_aer_errors` | remote (SSH) | none | PCIe AER (Advanced Error Reporting) events in dmesg |
| `ssh_check_ram_ecc_errors` | remote (SSH) | none | ECC memory errors via dmesg, EDAC counters, and mcelog |
| `ssh_check_services` | remote (SSH) | `<comma,separated,services>` | Fails if any listed service is not active |
| `check_bmc` | local | `[lookback_hours]` - default `24` | BMC sensor/log health via IPMI or Redfish (see below) |

### check_bmc

Runs locally on the management node (not over SSH) - it needs the target host's BMC address and
credentials, sourced from `bmc` + `hw_board_authentication` in the inventory (same fields
`bluebanquise_power` already uses), embedded by this role into
`cluster_supervision_checks.conf` for any host whose check list includes `check_bmc`. A host
missing either `bmc` or a `hw_board_authentication` entry with `protocol`/`user`/`password` all
set simply gets no `bmc` block written, and the check fails clearly (`CRITICAL: no bmc block for
...`) rather than silently.

Dispatches on the declared `protocol` (`IPMI` or `REDFISH`):

- **IPMI**: `ipmitool sdr elist` for any sensor not reporting `ok`/`ns`, plus `ipmitool sel elist`
  for recent (`lookback_hours`) asserted entries carrying a critical/failure keyword.
- **REDFISH**: discovers the `Systems` and `Chassis` collections generically (no hardcoded
  vendor-specific ids), checks `Status.Health`/`Status.HealthRollup` on every member found, and
  walks each System's `LogServices` entries for recent (`lookback_hours`) `Critical`/`Warning`
  severities. Trusts the BMC's own vendor-normalized health state rather than hardcoding
  per-vendor thresholds, so it adapts across vendors for free - the same idea
  `bluebanquise_power`'s `REDFISH.py` uses for discovering the `Systems` endpoint before a power
  action.

Needs `ipmitool` and the `requests` Python module (via the `bluebanquise-venv` package, same as
`bluebanquise_power`) on the management node - both pulled in by
`cluster_management_supervision_packages_to_install`.

**Known gap:** IPMI SEL entries and Redfish log severities can only be exercised against real
hardware - there is no way to validate the parsing logic against a real BMC in this repo's CI
sandbox (no BMC to talk to). The sensor/log field parsing follows `ipmitool`'s and Redfish's
documented output formats but should be treated as unverified against real hardware until run
against one.

## Host status & events

Solves a gap state tracking and supervision would otherwise share on their own: they recompute
status fresh every cycle, so a transient fault that self-heals before anyone looks leaves no
trace, and there's no way to say "I know this host is broken, stop reporting it while I fix it."

`status.yml`:

```yaml
maintenance:
  active: false
  reason: null
  since: null
  by: null
latched:
  cluster_state: Ok
  cluster_supervision: Error
```

`events.yml`:

```yaml
- number: 1
  kind: Error
  timestamp: '2026-08-03T10:15:00+00:00'
  subsystem: cluster_supervision
  message: "cluster_supervision: bmc_status -> error (check_bmc: CRITICAL: 2 issue(s) found on BMC bc001)"
- number: 2
  kind: Acknowledge
  timestamp: '2026-08-03T11:00:00+00:00'
  subsystem: cluster_supervision
  by: Oxedions
  reason: "replaced faulty PSU"
```

Displayed (by the `events` plugin) as, e.g.:
`[2] Acknowledge - 2026-08-03T11:00:00+00:00: cluster_supervision: acknowledged event #1 by Oxedions (replaced faulty PSU)`

Event kinds: `Error` (a fresh Ok->Error transition, written by a daemon), `Acknowledge`
(sysadmin cleared a latch), `MaintenanceStart`/`MaintenanceEnd` (sysadmin toggled maintenance).

### Latch policy

Both daemons call `record_transition(hostname, subsystem, is_error, message, base_path, tmp_path)`
once per host per cycle (`subsystem` is `cluster_state` or `cluster_supervision`). Behavior:

- Host in maintenance: no-op entirely - no latch change, no event, regardless of `is_error`.
- `is_error` is `False`: no-op. The latch never auto-clears on its own, and the live
  `dynamic_cluster_state.yml`/`dynamic_supervision.yml` already show current truth each cycle -
  the latch's only job is "did this go bad since the last ack", not "is it bad right now", so no
  "recovered" event is written either.
- `is_error` is `True` and the subsystem is already latched `Error`: no-op (suppressed) - this is
  what prevents `events.yml` from filling up with one identical entry per cycle for a
  permanently-broken host. The *first* transition is the only one that gets recorded until
  acknowledged.
- `is_error` is `True` and the subsystem was `Ok`: latch set to `Error`, one `Error` event
  written.

### Adding a new subsystem

Any daemon can participate: call `record_transition()` once per host per cycle with a subsystem
name of your choosing (`cluster_playbooks` was deliberately left out of this round - see
`AI/CLAUDE.md` - but the mechanism is generic). Use `acknowledge_event()`/`set_maintenance()`/
`clear_maintenance()` from a CLI context (see the `events`/`maintenance` plugins below for the
reference implementation) - no changes to `events.py` itself are needed either way, it has no
per-subsystem knowledge.

`state_diff.py` and `events.py` are standalone files (not an importable package - loaded
dynamically via `importlib.util.spec_from_file_location` by whichever plugin/daemon needs them),
but always installed together with everything else in this role: a daemon or plugin finding
either missing at startup treats it as a fatal, immediate error (this role's install is
incomplete), not something to gracefully route around.

## The `bluebanquise-cluster` CLI

```
bluebanquise-cluster <action> [args...]
```

If `<action>` does not match any installed plugin, the tool lists available actions and exits.

### state plugin

Reads static inventory snapshots (`static_*.yml`) and live daemon data (`dynamic_*.yml`) from
`/var/lib/bluebanquise/cluster/hosts/<hostname>/` and displays them with drift highlighting.

Files are paired **by suffix**: `static_<suffix>.yml` is compared against `dynamic_<suffix>.yml`
— nothing is merged across suffixes. Each suffix gets its own banner. `cluster_state` (the
primary static+dynamic pair) is always shown first; every other suffix (`pxe_stack`,
`cluster_playbooks`, or any future `dynamic_<name>.yml`/`static_<name>.yml` writer) follows,
sorted alphabetically.

```bash
bluebanquise-cluster state host c001    # display one host
bluebanquise-cluster state all          # display all hosts
bluebanquise-cluster state error        # display only hosts where at least one suffix has drift
```

**Output format**

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
```

**Color legend**

| Color | Meaning |
|-------|---------|
| Green | Dynamic value matches static (expected == actual) |
| Red | Dynamic value differs from static (drift detected) |
| Cyan | Field/suffix has no static counterpart (live-only data); static side is uncolored always |
| Blue `NA` | This side has no value at all for this key (missing on one side, not drift) |

**Missing data handling**: a suffix with only one side present gets a plain/cyan banner and no
comparison; a key present on one side but not the other renders as `<value> / NA` (blue on the
missing side, not counted as drift); a host directory with no state files at all shows
`(no state data)`.

**Maintenance / latch overlay:** a banner appears right under the host title whenever it's in
maintenance (yellow `[MAINTENANCE] since <date> by <who>: <reason>`) or has an unacknowledged
latched `cluster_state` error (red `[LATCHED ERROR] cluster_state - unacknowledged, see: ...`).
Such a host is excluded from `state error` (it's already known about).

### supervision plugin

Displays health check results (as opposed to `state`, which compares live state against
inventory-declared expectations, `supervision` runs real health probes and reports pass/fail).

```bash
bluebanquise-cluster supervision host c001   # display one host
bluebanquise-cluster supervision all         # display every host that has supervision data
bluebanquise-cluster supervision error       # display only hosts currently in error
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
```

Same maintenance/latch overlay as `state`, against the `cluster_supervision` latch.

### events plugin

Displays the per-host event history and acknowledges Error events.

```bash
bluebanquise-cluster events all                                    # every host's events
bluebanquise-cluster events error                                  # hosts with an unacknowledged error
bluebanquise-cluster events host c001                               # one host's events
bluebanquise-cluster events host c001 ack 3 --by Oxedions --reason "replaced faulty PSU"
```

`--by` and `--reason` are required on `ack` - deliberately, so `events.yml` stays a readable
history of who did what and why. `ack` looks up the target event's `subsystem` itself (no need
to pass it separately) and rejects acking anything that isn't a currently-latched `Error` event.

### maintenance plugin

Sets/clears a host's maintenance flag, historized the same way as everything else in
`events.yml`.

```bash
bluebanquise-cluster maintenance set c001 --by Oxedions --reason "firmware upgrade"
bluebanquise-cluster maintenance unset c001 --by Oxedions --reason "firmware upgrade complete"
```

`--by` and `--reason` are required on both actions. While active, both daemons stop latching new
errors for that host, and `state`/`supervision` show a `[MAINTENANCE]` banner instead of the
normal error coloring.

### dashboard plugin

`bluebanquise-cluster dashboard` — one static snapshot, three bordered frames with a green/red
gauge bar each: Connectivity (ping/SSH/BMC reachability), State Drift, Supervision. No
subcommands, no live refresh.

```bash
bluebanquise-cluster dashboard
```

```
BlueBanquise Cluster Dashboard - 21 host(s), 1 in maintenance

┌─ Connectivity ─────────────────────────────────────────────┐
│ Hosts up          20/21 (95%)   [███████████████████████░] │
│ Hosts SSH-able    19/21 (90%)   [█████████████████████░░░] │
│ BMC up             8/10 (80%)   [███████████████████░░░░░] │
└────────────────────────────────────────────────────────────┘

┌─ State Drift ──────────────────────────────────────────────┐
│ Hosts in sync     19/20 (95%)   [███████████████████████░] │
└────────────────────────────────────────────────────────────┘

┌─ Supervision ──────────────────────────────────────────────┐
│ Hosts healthy     18/19 (95%)   [███████████████████████░] │
└────────────────────────────────────────────────────────────┘
```

Every count/bar shows the same **green = healthy** quantity - "Hosts up", "Hosts in sync",
"Hosts healthy" - consistently, never the inverse.

**Denominators**: Connectivity's Hosts up/SSH-able count every host with a
`dynamic_cluster_state.yml`; BMC up counts only hosts with a `bmc` attached. State Drift counts
hosts with both a static and dynamic `cluster_state` file. Supervision counts hosts with a
`supervision.yml`. Hosts currently in maintenance are excluded from every frame's counts,
denominator included - disclosed once via the header's "N in maintenance", not repeated per frame.

**Data source, in priority order**: if a host has a latched value for the relevant subsystem in
its `status.yml`, that's used (`Error` = unhealthy) - this is *by design* the same "has anyone
acknowledged this" answer the latch already gives elsewhere, not necessarily "is it broken right
now". Otherwise (host never scanned with latching active yet), falls back to computing live -
`state_diff.py`'s `has_drift()` for State Drift, `dynamic_supervision.yml`'s `host_status`/
`bmc_status` directly for Supervision. Connectivity has no latch to prefer - ping/SSH/BMC
reachability were never part of the latch system - always read live.

**Gauge bar rule**: proportional to healthy/total at a fixed width, but never allowed to *look*
like a clean 100% or 0% result when the true value isn't exactly that - if rounding at the bar's
character width would otherwise collapse away the minority segment, one character is forced to
the minority color instead. Exact 0%/100% values are left alone.

### Adding new plugins

Create a Python file in `/usr/local/lib/bluebanquise/cluster/plugins/` with a `run(args, config)`
function:

```python
def run(args, config):
    base_path = config['base_path']                    # /var/lib/bluebanquise/cluster/hosts
    tmp_path = config['tmp_path']                       # /var/lib/bluebanquise/cluster/.tmp
    events_module_path = config['events_module_path']   # events.py's install path
    # args = remaining argv after the action name
    ...
```

The plugin is automatically discovered — no registration needed. `state_diff.py` and `events.py`
are the exception: they live one directory above `plugins/`, precisely so the dispatcher's
auto-discovery doesn't try to treat them as runnable actions.

## Variables

### State tracking (formerly `cluster_state_*`)

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_management_state_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host state folders |
| `cluster_management_state_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Temporary directory for atomic writes by state daemons |
| `cluster_management_state_hosts_group` | `all` | Ansible group whose members are processed (static write loop and daemon host list) |
| `cluster_management_state_conf_path` | `/etc/bluebanquise/cluster_dynamic.conf` | Path to the daemon's generated configuration file |
| `cluster_management_state_daemon_script_path` | `/usr/local/sbin/bluebanquise-cluster-dynamic` | Installation path for the daemon script |
| `cluster_management_state_scan_interval` | `300` | Seconds between full scan cycles |
| `cluster_management_state_thread_pool_size` | `100` | Maximum concurrent host scans |
| `cluster_management_state_ping_timeout` | `5` | Seconds before ping times out |
| `cluster_management_state_ssh_timeout` | `10` | Seconds before SSH connect or command times out |
| `cluster_management_state_lock_timeout` | `30` | Seconds to wait for per-host write lock before skipping |
| `cluster_management_state_log_level` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `cluster_management_state_diff_module_path` | `/usr/local/lib/bluebanquise/cluster/state_diff.py` | Path to the shared drift-comparison module |
| `cluster_management_state_events_module_path` | `/usr/local/lib/bluebanquise/cluster/events.py` | Path to the shared events module |

### CLI / tools (formerly `cluster_tools_*`)

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_management_tools_script_path` | `/usr/local/sbin/bluebanquise-cluster` | Installation path for the main script |
| `cluster_management_tools_lib_path` | `/usr/local/lib/bluebanquise/cluster` | Parent directory holding both `plugins/` and shared (non-plugin) library files like `state_diff.py` |
| `cluster_management_tools_plugins_path` | `{{ cluster_management_tools_lib_path }}/plugins` | Directory where action plugins are installed |
| `cluster_management_tools_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host state data (passed to plugins) |
| `cluster_management_tools_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Shared temporary directory for atomic writes (passed to plugins) |
| `cluster_management_tools_events_module_path` | `/usr/local/lib/bluebanquise/cluster/events.py` | Path to the shared events module (passed to plugins) |

### Supervision (formerly `cluster_supervision_*`)

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_management_supervision_packages_to_install` | `[ipmitool, bluebanquise-venv]` | Packages installed on the management node |
| `cluster_management_supervision_scripts_path` | `/usr/local/lib/bluebanquise/supervision/scripts` | Where check scripts are installed |
| `cluster_management_supervision_scripts` | see `defaults/main.yml` | List of built-in script filenames installed by this role |
| `cluster_management_supervision_checks` | `{}` | Operator-defined: `{ansible_group_name: {check_name: args_string_or_none}}` |
| `cluster_management_supervision_conf_path` | `/etc/bluebanquise/cluster_supervision_checks.conf` | Generated per-host checks + BMC credentials file (mode `0640`) |
| `cluster_management_supervision_daemon_conf_path` | `/etc/bluebanquise/cluster_supervision_daemon.conf` | Daemon settings file |
| `cluster_management_supervision_daemon_script_path` | `/usr/local/sbin/bluebanquise-cluster-supervision-daemon` | Installation path for the daemon script |
| `cluster_management_supervision_daemon_loop_interval` | `1800` | Seconds between full supervision cycles |
| `cluster_management_supervision_daemon_thread_pool_size` | `100` | Maximum concurrent host scans |
| `cluster_management_supervision_daemon_ssh_gate_timeout` | `10` | Seconds before the initial per-host SSH liveness probe times out |
| `cluster_management_supervision_daemon_ssh_check_timeout` | `60` | Seconds before one `ssh_*` check's script execution times out |
| `cluster_management_supervision_daemon_local_check_timeout` | `60` | Seconds before one locally-executed check times out |
| `cluster_management_supervision_daemon_log_level` | `INFO` | Daemon logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `cluster_management_supervision_hosts_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host output files |
| `cluster_management_supervision_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Shared temporary directory for atomic writes |
| `cluster_management_supervision_supervision_filename` | `supervision.yml` | Per-host filename for full check detail |
| `cluster_management_supervision_dynamic_filename` | `dynamic_supervision.yml` | Per-host filename for the `host_status`/`bmc_status` summary |
| `cluster_management_supervision_events_module_path` | `/usr/local/lib/bluebanquise/cluster/events.py` | Path to the shared events module |

### Events (formerly `cluster_events_*`)

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_management_events_lib_path` | `/usr/local/lib/bluebanquise/cluster` | Directory the shared events module is installed into |
| `cluster_management_events_module_path` | `{{ cluster_management_events_lib_path }}/events.py` | Full path to the installed module |
