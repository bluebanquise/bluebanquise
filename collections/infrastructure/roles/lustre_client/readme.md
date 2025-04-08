# Lustre client 

Role compatibility:

|      OS      | Version | Supported |
|:-------------|:--------|:---------:|
| Ubuntu       |   20.04 |    no     |
| Ubuntu       |   22.04 |    no     |
| RHEL         |       7 |    yes    |
| RHEL         |       8 |    yes    |
| RHEL         |       9 |    yes    |
| OpenSuseLeap |      15 |    no     |
| Debian       |      11 |    no     |


## Description

This role provides lustre client instalation and configuration. Lustre server configuration is not covered by it !


## Instructions

### Configure you lustre_client inventory file 

The configuration is a simple description of your lustre networks and your lustre mount points, as you can see below: 

recommended path: /$HOME/bluebanquise/inventories/group_vars/all/addons/lustre_client.yml

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

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.2.0: Added sysctl configuration to avoid issues with multi-rail. Lucas Santos <lucassouzasantos@gmail.com>
* 1.1.0: Added LNET configuration support for multi-rail. Lucas Santos <lucassouzasantos@gmail.com>
* 1.0.1: Just a minor fix to mount filesystem o the role execution. Lucas Santos <lucassouzasantos@gmail.com>
* 1.0.0: Role creation. Lucas Santos <lucassouzasantos@gmail.com>
