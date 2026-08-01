# cluster_state

## Description

This role writes both halves of the BlueBanquise cluster state system's `cluster_state` data
pair, under `/var/lib/bluebanquise/cluster/hosts/`:

- The **static** side: it collects host data from the Ansible inventory and writes it to
  per-host `static_cluster_state.yml` files.
- The **dynamic** side: it installs and configures the BlueBanquise cluster dynamic state
  daemon (`bluebanquise-cluster-dynamic`), which periodically scans all cluster hosts, collects
  live system data via SSH, and writes per-host `dynamic_cluster_state.yml` files to the same
  directory.

Both files use the same field names and value formats for comparable data, so the
`bluebanquise-cluster state` tool (installed by the `cluster_tools` role) can compare them
field by field and highlight drift between expected (static) and live (dynamic) state.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Output structure

For each host in the target group, the role creates:

```
/var/lib/bluebanquise/cluster/hosts/
  <hostname>/
    static_cluster_state.yml
    dynamic_cluster_state.yml     <- written by the daemon, not by the Ansible role itself
/var/lib/bluebanquise/cluster/
  .tmp/                          <- shared tmp directory for atomic writes by daemons
```

Each `static_cluster_state.yml` contains the fields described below. Only fields present in the
inventory are written — optional fields are omitted when undefined.

## Instructions

Run this role on the management node.

```yaml
- hosts: fn_management
  roles:
    - bluebanquise.infrastructure.cluster_state
```

It reads from `hostvars` (inventory data) and writes the static file locally — no SSH
connection to target hosts is required for that part. It also installs the daemon script,
generates its configuration from the inventory, installs the systemd unit, and reloads
systemd. The service is **not** started automatically — start it manually after installation,
or let `bb_start_services`/`cluster_state_start_services` start it on real hardware.

```bash
systemctl start bluebanquise-cluster-dynamic
systemctl enable bluebanquise-cluster-dynamic  # optional: start on boot
```

Follow logs via journald:

```bash
journalctl -u bluebanquise-cluster-dynamic -f
```

Enable debug logging at runtime by editing `/etc/bluebanquise/cluster_dynamic.conf` and setting
`log_level: DEBUG`, then restarting the service. Alternatively, pass `--log-level DEBUG` to the
script directly for one-shot debugging:

```bash
/usr/local/sbin/bluebanquise-cluster-dynamic /etc/bluebanquise/cluster_dynamic.conf --log-level DEBUG
```

Re-run the role whenever the inventory changes — this refreshes the static snapshot and
regenerates the daemon's host list in the configuration file (restart the service afterwards to
pick up the new host list).

### Processed fields (static)

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

### Example static output

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

## How the dynamic daemon works

1. On each scan cycle the daemon submits all hosts to a thread pool.
2. Per host: ping check → SSH check → data gathering via SSH commands.
3. Gathered data is written atomically to `dynamic_cluster_state.yml` using a tmp file and
   `os.replace()`, protected by a per-host `dynamic_cluster_state.lock` file.
4. After the cycle completes the daemon sleeps for `scan_interval` seconds before starting the
   next cycle.

SSH is invoked as `ssh <hostname>` with no explicit user or key flags — connection parameters
(user, identity file, jump hosts, etc.) are resolved from the `bluebanquise` user's
`~/.ssh/config`. The daemon runs as the `bluebanquise` user via systemd.

### Example dynamic output

```yaml
hostname: c001
last_updated: '2026-07-13T10:00:00+00:00'
ping: true
ssh: true
cpu:
  architecture: x86_64
  count: 72
  threads_per_core: 2
  cores_per_socket: 18
  sockets: 2
  model: Intel(R) Xeon(R) Gold 6154 CPU @ 3.00GHz
ram:
  total_bytes: 137438953472
  available_bytes: 131801407488
gpu:
  - '01:00.0 VGA compatible controller: NVIDIA Corporation GV100GL [Tesla V100]'
firewall: true
access_control:
  type: selinux
  state: Enforcing
os:
  distribution: rhel
  version: '9.2'
  pretty_name: Red Hat Enterprise Linux 9.2 (Plow)
kernel: 5.14.0-284.11.1.el9_2.x86_64
network_interfaces:
  - name: enp1s0
    ip4:
      - 10.10.3.1/16
    ip6: []
    speed_mbps: 1000
  - name: lo
    ip4:
      - 127.0.0.1/8
    ip6:
      - '::1/128'
    speed_mbps: null
```

If a host is unreachable by ping, only `hostname`, `last_updated`, and `ping: false` are
written. If ping succeeds but SSH fails, `ssh: false` is also written and no gathered data is
included.

### Adding new gatherers

Each gatherer is a standalone function with the signature:

```python
def gather_<name>(hostname, ssh_timeout):
    # run one or more SSH commands via run_ssh_command(hostname, command, ssh_timeout)
    # return any YAML-serialisable value, or None on failure
    ...
```

Register it by adding an entry to the `GATHERERS` dict in the script:

```python
GATHERERS = {
    ...
    '<name>': gather_<name>,
}
```

The key name becomes the field name in `dynamic_cluster_state.yml`. To have
`bluebanquise-cluster state` compare it against the static side, give it the same key name in
`static_cluster_state.yml.j2`.

## Schema alignment between static and dynamic

The `cpu`, `gpu`, `os`, `firewall`, `access_control`, `kernel`, and `network_interfaces[].name`
fields use the same keys and value formats on both sides. This allows the
`bluebanquise-cluster state` tool to compare `static_cluster_state.yml` and
`dynamic_cluster_state.yml` field by field and highlight drift.

Fields present only in static (`ansible_groups`, `bmc`, `os_partitioning`,
`network_interfaces[].mac/network`) have no dynamic counterpart and are displayed as
inventory-only data. Fields present only in dynamic (`last_updated`, `ping`, `ssh`, `cpu.count`,
`cpu.model`, `os.pretty_name`, `access_control.state`, `ram`,
`network_interfaces[].ip6/speed_mbps`) have no static counterpart and are displayed as
live-only data.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_state_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host state folders |
| `cluster_state_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Temporary directory for atomic writes by state daemons |
| `cluster_state_hosts_group` | `all` | Ansible group whose members are processed (static write loop and daemon host list) |
| `cluster_state_conf_path` | `/etc/bluebanquise/cluster_dynamic.conf` | Path to the daemon's generated configuration file |
| `cluster_state_daemon_script_path` | `/usr/local/sbin/bluebanquise-cluster-dynamic` | Installation path for the daemon script |
| `cluster_state_scan_interval` | `300` | Seconds between full scan cycles |
| `cluster_state_thread_pool_size` | `100` | Maximum concurrent host scans |
| `cluster_state_ping_timeout` | `5` | Seconds before ping times out |
| `cluster_state_ssh_timeout` | `10` | Seconds before SSH connect or command times out |
| `cluster_state_lock_timeout` | `30` | Seconds to wait for per-host write lock before skipping |
| `cluster_state_log_level` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
