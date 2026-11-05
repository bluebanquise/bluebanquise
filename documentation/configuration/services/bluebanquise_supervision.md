# BlueBanquise supervision

## Description

This role installs **bluebanquise-supervision** (nicknamed *Inquisitor*), a tool that keeps an eye
on every host of the cluster, all the time:

* **Probes**: health checks (disks SMART, kernel errors, ECC memory, GPU, InfiniBand, services, file
  systems, BMC...), run regularly and on demand. Remote probes are scripts stored on the management
  host, sent to the host through SSH: nothing is installed on supervised hosts.
* **Drift check**: compares what is really on a host (CPU, GPU, PCIe links, OS, kernel, firewall,
  SELinux, network interfaces) with what the inventory expects.
* **Events**: each host keeps a log of its errors, acknowledgements, maintenance periods and admin
  notes. An error stays visible until an admin acknowledges it, even if it disappeared meanwhile.
* **Maintenance mode**: a host in maintenance is not probed anymore.
* **Actions**: a command can be run on the first error of a host, for example to drain it in Slurm.
* A **command line tool**, a **WebUI** with a map of the cluster, a **REST API**, and a
  **Prometheus exporter**.

The tool is made of small parts, each simple to read and debug:

| Part | Kind | Role |
|------|------|------|
| `bluebanquise-supervision-probe` | daemon | Probes hosts, writes results and events, runs actions |
| `bluebanquise-supervision-api` | daemon | REST API and WebUI |
| `bluebanquise-supervision-exporter` | daemon | Prometheus metrics |
| `bluebanquise-supervision` | command | Command line tool |

All of them run as the dedicated unprivileged `bluebanquise-supervision` user, and share data
through plain YAML files.

[SCHEMA: bluebanquise-supervision-workflow]
*Inventory -> role -> hosts.yml; probe daemon -> SSH -> hosts; probe daemon -> files (probes.yml,
events.yml...); CLI, API/WebUI and exporter reading the files; CLI/API dropping probe requests read
by the probe daemon; on_fail action triggered on a first error.*

## Instructions

### 1. Give the tool SSH access to hosts

On its first run, the role generates an SSH key for the `bluebanquise-supervision` user, and
displays its public key. Remote probes connect with it, as the `bluebanquise` user by default
(`bluebanquise_supervision_ssh_username`, or `ssh.username` per group, see below).

Add this public key to `os_admin_ssh_keys`, so that it is deployed on hosts:

```yaml
os_admin_ssh_keys:
  - ssh-ed25519 AAAAC3Nza... bluebanquise-supervision@mgt1
```

The remote user needs passwordless sudo: probes read the kernel log, SMART data, etc.

### 2. Define what to check

Checks are defined per Ansible group (any group: `fn_`, `hw_`, `os_`, or custom), in
`bluebanquise_supervision_checks`:

```yaml
bluebanquise_supervision_checks:
  fn_compute:
    drift_check: true
    probes:
      ssh_check_fs_usage: "/ 90"
      ssh_check_dmesg_errors: crit
      ssh_check_services: "sshd,slurmd"
    actions:
      on_fail: 'sudo /usr/bin/scontrol update nodename=$SUPERVISION_HOST state=drain reason="supervision: $SUPERVISION_PROBES"'
  hw_supermicro_X11:
    probes:
      check_bmc:
      ssh_check_disk_smart:
      ssh_check_ram_ecc_errors:
  os_rhcos:
    ssh:
      username: core
```

* `probes`: probe name and its arguments (empty for no argument). See
  [Probes](#probes) for the list.
* `drift_check`: `true` to compare the host with the inventory. See [Drift check](#drift-check).
* `actions.on_fail`: command run on the first error of a host. See [Actions](#actions).
* `ssh.username`: remote user for this group of hosts.

A host member of several of these groups accumulates them, in the order groups are written:
probes and actions are merged (the later group wins for the same name), `ssh.username` and
`drift_check` are taken from the last group defining them. In the example above, a compute node
of hardware `hw_supermicro_X11` gets the 3 probes of `fn_compute`, plus the 3 probes of its
hardware group.

Only hosts with at least one probe, or the drift check, are supervised.

### 3. Create WebUI users

The WebUI and the REST API need HTTP basic authentication. Generate a password hash on a host where
the role is already installed:

```
bluebanquise-supervision hash-password
```

And add users to the inventory (preferably in an Ansible vault):

```yaml
bluebanquise_supervision_webui_users:
  - name: admin
    password_hash: "scrypt:32768:8:1$..."
```

### 4. Choose where the WebUI and the exporter listen

Both listen on `127.0.0.1` by default. To reach them from other hosts, set the management network
IP of the host (or `0.0.0.0`):

```yaml
bluebanquise_supervision_api_bind: 10.10.0.1
bluebanquise_supervision_api_port: 8091
bluebanquise_supervision_exporter_bind: 10.10.0.1
bluebanquise_supervision_exporter_port: 9810
```

The WebUI has no TLS: use a reverse proxy (for example the `haproxy` role) to serve it over HTTPS
outside of the management network.

Then run the role. Configuration is read by daemons at startup only: the role restarts them when
anything changes.

## Probes

| Probe | Runs | Arguments | Checks |
|-------|------|-----------|--------|
| `ssh_check_disk_smart` | on host | `[device]`, all disks if omitted | SMART health of disks (ATA, NVMe, SAS) |
| `ssh_check_dmesg_errors` | on host | `[level]`, default `err` | No kernel log entry at this level (`err+` works on recent systems) |
| `ssh_check_fs_mount` | on host | `<mount_point> <expected_source>` | File system mounted, from the expected source |
| `ssh_check_fs_usage` | on host | `<path> <threshold_percent>` | File system usage below the threshold |
| `ssh_check_gpu_nvidia` | on host | `[max_temp_celsius]`, default `85` | nvidia-smi works, GPUs detected, no Xid errors, no uncorrected ECC error, temperature |
| `ssh_check_ib_errors` | on host | none | InfiniBand error counters are zero (`perfquery`) |
| `ssh_check_mce_errors` | on host | none | No Machine Check Exception in the kernel log |
| `ssh_check_pcie_aer_errors` | on host | none | No PCIe AER event in the kernel log |
| `ssh_check_ram_ecc_errors` | on host | none | No ECC memory error (kernel log, EDAC counters, mcelog) |
| `ssh_check_services` | on host | `<comma,separated,services>` | All services active |
| `check_bmc` | on management host | `[lookback_hours]`, default `24` | BMC sensors and logs, through IPMI or Redfish |

`check_bmc` uses the `bmc` entry of the host (its `ip4`, else its `name`) and its
`hw_board_authentication` credentials, the same way as the `bluebanquise_power` role. For IPMI, it
checks sensors (`ipmitool sdr elist`) and recent critical SEL entries. For Redfish, it checks the
health of every System and Chassis found, and recent Critical/Warning log entries. Redfish needs
the Python `requests` module, shipped in `bluebanquise-venv` 1.2.2 and later.

### How a probe pass works

1. **SSH gate**: a cheap `ssh host true`, if the host has `ssh_` probes or the drift check. If it
   fails, these are skipped and reported as failed (`ssh` is reported as failed too), while local
   probes like `check_bmc` still run: it is exactly when the OS is down that the BMC matters.
2. **Probes**, in name order. A probe whose name starts with `ssh_` is a bash script, sent to the
   host with `ssh host bash -s -- <args>`: nothing is written on the host. Any other probe runs on
   the management host, with the hostname as first argument.
3. **Drift check**, if enabled.
4. Results are written, then, if anything failed: see [Events](#events-acknowledgement-and-maintenance).

### Adding a probe

Add a script to the role `files/probes/` folder (all files of this folder are installed):

* Name it `ssh_<something>` to run it on hosts, anything else to run it on the management host.
* Print what was checked on stdout (displayed as is by the tool), exit `0` when healthy, anything
  else (`2` by convention) on error.
* A remote probe gets its arguments as `$1`, `$2`... It runs as the remote user: use `sudo -n`
  for privileged commands, and never take a failing command as "no error found".
* When searching logs, match real error reports only: boot messages like `AER: enabled with IRQ`
  or `mce: CPU supports 22 MCE banks` are printed on every healthy host.
* A local probe gets the hostname as `$1`, then its arguments.

## Drift check

The `ssh_gather` script collects host data in a single SSH session (written to `gathered.yml`),
which is compared with the values of the inventory. Only values set in the inventory are compared.

| Compared | Inventory | Found on host |
|----------|-----------|---------------|
| CPU architecture, sockets, cores per socket, threads per core | `hw_specs.cpu` (architecture can also come from `hw_architecture`) | `lscpu` |
| GPUs | `hw_specs.gpu` (`none` for no GPU) | `nvidia-smi` GPU names |
| PCIe link width and speed | `hw_specs.pcie` (list of `name` (slot), `width`, `speed`) | sysfs |
| Distribution and version | `os_operating_system.distribution`, `.distribution_version` | `/etc/os-release` (`9` matches `9.4`) |
| Kernel | `os_kernel_version` | `uname -r` |
| Firewall | `os_firewall` | firewalld active |
| SELinux | `os_access_control` (`enforcing`, `permissive`, `disabled`) | `getenforce` |
| Interfaces, their IPv4 and InfiniBand rate | `network_interfaces` (`interface`, `ip4`, `ib_rate` or network `ib_rate`) | `ip addr`, sysfs |

To declare PCIe links, run a first drift check, then copy the slot name and exact speed string of
the devices that matter from `gathered.yml` into `hw_specs.pcie`:

```yaml
hw_specs:
  pcie:
    - name: "0000:3b:00.0"
      width: 16
      speed: "16.0 GT/s PCIe"
```

## Events, acknowledgement and maintenance

When a probe pass fails (anything failed: SSH, a probe, the drift check), an **Error** event is
written in the host events log, unless the host already has an error not acknowledged yet: one
problem gives one event, not one per pass. The host is now *latched*: it is displayed in error until
an admin **acknowledges** it, even if the problem disappeared meanwhile, so that nothing goes
unnoticed. If the problem is still there after the acknowledgement, the next pass writes a new
Error event.

A host in **maintenance** is not probed by the regular loop anymore, and never gets events nor
actions. It can still be probed on demand, to check it before leaving maintenance.

Admins can add free text **notes** to the events log ("replaced DIMM B2").

Event kinds: `Error`, `Action`, `Acknowledge`, `MaintenanceStart`, `MaintenanceEnd`, `Note`.

## Actions

`actions.on_fail` runs on the management host, as the `bluebanquise-supervision` user, with
`/bin/sh`, each time a new Error event is written (first error, or first error after an
acknowledgement). Its result is written as an `Action` event.

The host and the failed probes are given as environment variables, never inserted in the command
text:

* `SUPERVISION_HOST`: the host name
* `SUPERVISION_PROBES`: failed probes, comma separated (`ssh` and `drift` included)

To use sudo in an action, allow the exact command (full path) in the inventory:

```yaml
bluebanquise_supervision_sudoers_commands:
  - /usr/bin/scontrol
```

## Command line tool

Run as root, or with sudo (the admin name written in events comes from `SUDO_USER`):

```
bluebanquise-supervision status                              # state of all hosts
bluebanquise-supervision show c001                           # last probe results
bluebanquise-supervision events c001                         # events log
bluebanquise-supervision probe c001                          # probe now, wait and show results
bluebanquise-supervision probe c001 --no-wait
bluebanquise-supervision ack c001 replaced the faulty disk
bluebanquise-supervision maintenance start c001 DIMM swap
bluebanquise-supervision maintenance stop c001 DIMM replaced
bluebanquise-supervision note c001 fan is noisy, to watch
bluebanquise-supervision hash-password
```

Only `probe` needs the probe daemon to be running: other commands work on files directly.

## WebUI

* `/`: global report (hosts ok, in error, in maintenance, never probed), and the hosts, displayed
  as a **map** of the cluster (one tile per host, grouped by function group, hover a tile for its
  status) or as a **list** (one row per host with its status). Colors: green ok, red error, blue
  maintenance, grey never probed. Filters show only hosts in error and/or in maintenance. Click a
  host to open its page.
* The moon/sun button (top right) switches between dark and light mode. By default, the WebUI
  follows the system theme. The chosen mode and view are remembered by the browser.
* `/<host>`: host page, with its state, last probe results, drift findings, events log, and
  buttons to probe now, acknowledge, start or stop maintenance, and add a note.

## REST API

All routes need HTTP basic authentication. POST and DELETE requests must be sent as JSON
(`Content-Type: application/json`): browsers can not send such requests from another web site,
which protects the API from cross-site requests using the cached credentials of an admin.

| Method | Route | Body | Description |
|--------|-------|------|-------------|
| GET | `/api/hosts` | | State of all hosts, and counts per state |
| GET | `/api/hosts/<host>` | | State, maintenance and last probe results |
| GET | `/api/hosts/<host>/events` | | Events log |
| POST | `/api/hosts/<host>/probe` | `{}` | Probe now, returns a `request_id` found in the results once done |
| POST | `/api/hosts/<host>/acknowledge` | `{"reason": "..."}` | Acknowledge the error |
| POST | `/api/hosts/<host>/maintenance` | `{"reason": "..."}` | Start maintenance |
| DELETE | `/api/hosts/<host>/maintenance` | `{"reason": "..."}` | Stop maintenance |
| POST | `/api/hosts/<host>/notes` | `{"text": "..."}` | Add a note |

Example:

```
curl -u admin -H 'Content-Type: application/json' -X POST -d '{"reason": "DIMM swap"}' http://127.0.0.1:8091/api/hosts/c001/maintenance
```

## Prometheus metrics

`http://<exporter_bind>:<exporter_port>/metrics`:

| Metric | Labels | Value |
|--------|--------|-------|
| `bluebanquise_supervision_host_state` | `host`, `group`, `state` | 1 for the current state (`ok`, `error`, `maintenance`, `unknown`), 0 for others |
| `bluebanquise_supervision_host_latched` | `host`, `group` | 1 if an error is not acknowledged yet |
| `bluebanquise_supervision_host_maintenance` | `host`, `group` | 1 if in maintenance |
| `bluebanquise_supervision_host_last_probe_timestamp_seconds` | `host`, `group` | End of the last probe pass |
| `bluebanquise_supervision_probe_ok` | `host`, `group`, `probe` | 1 if the probe passed at the last pass (`ssh` and `drift` included) |

For example, to alert on hosts in error: `bluebanquise_supervision_host_state{state="error"} == 1`.

## Files

| Path | Content |
|------|---------|
| `/etc/bluebanquise/bluebanquise-supervision/bluebanquise-supervision.yml` | Settings (paths, intervals, timeouts, ports) |
| `/etc/bluebanquise/bluebanquise-supervision/hosts.yml` | Supervised hosts: probes, actions, BMC credentials, expected values |
| `/etc/bluebanquise/bluebanquise-supervision/webui_users.yml` | WebUI users and password hashes |
| `/usr/lib/bluebanquise/bluebanquise-supervision/` | Shared Python code (`lib/`), probes, WebUI files |
| `/var/lib/bluebanquise-supervision/cluster/hosts/<host>/probes.yml` | Last probe pass results |
| `/var/lib/bluebanquise-supervision/cluster/hosts/<host>/gathered.yml` | Data gathered for the drift check |
| `/var/lib/bluebanquise-supervision/cluster/hosts/<host>/maintenance.yml` | Maintenance state |
| `/var/lib/bluebanquise-supervision/cluster/hosts/<host>/events.yml` | Events log |
| `/var/lib/bluebanquise-supervision/requests/<host>` | On-demand probe requests, read by the probe daemon |

Files are written atomically (temporary file, then rename), and changes to events and maintenance
are done under a per-host lock, so the daemons and the command line tool can work at the same time.

## Security

* Daemons run as the unprivileged `bluebanquise-supervision` user, never as root. The API and
  exporter services can only write in the data folder (systemd hardening). The probe daemon is not
  hardened the same way, so that actions can use sudo.
* The remote user (`bluebanquise` by default) has passwordless sudo on hosts: the private key of
  `bluebanquise-supervision` gives root access to supervised hosts. Keep the management host safe.
* SSH host keys are not checked nor stored (hosts are reinstalled often, and a changed key must not
  stop the supervision): keep supervision on a trusted management network.
* `hosts.yml` holds BMC credentials: readable by root and the `bluebanquise-supervision` group only.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `bluebanquise_supervision_checks` | `{}` | What to check, per group, see above |
| `bluebanquise_supervision_ssh_username` | `bluebanquise` | Default remote user |
| `bluebanquise_supervision_loop_interval` | `1800` | Seconds between two regular probe passes of all hosts |
| `bluebanquise_supervision_thread_pool_size` | `100` | Hosts probed in parallel |
| `bluebanquise_supervision_ssh_gate_timeout` | `10` | SSH connection timeout (seconds) |
| `bluebanquise_supervision_ssh_probe_timeout` | `60` | Timeout of a remote probe, and of the drift data gathering |
| `bluebanquise_supervision_local_probe_timeout` | `60` | Timeout of a local probe |
| `bluebanquise_supervision_action_timeout` | `60` | Timeout of an action |
| `bluebanquise_supervision_api_bind` / `_api_port` | `127.0.0.1` / `8091` | REST API and WebUI address |
| `bluebanquise_supervision_exporter_bind` / `_exporter_port` | `127.0.0.1` / `9810` | Prometheus exporter address |
| `bluebanquise_supervision_webui_users` | `[]` | WebUI users: `name`, `password_hash` |
| `bluebanquise_supervision_sudoers_commands` | `[]` | Commands the daemons user may run with sudo |
| `bluebanquise_supervision_log_level` | `INFO` | Daemons log level |
| `bluebanquise_supervision_enable_services` | `bb_enable_services`, else `true` | Enable services at boot |
| `bluebanquise_supervision_start_services` | `bb_start_services`, else `true` | Start (and restart on change) services |

## Debugging

Each daemon logs to the journal (`journalctl -u bluebanquise-supervision-probe`). To see every SSH
command run, start a daemon by hand with `--log-level DEBUG`, as root (it switches to the
`bluebanquise-supervision` user itself), after stopping its service.
