# lustre_client

## Description

This role installs and configures the Lustre client. Lustre server configuration is not covered by this role.

Supported distributions: RHEL 9/10. The `lustre-client` and `kmod-lustre-client` packages come from Whamcloud (https://downloads.whamcloud.com/public/lustre/) or DDN repositories, matching the running kernel. The role fails on other distributions.

## Instructions

### Configure your lustre_client inventory

The configuration describes your Lustre networks and mount points.

Recommended path: `inventories/group_vars/all/addons/lustre_client.yml`

```yaml
lustre_multirail: true
lustre_networks:
  - name: o2ib0
    network: interconnect-1
    clients_groups:
      - mg_computes
      - mg_logins

lustre_mounts:
  - name: scratch
    path: /scratch
    mount_path: /mnt/scratch
    lnet: o2ib0
    mgs_servers:
      - 10.30.6.103
      - 10.30.6.104
      - 10.30.6.105
    clients_groups:
      - mg_computes
    mount_opts: "_netdev,flock,rw"
```

Each host gets the LNET networks whose `clients_groups` contain it, using its interfaces connected to the
inventory `network` (for example `options lnet networks=o2ib0(ib0)`). Networks where the host has no interface
are skipped. Hosts mount the filesystems whose `clients_groups` contain them, from
`<mgs1>@<lnet>:<mgs2>@<lnet>:/<path>`, where `path` (file system name) defaults to `name`.

LNET settings are read when the `lnet` kernel module is loaded: after a change, unmount Lustre filesystems
and unload the Lustre modules (`lustre_rmmod`), or reboot.

### Multi-rail

When `lustre_multirail: true`, the role deploys sysctl settings for LNET interfaces to handle multi-rail networking correctly.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `lustre_networks` | `[]` | LNET networks: `name` (LNET name), `network` (inventory network), `clients_groups`. |
| `lustre_mounts` | `[]` | Lustre filesystems: `name`, `path` (file system name, default `name`), `mount_path`, `lnet`, `mgs_servers`, `clients_groups`, `mount_opts`. |
| `lustre_multirail` | `false` | Deploy sysctl settings needed by LNET multi-rail. |
