# community/podman

Ansible role for setting up [podman](https://podman.io) in Bluebanquise environment.

This role is compatible with HA clusters:
* For active/active configuration please refer to the documentation since you need create 'bundles' to launch your containers: [How to create pacemaker container bundles using podman](https://access.redhat.com/solutions/3871591).
* For active/passive cluster, it is possible to use systemd services to launch containers, and then use pacemaker to manage the systemd containers. An example of this is the registry container deployed by this role. Note that the clients of the registry should use a virtual IP address managed by pacemaker.

## Supported Platforms

* RedHat 8
* CentOS 8
* Ubuntu 18.04 & 20.04

## Requirements

Ansible 2.7 or higher is required for defaults/main/*.yml to work correctly.

## Known Limitations

When firewalld is running, containers deployed with podman may lose connectivity if the firewall rules are reloaded with the `firewall-cmd --reload` command, due to non-persistent rules added by podman being lost. As a workaround, the following command should be used after reloading the firewall, it will restore container connectivity without having to re-deploy the containers:

```
podman network reload --all
```

## Variables

Variables for this role:

| variable | defaults/main/*.yml | type | description |
| -------- | ------------------- | ---- | ----------- |
| podman_configure | True | boolean | use default configuration when False, write config, when True |
| podman_configure_local_registry | False | boolean | starts a default local registry when True |
| podman_configure_ha | False | boolean | configure podman for a HA cluster |
| podman_users | { root: '100000:65535' } | dictionary | podman users that get uid mapping configured, those users MUST exist on the system before running this role |
| podman_manual_mapping | False | boolean | ansible managed /etc/subuid and /etc/subgid entries |
| podman_search_registries | - 'docker.io' | items | list of registries that podman is pulling images from |
| podman_insecure_registries | [] | items | non TLS registries for podman, i.e. localhost:5000 |
| podman_blocked_registries | [] | items | blocked container registries |
| podman_local_registry_dir | "/var/lib/registry" | String | default local registry path when enabled |
| podman_local_registry_port | 5000 | integer | port of the local registry when enabled |
| podman_registry_container_path | /var/www/html/images/registry-2.tgz | String | path of the container used to spawn to default local registry when enabled |
| podman_conf_cgroup_manager | 'systemd' | string | /etc/container/libpod.conf: cgroup_manager |
| podman_conf_events_logger | 'file' | string | /etc/container/libpod.conf: events_logger, due to podman error with journald, see [issue](https://github.com/containers/libpod/issues/3126) |
| podman_conf_namespace | '' | string | /etc/container/libpod.conf: namespace (=default namespace) |
| podman_storage_driver | 'overlay' | string | storage driver |
| podman_storage_mountopt | 'nodev' | string | storage driver mount options |

## Dependencies

None.

## Example Playbook

For a basic setup with default values run:

```yaml
---
- hosts: management1
  vars:
    podman_configure_local_registry: True
    podman_users:
      root: '100000:65535'
      guest: '1000:1000'
      ...
    podman_insecure_registries:
      - 'localhost:5000'
    podman_search_registries:
      - 'registry.access.redhat.com'
  roles:
    - role: podman
```

## Local registry

In order to deploy the optionnal local registry, you must provide the container for it. 
This is done wih the following steps from your local PC or from a server with Internet access:

* Using Docker

```shell
docker pull registry:2
docker save registry:2 | gzip > registry-2.tgz
scp registry-2 root@<management1>:/var/www/html/images/registry-2.tgz
```

* Using podman

```shell
podman pull registry:2
podman save registry:2 | gzip > registry-2.tgz
scp registry-2 root@<management1>:/var/www/html/images/registry-2.tgz
```

To deploy the local registry, you must customize the following variables when calling the role:

```yaml
podman_configure_local_registry: true

####################
# registries section
####################
podman_search_registries:
  - 'localhost:5000'
  - 'docker.io'
podman_insecure_registries:
  - 'localhost:5000'
podman_local_registry_dir: "/var/lib/registry"
podman_local_registry_port: 5000
podman_registry_container_path: "/var/www/html/images/registry-2.tgz"
podman_registry_container: "registry"
podman_registry_container_tag: "2"
podman_local_registry_owner: "root"
podman_local_registry_group: "root"
```

## License and Author

* Author:: @strus38
