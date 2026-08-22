# lustre_client

## Description

This role installs and configures the Lustre client. Lustre server configuration is not covered by this role.

Supported distributions: RHEL 9/10 (Lustre packages available via EPEL or DDN repositories).

Note: Ubuntu, Debian, and OpenSuse Leap are not officially supported as Lustre client packages are not widely available for those distributions.

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

### Multi-rail

When `lustre_multirail: true`, the role deploys sysctl settings for LNET interfaces to handle multi-rail networking correctly.

## Variables

| Variable         | Description                                      | Required |
|:-----------------|:-------------------------------------------------|:--------:|
| lustre_networks  | List of LNET networks with client group scoping  |   yes    |
| lustre_mounts    | List of Lustre mount points                      |   yes    |
| lustre_multirail | Enable multi-rail sysctl configuration           |    no    |

## Output

Packages installed:

* lustre-client
* kmod-lustre-client

Files generated:

* /etc/modprobe.d/lustre.conf
* /etc/sysctl.d/80-lustre-multi-rail.conf (when multirail enabled)

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.2.1: Fix issues with multiple-lnet setup. Lucas Santos <lucassouzasantos@gmail.com>
* 1.2.0: Added sysctl configuration to avoid issues with multi-rail. Lucas Santos <lucassouzasantos@gmail.com>
* 1.1.0: Added LNET configuration support for multi-rail. Lucas Santos <lucassouzasantos@gmail.com>
* 1.0.1: Just a minor fix to mount filesystem on the role execution. Lucas Santos <lucassouzasantos@gmail.com>
* 1.0.0: Role creation. Lucas Santos <lucassouzasantos@gmail.com>
