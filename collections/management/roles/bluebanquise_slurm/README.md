# BlueBanquise slurm

## Description

This role installs the **Slurm** WebUI pack, at `http://<management host>/webui/slurm/`: state of
the Slurm nodes, and drain or resume of a node or a nodeset.

* **Overview**: counts (nodes in production, drained, down, CPUs allocated, jobs running and
  pending), the nodes as a map grouped by function group, the nodes out of production with their
  reason, drain and resume on a nodeset, and the last actions: who did what, when, and the
  result.
* **Node page**: Slurm state, reason and its date, partitions, drain and resume.
* **Job page**: an action, with the result of every node.

A drain needs a reason. Slurm records it as `[<WebUI user>] <reason>`, so `sinfo -R` tells who
drained a node.

Pages never call Slurm: the state of the nodes is read every 30 seconds by a daemon, and right
after each action.

## Security

Draining a node needs a Slurm administrator: an unprivileged user gets
`slurm_update error: Invalid user id`, and the SlurmUser can do anything (set a whole partition
down, cancel every job). The pack never gets that power:

* **The node wrapper**, `/usr/lib/bluebanquise/bluebanquise-slurm/bluebanquise-slurm-node`, owned
  by root, does only three things, and checks every argument itself:
  * `status`: `sinfo` and `squeue`, as JSON (also with `PrivateData=jobs`, where an unprivileged
    user sees no job);
  * `drain <node> <reason>`: the node must be in `sinfo`, the reason must be one line of at most
    200 characters, not starting with `-`;
  * `resume <node>`.
* **Two users, one per daemon:**
  * `bluebanquise-slurm` runs `bluebanquise-slurm-worker`. Its only power is one sudo rule
    (`/etc/sudoers.d/bluebanquise-slurm`): run the wrapper as the SlurmUser. The rule opens no PAM
    session (`!pam_session`): sudo logs one line per call, with the command line. sudo-rs
    (Ubuntu 26.04) has no such setting: the rule is then written without it.
  * `bluebanquise-slurm-api` runs `bluebanquise-slurm-api`, the WebUI and REST API. It has no
    sudo rule and runs no Slurm command: it reads the files of the worker (group
    `bluebanquise-slurm`), and writes requests. Its systemd unit lets it write into the requests
    folder only.

A bug in the WebUI can then at most ask for a drain or a resume of a Slurm node, with a reason
the wrapper checks again.

## Instructions

### 1. Apply http_server and slurm first

The pack runs Slurm commands on the management host: apply the
`bluebanquise.infrastructure.slurm` role there first (`controller` or `submitter` profile), and
`bluebanquise.infrastructure.http_server`. The role checks that the SlurmUser (`slurm`) exists.

### 2. Packs and users

Shared by all WebUI packs, see the `bluebanquise_federator` role: add Slurm to
`bluebanquise_webui_packs`, users are in `bluebanquise_webui_users`.

```yaml
bluebanquise_webui_packs:
  - name: cluster
    label: Cluster overview
  - name: slurm
    label: Slurm
```

Levels in Slurm:

| Page or route | Level |
|---------------|-------|
| `GET /api/summary` (federator contract) | `viewer` |
| Everything else: pages, nodes, drain, resume, jobs | `operator` |

### 3. Apply the role

```yaml
- name: Management host
  hosts: management1
  roles:
    - role: bluebanquise.infrastructure.http_server
    - role: bluebanquise.infrastructure.slurm
      vars:
        slurm_profile: controller
    - role: bluebanquise.management.bluebanquise_federator
    - role: bluebanquise.management.bluebanquise_slurm
```

## How it works

1. A click on "Drain" sends `POST api/drain {"hosts": "c[001-004]", "reason": "disk swap"}`. The
   API checks the user, the nodes (all must be Slurm nodes), the reason, and that no running
   action already holds one of the nodes, writes a request file and an AUDIT line, and answers
   `202` with the job.
2. The worker sees the request within a second, writes the job, and runs for each node, one after
   the other:
   `sudo -n -u slurm /usr/lib/bluebanquise/bluebanquise-slurm/bluebanquise-slurm-node drain c001 "[jdoe] disk swap"`.
   The job ends `success` when every node is done, else `failed`, with the result of every node.
3. The page follows the job (`GET api/jobs/<job>` every second) and shows the result.
4. Every 30 seconds, right after a job and 5 seconds later (a resumed node is "not responding"
   until slurmctld pings it), the worker runs the wrapper `status` and writes the state of every
   node.

## How the state of a node is given to the federator

| Slurm state (`sinfo %T`) | State | Text |
|--------------------------|-------|------|
| idle, allocated, mixed, completing, reserved... | `ok` (green) | the Slurm state |
| drained, draining | `maintenance` (blue) | the Slurm state and the reason |
| down, fail, failing, or not responding (`*`) | `error` (red) | the Slurm state and the reason |
| unknown | `unknown` (grey) | |

The host summary also gives `drained`: `true` once a drained node has no job left (a draining node
still runs jobs), for Automation. Slurm keeps the reason after a resume: it is shown only for a
node out of production.

When the worker can not read Slurm (slurmctld stopped...), the pages say why, and the states get
old (grey after 90 seconds).

## REST API

Routes below are relative to `http://<management host>/webui/slurm/`. All of them need HTTP basic
authentication. POST requests must be JSON (`Content-Type: application/json`).

| Method | Route | Level | Description |
|--------|-------|-------|-------------|
| GET | `/api/summary` | viewer | State of the cluster and of every node (federator contract) |
| GET | `/api/hosts` | operator | State of every node, counts, CPUs, jobs, and `error` when Slurm could not be read |
| GET | `/api/hosts/<host>` | operator | State of a node: Slurm state, reason and its date, partitions |
| GET | `/api/hosts/<host>/summary` | operator | State of a node (federator contract), plus `slurm_state`, `reason`, `drained` |
| POST | `/api/drain` | operator | `{"hosts": "<nodeset>", "reason": "..."}`, answers `202` and a job |
| POST | `/api/resume` | operator | `{"hosts": "<nodeset>"}`, answers `202` and a job |
| GET | `/api/jobs` | operator | Last 50 jobs, the newest first, `?host=<host>` for the jobs of a node |
| GET | `/api/jobs/<job>` | operator | A job: `state` (`running`, `success`, `failed`), `message`, `results` per node |

`hosts` is a node or a nodeset of Slurm nodes: names, ranges and lists (`c[001-004],login1`), no
`@group`. The reason is at most 200 characters with its `[<user>] ` prefix.

Examples:

```
curl -u jdoe http://127.0.0.1/webui/slurm/api/hosts/c001/summary
curl -u jdoe -H 'Content-Type: application/json' -d '{"hosts": "c[001-004]", "reason": "disk swap"}' http://127.0.0.1/webui/slurm/api/drain
curl -u jdoe http://127.0.0.1/webui/slurm/api/jobs/<job>
```

## Files

| Path | Content |
|------|---------|
| `/etc/bluebanquise/bluebanquise-slurm/bluebanquise-slurm.yml` | Settings (port, prefix, refresh interval, users) |
| `/etc/bluebanquise/bluebanquise-slurm/hosts.yml` | Hosts of the inventory and their function group, for the map |
| `/etc/sudoers.d/bluebanquise-slurm` | The sudo rule of the worker |
| `/etc/bluebanquise/webui/users.yml` | WebUI users, levels and password hashes, shared by all WebUI packs |
| `/var/lib/bluebanquise-slurm/state.yml` | State of every node, CPUs and jobs, written by the worker |
| `/var/lib/bluebanquise-slurm/requests/<job>.yml` | An action asked through the API, waiting for the worker |
| `/var/lib/bluebanquise-slurm/jobs/<job>.yml` | A job (kept 7 days), written by the worker |
| `/usr/lib/bluebanquise/bluebanquise-slurm/bluebanquise-slurm-node` | The node wrapper |
| `/usr/lib/bluebanquise/bluebanquise-slurm/` | Shared Python code (`lib/`), WebUI files (`webui/`) |
| `/usr/sbin/bluebanquise-slurm-api`, `/usr/sbin/bluebanquise-slurm-worker` | The daemons |
| `<Apache configuration folder>/bluebanquise-webui-slurm.conf` | Apache proxy to the API daemon, under `/webui/slurm/` |

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `bluebanquise_slurm_api_port` | `8095` | WebUI and REST API daemon port, on `127.0.0.1` |
| `bluebanquise_slurm_refresh_interval` | `30` | Seconds between two reads of the state of the nodes |
| `bluebanquise_webui_packs` | Slurm only | Packs of the menu, shared by all packs |
| `bluebanquise_webui_users` | `[]` | WebUI users, shared by all packs |
| `bluebanquise_slurm_log_level` | `INFO` | Daemons log level |
| `bluebanquise_slurm_enable_services` | `bb_enable_services`, else `true` | Enable the services at boot |
| `bluebanquise_slurm_start_services` | `bb_start_services`, else `true` | Start (and restart on change) the services |

## Debugging

* An action failed: open its job page (click its time in "Last actions"): the result of each node
  says why (refused by the wrapper, or the error of `scontrol`). Replay it as the worker does:
  `sudo -u bluebanquise-slurm sudo -n -u slurm /usr/lib/bluebanquise/bluebanquise-slurm/bluebanquise-slurm-node drain c001 "[jdoe] test"`.
* The pages say Slurm could not be read: the error is the one of `sinfo` or `squeue`. Check
  slurmctld (`scontrol ping`), and replay the status:
  `sudo -u slurm /usr/lib/bluebanquise/bluebanquise-slurm/bluebanquise-slurm-node status`.
* The worker logs every action, the API every request it refuses:
  `journalctl -u bluebanquise-slurm-worker -u bluebanquise-slurm-api`. Every write action writes
  an AUDIT line: `journalctl -u bluebanquise-slurm-api -o cat | grep '^AUDIT'`. sudo also logs
  every call of the wrapper in the journal.
* To start a daemon by hand, stop its service, then run it as its user:
  `sudo -u bluebanquise-slurm /usr/sbin/bluebanquise-slurm-worker --log-level DEBUG`.
* Each page is one file of `/usr/lib/bluebanquise/bluebanquise-slurm/webui/templates/`, with its
  HTML and its JavaScript. Every call of a page can be replayed with `curl` (examples above).
