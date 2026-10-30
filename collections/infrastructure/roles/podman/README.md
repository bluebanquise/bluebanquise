# Podman

## Description

This role installs [podman](https://podman.io), configures registries and container engine settings, and can deploy a local
container registry.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

The role does not replace the distribution configuration files. It adds drop-in files, which override only the settings they define:

* `/etc/containers/registries.conf.d/50-bluebanquise.conf`, see `containers-registries.conf.d(5)`.
* `/etc/containers/containers.conf.d/50-bluebanquise.conf`, see `containers.conf(5)`.

Only `/etc/containers/storage.conf` (no drop-in support) is fully written, and only when `podman_storage_driver` is set.

## Instructions

### Registries

```yaml
podman_search_registries:     # Registries searched for short image names (myimage:1.0), in order
  - registry.cluster.local:5000
  - docker.io
podman_insecure_registries:   # Registries reached using HTTP, or HTTPS without certificate check
  - registry.cluster.local:5000
podman_blocked_registries:    # Registries images cannot be pulled from
  - quay.io
```

When `podman_search_registries` is empty (default), the distribution search list is kept.

### Container engine settings

`podman_conf_cgroup_manager`, `podman_conf_events_logger` and `podman_conf_namespace` set the corresponding
`[engine]` settings when defined. Any other setting can be added as raw TOML content:

```yaml
podman_containers_conf_content: |
  [containers]
  log_size_max = 10485760
  pids_limit = 4096
```

### Storage

When `podman_storage_driver` is set (for example `overlay`), `/etc/containers/storage.conf` is written with this
driver, and `podman_storage_mountopt` (for example `nodev`) as overlay mount options if set. Otherwise, the
distribution storage configuration is used.

Changing the storage driver of a host where podman was already used makes podman fail
(`database configuration mismatch`): existing containers and images must then be removed with `podman system reset`.

### Rootless containers

Users running rootless containers need subordinate uids and gids ranges, in `/etc/subuid` and `/etc/subgid`.
Users created with `useradd` usually get one automatically. To set them explicitly (`start:count`):

```yaml
podman_users:
  alice: "200000:65536"
  bob: "265536:65536"
```

Ranges must not overlap with each other, nor with ranges already set by `useradd` (check `/etc/subuid`).

### Local registry

The role can deploy a local registry, running as a container managed by the `registry` systemd service, and
storing images in `podman_local_registry_dir`. As management hosts usually have no internet access, the registry
image must be provided as an archive. From a host with internet access:

```shell
podman pull docker.io/library/registry:2
podman save docker.io/library/registry:2 | gzip > registry-2.tgz
scp registry-2.tgz root@<management1>:/var/www/html/images/registry-2.tgz
```

Then set:

```yaml
podman_configure_local_registry: true
podman_insecure_registries:
  - mgt1:5000
```

The archive is loaded only if the image is not already present. The registry port is opened in the firewall.

### Known limitations

* When the firewall rules are reloaded (`firewall-cmd --reload`), rootful containers may lose connectivity, as rules
  added by podman are not persistent. Run `podman network reload --all` after reloading the firewall.
* For active/active HA clusters, containers must be managed by pacemaker using bundles. For active/passive clusters,
  pacemaker can manage the systemd service of the container, like the `registry` service.

### Upgrade from role versions 2.x

Role versions 2.x replaced `/etc/containers/containers.conf`, `/etc/containers/registries.conf`,
`/etc/containers/storage.conf` and users `~/.config/containers/containers.conf` with their own content.

* `/etc/containers/containers.conf`, and `/etc/containers/storage.conf` when `podman_storage_driver` is not set,
  are removed when they were written by the role (they contain `Ansible managed`), so that distribution defaults apply again.
* `/etc/containers/registries.conf` is left in place, as distributions ship it in `/etc` only. To restore the
  distribution file, reinstall the package owning it (`rpm -qf /etc/containers/registries.conf` or
  `dpkg -S /etc/containers/registries.conf`), or restore the `registries.conf.*~` backup made by the role.
* Users `~/.config/containers/containers.conf` files containing `Ansible managed` should be removed manually: they use
  the `k8s.gcr.io/pause:3.1` infra image, from the frozen `k8s.gcr.io` registry.
* The registry service published the registry on port 5000 only, ignoring `podman_local_registry_port`, and mounted
  `/var/lib/registry` only, ignoring `podman_local_registry_dir`. Both are now honored. The registry container
  does not run privileged anymore, and uses the default podman network instead of `slirp4netns` (deprecated, and
  not installed with podman 5).
* Variables `podman_configure`, `podman_configure_ha`, `podman_manual_mapping`, `podman_sudo_user` and
  `podman_local_registry_host` are not used anymore: the role fails if they are still set, remove them from the inventory.
  `podman_users` now only sets `/etc/subuid` and `/etc/subgid` entries, without removing other entries.
* `podman-compose` is not installed anymore on RHEL (only available from EPEL). Add it to `podman_packages_to_install` if needed.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `podman_packages_to_install` | `[podman]` | Packages to install. |
| `podman_search_registries` | `[]` | Registries searched for short image names. Empty: distribution default. |
| `podman_insecure_registries` | `[]` | Registries reached without TLS or certificate check. |
| `podman_blocked_registries` | `[]` | Blocked registries. |
| `podman_conf_cgroup_manager` | not set | `[engine]` `cgroup_manager`. |
| `podman_conf_events_logger` | not set | `[engine]` `events_logger`. |
| `podman_conf_namespace` | not set | `[engine]` `namespace`. |
| `podman_containers_conf_content` | not set | Raw TOML content added to the containers.conf drop-in. |
| `podman_storage_driver` | not set | Storage driver. Not set: distribution storage configuration. |
| `podman_storage_mountopt` | not set | Overlay mount options, used with `podman_storage_driver`. |
| `podman_users` | `{}` | Users subordinate uids and gids ranges (`user: "start:count"`). |
| `podman_configure_local_registry` | `false` | Deploy a local registry. |
| `podman_local_registry_dir` | `/var/lib/registry` | Local registry storage directory. |
| `podman_local_registry_port` | `5000` | Local registry port. |
| `podman_local_registry_owner` | `root` | Owner of the local registry storage directory. |
| `podman_local_registry_group` | `root` | Group of the local registry storage directory. |
| `podman_registry_container_path` | `/var/www/html/images/registry-2.tgz` | Registry image archive. |
| `podman_registry_container` | `registry` | Registry image name. |
| `podman_registry_container_tag` | `2` | Registry image tag. |
| `podman_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open the local registry port in. |
| `podman_enable_services` | `bb_enable_services`, else `true` | Enable the registry service. |
| `podman_start_services` | `bb_start_services`, else `true` | Start the registry service, and restart it on changes. |

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 2.0.0: Updated registry format;Use handlers;Replace libpod.conf. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.0.3: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Fix services to match bb 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Use slirp4netns to avoid error with HA. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.0.0: Role creation. @strus38
