# cluster_supervision

## Description

This role provides BlueBanquise's health-check ("supervision") system - complementary to, but
distinct from, `cluster_state`: `cluster_state` compares live state against inventory-declared
expectations (drift), while `cluster_supervision` runs real health probes (SMART, dmesg/MCE/ECC
errors, BMC sensors and logs, service liveness, ...) and reports pass/fail per check. A check
that only compares an actual value to an expected one (e.g. "is this NIC negotiating exactly
1000Mb/s") belongs in `cluster_state`, not here - see "Scope: health vs. state" below.

It installs:

- A library of check scripts under `/usr/local/lib/bluebanquise/supervision/scripts/`, each
  either a `ssh_`-prefixed script (runs on the remote host over SSH) or a locally-executed one
  (only `check_bmc` today, reaching the host's BMC via IPMI/Redfish instead of SSH).
- `bluebanquise-cluster-supervision-daemon`, a systemd service that loops with a sleep
  (`cluster_supervision_daemon_loop_interval`, default 1800s / 30 minutes), running every
  configured host's checks and writing the results to
  `/var/lib/bluebanquise/cluster/hosts/<hostname>/`.

Results are read back via the `bluebanquise-cluster supervision` plugin (installed by
`cluster_tools`), not by this role.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Run this role on the management node.

```yaml
- hosts: fn_management
  roles:
    - bluebanquise.infrastructure.cluster_supervision
```

Declare checks in the inventory via `cluster_supervision_checks`, keyed by any Ansible group
name (not necessarily `fn_`/`hw_`/`os_` - any group works):

```yaml
cluster_supervision_checks:
  hw_server_A:
    check_bmc:
    ssh_check_disk_smart: /dev/sda
  os_ubuntu:
    ssh_check_fs_mount: "/shared mynfs:/export/path"
```

A host that is a member of several referenced groups accumulates every group's checks (a check
name defined in two groups for the same host: the later group in `cluster_supervision_checks`
wins for that one check). A bare check name (no trailing value, like `check_bmc:` above) is
called with no arguments; the daemon still prepends the hostname as its first argument for
locally-executed checks. Only hosts that end up with at least one check get an entry in the
generated configuration - a host in no referenced group is never SSH-probed by the daemon.

Re-run the role whenever `cluster_supervision_checks` or the inventory's group membership
changes, then restart the daemon to pick it up (it loads its checks catalog and caches every
script's content once at startup, same as `cluster_state`'s host list - a role re-run alone does
not hot-reload it):

```bash
systemctl restart bluebanquise-cluster-supervision-daemon
systemctl enable bluebanquise-cluster-supervision-daemon  # optional: start on boot
journalctl -u bluebanquise-cluster-supervision-daemon -f   # follow its own operational logging
```

## Output structure

```
/etc/bluebanquise/
  cluster_supervision_checks.conf   # Ansible-owned, per-host checks + BMC credentials (0640)
  cluster_supervision_daemon.conf   # Ansible-owned, daemon settings
/var/lib/bluebanquise/cluster/hosts/<hostname>/
  supervision.yml                   # daemon-owned, full detail: exit code, stdout, stderr per check
  dynamic_supervision.yml           # daemon-owned, host_status/bmc_status summary
```

`cluster_supervision_checks.conf` can contain BMC credentials (for hosts checking `check_bmc`)
and is kept `bluebanquise:bluebanquise` mode `0640` - readable only by root or the `bluebanquise`
system user, never world-readable.

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

## How the daemon works

1. At startup: load daemon settings, load the generated checks catalog
   (`cluster_supervision_checks.conf`), and cache every check script's content in memory (so a
   cycle never re-reads a script from disk before piping it over SSH). All three are loaded once
   - a role re-run requires a service restart to take effect, same as `cluster_state`.
2. Each cycle, hosts are processed concurrently (`cluster_supervision_daemon_thread_pool_size`
   threads); within one host's checks run sequentially, one `ssh`/local subprocess at a time.
3. Per host: one cheap SSH liveness probe first
   (`cluster_supervision_daemon_ssh_gate_timeout`). If it fails, every `ssh_*` check is skipped
   for this cycle (recorded as an error, not silently dropped) - but locally-executed checks
   (`check_bmc`) still run, since a BMC check is exactly what you want when the OS itself is
   unreachable.
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

Document accepted arguments in this README's "Built-in checks" section below when adding one.

### Scope: health vs. state

Only keep a check here if it detects an actual fault, not just a mismatch against an expected
value the operator typed into `cluster_supervision_checks` - that comparison duplicates
`cluster_state`'s job and belongs there instead (or as a new `cluster_state` gatherer, if the
live value isn't tracked yet). Two probes from the predecessor prototype
(`bluebanquise_healthchecker`) were split rather than imported wholesale for exactly this reason:
`check_cpu_count_mce`'s core-count-vs-expected half was dropped (`cluster_state` already tracks
live `cpu.count`), keeping only its MCE dmesg scan as `ssh_check_mce_errors`; `check_pcie`'s
link-width/speed-vs-expected half was dropped for the same reason, keeping only its AER dmesg
scan as `ssh_check_pcie_aer_errors`.

**Deferred, not forgotten:** `check_eth_speed` (actual vs. expected NIC speed) and `check_ib_rate`
(actual vs. expected InfiniBand rate) were dropped outright rather than split, since there is no
fault-only half to keep - both are pure "actual vs. expected" comparisons. `cluster_state` should
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
`cluster_supervision_packages_to_install`.

**Known gap:** IPMI SEL entries and Redfish log severities can only be exercised against real
hardware - there is no way to validate the parsing logic against a real BMC in this repo's CI
sandbox (no BMC to talk to). The sensor/log field parsing follows `ipmitool`'s and Redfish's
documented output formats but should be treated as unverified against real hardware until run
against one.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_supervision_packages_to_install` | `[ipmitool, bluebanquise-venv]` | Packages installed on the management node |
| `cluster_supervision_scripts_path` | `/usr/local/lib/bluebanquise/supervision/scripts` | Where check scripts are installed |
| `cluster_supervision_scripts` | see `defaults/main.yml` | List of built-in script filenames installed by this role |
| `cluster_supervision_checks` | `{}` | Operator-defined: `{ansible_group_name: {check_name: args_string_or_none}}` |
| `cluster_supervision_conf_path` | `/etc/bluebanquise/cluster_supervision_checks.conf` | Generated per-host checks + BMC credentials file (mode `0640`) |
| `cluster_supervision_daemon_conf_path` | `/etc/bluebanquise/cluster_supervision_daemon.conf` | Daemon settings file |
| `cluster_supervision_daemon_script_path` | `/usr/local/sbin/bluebanquise-cluster-supervision-daemon` | Installation path for the daemon script |
| `cluster_supervision_daemon_loop_interval` | `1800` | Seconds between full supervision cycles |
| `cluster_supervision_daemon_thread_pool_size` | `100` | Maximum concurrent host scans |
| `cluster_supervision_daemon_ssh_gate_timeout` | `10` | Seconds before the initial per-host SSH liveness probe times out |
| `cluster_supervision_daemon_ssh_check_timeout` | `60` | Seconds before one `ssh_*` check's script execution times out |
| `cluster_supervision_daemon_local_check_timeout` | `60` | Seconds before one locally-executed check times out |
| `cluster_supervision_daemon_log_level` | `INFO` | Daemon logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `cluster_supervision_hosts_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host output files, shared with `cluster_state`/`cluster_playbooks` |
| `cluster_supervision_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Shared temporary directory for atomic writes |
| `cluster_supervision_supervision_filename` | `supervision.yml` | Per-host filename for full check detail |
| `cluster_supervision_dynamic_filename` | `dynamic_supervision.yml` | Per-host filename for the `host_status`/`bmc_status` summary |
