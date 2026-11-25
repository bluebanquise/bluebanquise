# BlueBanquise federator

## Description

This role installs the **cluster overview** of the BlueBanquise WebUI packs, at
`http://<management host>/webui/cluster/`, and makes `http://<management host>/webui/` open it.

Each WebUI pack of the `bluebanquise.management` collection (Supervision, and the next ones) shows
one view of the cluster. The federator puts them side by side:

* **Overview**: one tile per pack, with the state of the cluster seen by that pack and the age of
  its data, then the **cluster map**: one small square per host of the inventory, grouped by
  function group, colored by the states given by every pack. Hover a square to read what each
  pack says about the host, click it to open the host page.
* **Host page**: one tile per pack, with the state of the host in that pack. Click a tile to open
  the page of the host in that pack. Below, the inventory facts of the host: groups and network
  interfaces.
* **Packs page**: for each pack, reachable or not, its version, its contract version, the age of
  its data and its refresh period. Look here first when a page shows "unavailable" or old data,
  and copy this table in a bug report.

The federator holds no data and no secret, and never calls the other packs itself: its pages are
filled by the browser, which calls the API of each pack with the user's own login. A pack that is
stopped or slow shows "unavailable" in its tile (after 10 seconds at most), and the rest of the
page works.

It runs one daemon, `bluebanquise-federator`, as the dedicated unprivileged
`bluebanquise-federator` user, served by the Apache of the `http_server` role.

## Instructions

### 1. Apply http_server first

The WebUI is served by the Apache of the `bluebanquise.infrastructure.http_server` role: apply it
on the host before this role (the role checks it). The daemon itself listens on `127.0.0.1` only.

### 2. List the packs

The packs of the left menu, the tiles of the overview and the rows of the packs page all come from
one inventory variable, shared by all WebUI packs. Set it once, for example in
`group_vars/all`. The federator is the entry named `cluster`, written first by convention:

```yaml
bluebanquise_webui_packs:
  - name: cluster              # URL is /webui/<name>/
    label: Cluster overview
  - name: supervision
    label: Supervision
```

When not set, the menu shows only the federator, and the overview has no tile.

### 3. Users

Users are shared by all WebUI packs: see the `bluebanquise_webui_users` variable in the
[bluebanquise_supervision README](../bluebanquise_supervision/README.md#3-create-webui-users).
Levels in the federator:

| Page | Level |
|------|-------|
| Overview (`/webui/cluster/`), packs page | `viewer` |
| Host pages | `operator` |

A viewer sees the overview and the cluster map, without links to host pages.

### 4. Apply the role

```yaml
- name: Management host
  hosts: management1
  roles:
    - role: bluebanquise.infrastructure.http_server
    - role: bluebanquise.management.bluebanquise_federator
    - role: bluebanquise.management.bluebanquise_supervision
```

## How the map is colored

Each pack gives a state for the hosts it knows: `ok`, `error`, `maintenance` or `unknown`. The
square of a host takes the most important state given by the packs:

1. `maintenance` (blue): someone works on the host, an error is then expected;
2. `error` (red): something needs an action;
3. `unknown` (grey): a pack does not know the state, or its data is old;
4. `ok` (green): every pack says ok.

A pack that has nothing to say about a host (a storage server in a Slurm pack) does not count.
A host that no pack knows is grey. A pack that does not answer is not used: it is listed above the
map ("Not on the map: ..."), and its tile says "unavailable".

**Old data turns grey**, never stays green: data older than 3 times the refresh period of its
pack (for Supervision, its probe loop interval) is shown as "old data". Ages are computed with
the clock of the browser: keep the clocks of the admins' computers right.

## Summary contract

Every pack answers two routes for the federator (contract version 1), read by the browser:

* `GET /webui/<pack>/api/summary` (viewer level): the state of the cluster and of every host:

```
{"contract": 1, "pack": "supervision", "version": "1.1.0", "as_of": 1794746670, "refresh": 1800,
 "cluster": {"state": "error", "text": "510 ok, 2 error"},
 "hosts": {"c001": {"state": "ok", "text": "ok", "url": "hosts/c001", "as_of": 1794746670}}}
```

* `GET /webui/<pack>/api/hosts/<host>/summary` (operator level): the same entry for one host, plus
  `contract` and `refresh`. `404` (as JSON) when the pack has nothing to say about the host.

`as_of` is the time of the data, in seconds since 1970, `refresh` the seconds between two
refreshes of the data, `url` the page of the host in the pack (relative to the pack). Fields are
only ever added: an incompatible change would be `"contract": 2`, reported on the packs page.

## REST API

Routes below are relative to `http://<management host>/webui/cluster/`. All of them need HTTP
basic authentication.

| Method | Route | Level | Description |
|--------|-------|-------|-------------|
| GET | `/api/hosts` | viewer | Hosts of the inventory, with their function group |
| GET | `/api/hosts/<host>` | operator | Groups and network interfaces of a host |

## Files

| Path | Content |
|------|---------|
| `/etc/bluebanquise/bluebanquise-federator/bluebanquise-federator.yml` | Settings (port, prefix, packs of the menu) |
| `/etc/bluebanquise/bluebanquise-federator/hosts.yml` | Hosts of the inventory, with their groups and network interfaces |
| `/etc/bluebanquise/webui/users.yml` | WebUI users, levels and password hashes, shared by all WebUI packs |
| `/usr/lib/bluebanquise/bluebanquise-federator/` | Shared Python code (`lib/`), WebUI files (`webui/templates/` pages, `webui/static/` CSS and JavaScript) |
| `/usr/sbin/bluebanquise-federator` | The daemon |
| `<Apache configuration folder>/bluebanquise-webui-federator.conf` | Apache proxy to the daemon, under `/webui/cluster/`, and the `/webui/` redirection |

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `bluebanquise_federator_api_port` | `8090` | WebUI daemon port, on `127.0.0.1` |
| `bluebanquise_webui_packs` | the federator only | Packs of the menu and of the tiles: `name`, `label`. Shared by all packs |
| `bluebanquise_webui_users` | `[]` | WebUI users: `name`, `password_hash`, `role`. Shared by all packs |
| `bluebanquise_federator_log_level` | `INFO` | Daemon log level |
| `bluebanquise_federator_enable_services` | `bb_enable_services`, else `true` | Enable the service at boot |
| `bluebanquise_federator_start_services` | `bb_start_services`, else `true` | Start (and restart on change) the service |

## Debugging

* A tile says "unavailable": its error tells why. `HTTP error 503`: the daemon of the pack is
  stopped (`systemctl status bluebanquise-<pack>-api`). `HTTP error 404`: the pack is in
  `bluebanquise_webui_packs` but not installed on this host. `not reachable (signal timed out)`:
  the pack did not answer within 10 seconds.
* The daemon logs to the journal: `journalctl -u bluebanquise-federator`. To start it by hand,
  stop the service, then run it as its user:
  `sudo -u bluebanquise-federator /usr/sbin/bluebanquise-federator --log-level DEBUG`.
* Each page is one file of `/usr/lib/bluebanquise/bluebanquise-federator/webui/templates/`, with its
  HTML and its JavaScript. Fields of a page have an `id`, filled one by one by a `load` function.
  Every call of a page can be replayed with `curl`, for example
  `curl -u jdoe http://127.0.0.1/webui/supervision/api/summary`.
