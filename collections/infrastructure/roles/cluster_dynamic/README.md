# cluster_dynamic

## Description

This role installs and configures the BlueBanquise cluster dynamic state daemon. The daemon periodically scans all cluster hosts, collects live system data via SSH, and writes per-host `dynamic_state.yml` files under `/var/lib/bluebanquise/cluster/hosts/`.

It is the dynamic counterpart to the `cluster_state` role, which writes static inventory data to the same directory tree.

Supported distributions (management node): RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## How it works

1. On each scan cycle the daemon submits all hosts to a thread pool.
2. Per host: ping check → SSH check → data gathering via SSH commands.
3. Gathered data is written atomically to `dynamic_state.yml` using a tmp file and `os.replace()`, protected by a per-host `dynamic_state.lock` file.
4. After the cycle completes the daemon sleeps for `scan_interval` seconds before starting the next cycle.

SSH is invoked as `ssh <hostname>` with no explicit user or key flags — connection parameters (user, identity file, jump hosts, etc.) are resolved from the `bluebanquise` user's `~/.ssh/config`. The daemon runs as the `bluebanquise` user via systemd.

## Instructions

Run this role on the management node. It installs the daemon script, generates the configuration from the inventory, installs the systemd unit, and reloads systemd. The service is **not** started automatically — start it manually after installation.

```yaml
- hosts: fn_management
  roles:
    - bluebanquise.infrastructure.cluster_dynamic
```

Start the service:

```bash
systemctl start bluebanquise-cluster-dynamic
systemctl enable bluebanquise-cluster-dynamic  # optional: start on boot
```

Follow logs via journald:

```bash
journalctl -u bluebanquise-cluster-dynamic -f
```

Enable debug logging at runtime by editing `/etc/bluebanquise/cluster_dynamic.conf` and setting `log_level: DEBUG`, then restarting the service. Alternatively, pass `--log-level DEBUG` to the script directly for one-shot debugging:

```bash
/usr/local/sbin/bluebanquise-cluster-dynamic /etc/bluebanquise/cluster_dynamic.conf --log-level DEBUG
```

Re-run the role whenever the inventory changes to regenerate the host list in the configuration file, then restart the service.

## Output format

For each host, `dynamic_state.yml` contains:

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

If a host is unreachable by ping, only `hostname`, `last_updated`, and `ping: false` are written. If ping succeeds but SSH fails, `ssh: false` is also written and no gathered data is included.

## Adding new gatherers

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

The key name becomes the field name in `dynamic_state.yml`. No other changes are needed.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cluster_dynamic_conf_path` | `/etc/bluebanquise/cluster_dynamic.conf` | Path to the generated configuration file |
| `cluster_dynamic_script_path` | `/usr/local/sbin/bluebanquise-cluster-dynamic` | Installation path for the daemon script |
| `cluster_dynamic_scan_interval` | `300` | Seconds between full scan cycles |
| `cluster_dynamic_thread_pool_size` | `100` | Maximum concurrent host scans |
| `cluster_dynamic_ping_timeout` | `5` | Seconds before ping times out |
| `cluster_dynamic_ssh_timeout` | `10` | Seconds before SSH connect or command times out |
| `cluster_dynamic_lock_timeout` | `30` | Seconds to wait for per-host write lock before skipping |
| `cluster_dynamic_log_level` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `cluster_dynamic_hosts_group` | `all` | Ansible group whose members populate the host list |
| `cluster_dynamic_base_path` | `/var/lib/bluebanquise/cluster/hosts` | Root directory for per-host state folders |
| `cluster_dynamic_tmp_path` | `/var/lib/bluebanquise/cluster/.tmp` | Temporary directory for atomic writes |

## Schema alignment with static state

The `cluster_state` role writes `static_cluster_state.yml` to the same per-host directories using the same field names and value formats for comparable data: `cpu`, `gpu`, `os`, `firewall`, `access_control`, and `network_interfaces[].name`. The `bluebanquise-cluster state` tool merges both files and compares them field by field to highlight drift between expected (static) and live (dynamic) state.
