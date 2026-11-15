# Management

Management collection of roles for BlueBanquise collection set.

The `bluebanquise.infrastructure` collection deploys the cluster: provisioning, networks, base
services. This collection holds the tools used to run it once deployed: each role is a **pack**, a
few daemons with a JSON REST API and a small WebUI focused on one need.

All the WebUI packs are served by the Apache of the `bluebanquise.infrastructure.http_server`
role, under `/webui/<pack>/`, with one login for all of them. Apply `http_server` on the host
before any pack role.

## List of roles:

* [roles/bluebanquise_supervision](roles/bluebanquise_supervision): health probes, drift check,
  events and maintenance of every host, with a WebUI (`/webui/supervision/`), a REST API, a command
  line tool and a Prometheus exporter.

## Duplicated files

Some files are the same in every pack: the login module (`webui_auth.py`), the page layout
(`webui_base.html`), `bluebanquise-webui.js`, `bluebanquise-webui.css`, the users template
(`webui_users.yml.j2`) and `bulma.min.css`. They are copied on purpose, not shared through a
library: each pack works on its own.

Each copy starts with a `DUPLICATED FILE` header listing every copy, itself included. A change
must be made identically in every copy, and a new pack adds its copy to the list of every copy.
`bulma.min.css` stays the untouched vendor file, without header: all files of this name must be
identical. The CI checks both, run it before committing:

```
python3 resources/workflow/check_duplicated_files.py
```
