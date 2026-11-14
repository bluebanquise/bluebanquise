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
