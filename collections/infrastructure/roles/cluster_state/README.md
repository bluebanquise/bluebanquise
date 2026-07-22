# cluster_state

## Description

This role collects static host data from the Ansible inventory and writes it to per-host YAML files under `/var/lib/bluebanquise/cluster/hosts/`. It is part of the BlueBanquise cluster state tracking system.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Output structure

For each host in the target group, the role creates:

```
/var/lib/bluebanquise/cluster/hosts/
  <hostname>/
    static_cluster_state.yml
/var/lib/bluebanquise/cluster/
  .tmp/                          <- shared tmp directory for atomic writes by daemons
```

Each `static_cluster_state.yml` contains the fields described below. Only fields present in the inventory are written — optional fields are omitted when undefined.

## Instructions

Run this role on the management node. It reads from `hostvars` (inventory data) and writes files locally — no SSH connection to target hosts is required.

```yaml
- hosts: fn_management
  roles:
    - bluebanquise.infrastructure.cluster_state
```

Re-run whenever the inventory changes to refresh the static snapshot.

### Processed fields

| Field | Source | Required |
|-------|--------|----------|
| `hostname` | host name | always |
| `ansible_groups.function` | `fn_*` group membership | always |
| `ansible_groups.hardware` | `hw_*` group membership | always |
| `ansible_groups.os` | `os_*` group membership | always |
| `network_interfaces` | host vars `network_interfaces` (`interface` key renamed to `name`) | always |
| `bmc` | host vars `bmc` | optional |
| `cpu.architecture` | `hw_specs.cpu.architecture` or `hw_architecture` | optional |
| `cpu.sockets` | `hw_specs.cpu.sockets` | optional |
| `cpu.cores_per_socket` | `hw_specs.cpu.cores_per_socket` | optional |
| `cpu.threads_per_core` | `hw_specs.cpu.threads_per_core` | optional |
| `gpu` | `hw_specs.gpu` normalized to a list (`none` becomes `[]`) | always (default `[]`) |
| `os.distribution` | `os_operating_system.distribution` | optional |
| `os.version` | `os_operating_system.distribution_version` | optional |
| `firewall` | `os_firewall` as bool | optional |
| `access_control.type` | `os_access_control` | optional |
| `os_partitioning` | `os_partitioning` | optional |
| `kernel` | `os_kernel_version` | optional |

### Example output

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

## Schema alignment with dynamic state

The `cpu`, `gpu`, `os`, `firewall`, `access_control`, `kernel`, and `network_interfaces[].name` fields use the same keys and value formats as `cluster_dynamic`'s `dynamic_state.yml`. This allows the `bluebanquise-cluster state` tool to compare static (expected) vs dynamic (live) values field by field and highlight drift.

Fields present only in static (`ansible_groups`, `bmc`, `os_partitioning`, `network_interfaces[].mac/network`) have no dynamic counterpart and are displayed as inventory-only data.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_state_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host state folders |
| `cluster_state_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Temporary directory for atomic writes by state daemons |
| `cluster_state_hosts_group` | `all` | Ansible group whose members are processed |
