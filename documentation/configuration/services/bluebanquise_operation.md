# BlueBanquise operation

## Description

This role installs the **Operation** WebUI pack, at `http://<management host>/webui/operation/`:
power and next boot device of hosts, through their BMC, and their console logs.

* **Overview**: the power state of every host with a BMC (on, off, BMC error), as a map grouped by
  function group, and actions on a host or a nodeset: power on, off, reset, next boot device
  (PXE, disk, BIOS). Below, the last actions: who did what, when, and the result.
* **Host page**: power state and BMC of the host, the same actions, its **console log** (read
  only, followed every 2 seconds, BIOS screens readable), and its last actions.
* **Job page**: an action, with the result of every host, the command it ran and its logs.

The pack never talks to a BMC itself: every action, and every read of the power state, runs
`bluebanquise-power` (role `bluebanquise.infrastructure.bluebanquise_power`), and the console
logs are the ones written by conman (role `bluebanquise.infrastructure.conman`). What the WebUI
does can always be done, and debugged, by hand with the same command.

It runs two daemons, as the `conman` user of the conman role, which already holds the BMC
credentials, and is the only user able to read console logs:

* `bluebanquise-operation-api`: WebUI and REST API, served by the Apache of the `http_server`
  role;
* `bluebanquise-operation-worker`: runs the actions asked through the API, and reads the power
  state of every host every minute.

## Instructions

### 1. Apply http_server, conman and bluebanquise_power first

The role checks that `bluebanquise-power` and the `conman` user exist. Hosts managed by the pack
are the hosts of the bluebanquise-power configuration: a `bmc` entry and credentials in
`hw_board_authentication` (see the bluebanquise_power role), restricted to the same group
(`bluebanquise_power_restrict_to_group`, else `bb_restrict_to_group`). Console logs need the
host in conman too (a `bmc` entry with a `name`).

The role adds the `conman` user to two groups, each giving read access to one file:

* `bluebanquise-webui`, the WebUI users file;
* `bluebanquise-power` (created by the bluebanquise_power role), the bluebanquise-power
  configuration: the BMC credentials conman already has in `/etc/conman.conf`.

### 2. Packs and users

Shared by all WebUI packs, see the `bluebanquise_federator` role: add Operation to
`bluebanquise_webui_packs`, users are in `bluebanquise_webui_users`.

```yaml
bluebanquise_webui_packs:
  - name: cluster
    label: Cluster overview
  - name: operation
    label: Operation
```

Levels in Operation:

| Page or route | Level |
|---------------|-------|
| `GET /api/summary` (federator contract) | `viewer` |
| Everything else: pages, power state, actions, console logs, jobs | `operator` |

### 3. Apply the role

```yaml
- name: Management host
  hosts: management1
  roles:
    - role: bluebanquise.infrastructure.http_server
    - role: bluebanquise.infrastructure.conman
    - role: bluebanquise.infrastructure.bluebanquise_power
    - role: bluebanquise.management.bluebanquise_federator
    - role: bluebanquise.management.bluebanquise_operation
```

Applying the role restarts the worker when its files change: a power action running at that
moment is stopped, and its job ends failed. Do not apply it during a large power on.

## How it works

1. A click on "Reset" sends `POST api/power {"hosts": "c[001-004]", "action": "reset"}`. The API
   checks the user, the hosts (all must be hosts of the pack) and that no running action already
   holds one of them (two clicks give one action), writes the job file and a request file,
   writes an AUDIT line, and answers `202` with the job.
2. The worker sees the request within a second and runs:
   `bluebanquise-power --json --parallel 16 c[001-004] power reset`, its result (stdout) going to
   the job result file, its logs (stderr) to the job log file. Several actions run at the same
   time.
3. When bluebanquise-power ends, the worker reads its result (`{"nodes": {"c001": {"ok": true,
   "detail": "reset"}, ...}}`), and ends the job: `success` when every host is ok, else `failed`,
   with the result of every host.
4. The page follows the job (`GET api/jobs/<job>` every second) and shows the result.
5. Every minute, and 5, 15 and 30 seconds after a power action, the worker runs
   `bluebanquise-power --json <hosts> power status` and writes the power state of every host.

## How the state of a host is given to the federator

| Power state | State | Text |
|-------------|-------|------|
| on | `ok` (green) | `on` |
| off | `ok` (green) | `off` |
| the BMC did not answer | `error` (red) | `BMC error: ...` |
| not read yet, or another state | `unknown` (grey) | |

A host powered off is not an error for Operation: whether it should be on is the job of
Supervision, which shows it red (or blue, in maintenance). The Operation pages show off hosts in
dark grey. A BMC that does not answer is an error: the host can not be powered on or off from the
WebUI.

## REST API

Routes below are relative to `http://<management host>/webui/operation/`. All of them need HTTP
basic authentication. POST requests must be JSON (`Content-Type: application/json`).

| Method | Route | Level | Description |
|--------|-------|-------|-------------|
| GET | `/api/summary` | viewer | Power state of the cluster and of every host (federator contract) |
| GET | `/api/hosts` | operator | Power state of every host, and counts |
| GET | `/api/hosts/<host>` | operator | Power state and BMC of a host |
| GET | `/api/hosts/<host>/summary` | operator | Power state of a host (federator contract), plus `power`: `on`, `off` or `null` |
| GET | `/api/hosts/<host>/console` | operator | Console log, `?offset=<n>&inode=<n>` for only what is new |
| POST | `/api/power` | operator | `{"hosts": "<nodeset>", "action": "on\|off\|reset"}`, answers `202` and a job |
| POST | `/api/boot` | operator | `{"hosts": "<nodeset>", "device": "pxe\|disk\|bios"}`, answers `202` and a job |
| GET | `/api/jobs` | operator | Last 50 jobs, the newest first, `?host=<host>` for the jobs of a host |
| GET | `/api/jobs/<job>` | operator | A job: `state` (`running`, `success`, `failed`), `message`, `results` per host, `command` |
| GET | `/api/jobs/<job>/log` | operator | Logs of the bluebanquise-power command of a job (its stderr) |

`hosts` is a host or a nodeset of hosts of the pack: names, ranges and lists
(`c[001-004],login1`), no `@group`.

Console log answers: `{"offset": ..., "inode": ..., "reset": ..., "text": "..."}`. The first call,
without `offset`, gives the last 64 KiB. Each next call gives what was written since `offset`, at
most 256 KiB. When the log was rotated (new inode, or smaller file), the new file is read from its
start and `reset` is true. Escape sequences (colors, cursor moves) and control characters are
removed.

Examples:

```
curl -u jdoe http://127.0.0.1/webui/operation/api/hosts/c001
curl -u jdoe -H 'Content-Type: application/json' -d '{"hosts": "c[001-004]", "action": "reset"}' http://127.0.0.1/webui/operation/api/power
curl -u jdoe http://127.0.0.1/webui/operation/api/jobs/<job>
```

## Files

| Path | Content |
|------|---------|
| `/etc/bluebanquise/bluebanquise-operation/bluebanquise-operation.yml` | Settings (port, prefix, intervals, bluebanquise-power options) |
| `/etc/bluebanquise/bluebanquise-operation/hosts.yml` | Hosts of the pack: function group, BMC, protocol (no credentials) |
| `/etc/bluebanquise/webui/users.yml` | WebUI users, levels and password hashes, shared by all WebUI packs |
| `/var/lib/bluebanquise-operation/power.yml` | Power state of every host, written by the worker |
| `/var/lib/bluebanquise-operation/power-status.json` | Result of the last `bluebanquise-power --json ... power status` |
| `/var/lib/bluebanquise-operation/power-status.log` | Logs of the last `bluebanquise-power --json ... power status` |
| `/var/lib/bluebanquise-operation/jobs/<job>.yml` | A job (kept 7 days) |
| `/var/lib/bluebanquise-operation/jobs/<job>.json` | Result of the bluebanquise-power command of a job |
| `/var/lib/bluebanquise-operation/jobs/<job>.log` | Logs of the bluebanquise-power command of a job |
| `/var/lib/bluebanquise-operation/requests/<job>` | A job waiting for the worker |
| `/var/log/conman/<host>.log` | Console logs, written by conmand (conman role) |
| `/usr/lib/bluebanquise/bluebanquise-operation/` | Shared Python code (`lib/`), WebUI files (`webui/`) |
| `/usr/sbin/bluebanquise-operation-api`, `/usr/sbin/bluebanquise-operation-worker` | The daemons |
| `<Apache configuration folder>/bluebanquise-webui-operation.conf` | Apache proxy to the API daemon, under `/webui/operation/` |

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `bluebanquise_operation_api_port` | `8092` | WebUI and REST API daemon port, on `127.0.0.1` |
| `bluebanquise_operation_status_interval` | `60` | Seconds between two reads of the power state of every host |
| `bluebanquise_operation_power_parallel` | `16` | `--parallel` of bluebanquise-power: hosts handled at the same time |
| `bluebanquise_operation_power_delay` | `0` | `--delay` of bluebanquise-power: seconds between two hosts powered on or reset, against the power surge |
| `bluebanquise_webui_packs` | Operation only | Packs of the menu, shared by all packs |
| `bluebanquise_webui_users` | `[]` | WebUI users, shared by all packs |
| `bluebanquise_operation_log_level` | `INFO` | Daemons log level |
| `bluebanquise_operation_enable_services` | `bb_enable_services`, else `true` | Enable the services at boot |
| `bluebanquise_operation_start_services` | `bb_start_services`, else `true` | Start (and restart on change) the services |

## Debugging

* An action failed: open its job page (click its time in "Last actions"). The logs of
  bluebanquise-power hold a BMC debug report for each failed host. Replay the command of the job
  as the `conman` user, without `--json` to get the usual table:
  `sudo -u conman bluebanquise-power c001 power status` (add `--debug` to see the exact ipmitool
  or Redfish commands, passwords included).
* Power states look old (grey): the worker reads them every minute,
  `journalctl -u bluebanquise-operation-worker`, and the result and logs of the last read are in
  `/var/lib/bluebanquise-operation/power-status.json` and `power-status.log`.
* No console log: the host must be in `/etc/conman.conf`, and conmand running
  (`systemctl status conman`). The console of a host is in `/var/log/conman/<host>.log`.
* Every write action writes an AUDIT line:
  `journalctl -u bluebanquise-operation-api -o cat | grep '^AUDIT'`.
* To start a daemon by hand, stop its service, then run it as conman:
  `sudo -u conman /usr/sbin/bluebanquise-operation-worker --log-level DEBUG`.
* Each page is one file of `/usr/lib/bluebanquise/bluebanquise-operation/webui/templates/`, with
  its HTML and its JavaScript. Every call of a page can be replayed with `curl` (examples above).
