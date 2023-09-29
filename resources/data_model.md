# BlueBanquise CORE inventory data model reference 2.0.0

## Introduction

This data model explains how core inventory data are expected by most of BlueBanquise roles.
To ease roles usage, this data model is splitted into sections. Each role uses none, a part, or all sections of this data model. Refer to roles' README.md files to know which sections should be considered.

All roles also have dedicated variables, detailed in each roles' README.md file.

## Notes before reading

This data model is frozen, and should evolve only if major need or when BlueBanquise evolves to a new major version.

Notes:

* When empty, variables values are assumed string. When needed, an example is provided.
* When defined choices exist, these choices are listed: `{choice1|choice2|choice3}`. When these choices are also open to other choices (depending of needs), `|...}` will be used.
* When variable is a list, this will be specified by `[]`.
* When a dictionary can repeat itself (with other data), `...` are added.

Last but not least, note that `j2_` variables that contains the stack core logic are provided either by the vars plugin core.py in common collection, either by adding the provided `bb_core.yml` file into your `group_vars/all/` inventory folder.

## Section 1: Networks

Networks are defined as followed:

```yaml
networks:
  net-admin:
    prefix: 16
    subnet: 10.10.0.0
    services:
      dns:
        - ip4: 10.10.0.2
          hostname: mg1-dns
        ...
      pxe:
        - ip4: 10.10.0.1
          hostname: mg1-pxe
      ntp:
        - ip4: 10.10.0.4
          hostname: mg1-ntp
      ...
  interconnect:
    prefix: 16
    subnet: 10.20.0.0
  ...
```

When the network name starts by `net-` then it is considered a **management network**, and has special consideration. Other networks are considered simple networks.

When a network is a management network, services linked to this network are added under `services` key. Each service kind is a list, and so can accept multiple entries (multiple DNS servers for example).

Note that when a cluster is small and has a single management server, then a *magic* key `services_ip` can be set instead of `services`, and will make all services to converge to this unique ip.

Example:

```yaml
networks:
  net-admin:
    prefix: 16
    subnet: 10.10.0.0
    services_ip: 10.10.0.1
```

Note that some roles supports more keys in networks definition. Data given here are core minimal.

## Section 2: Hosts (nodes) definition

Hosts network connections must be defined the following way:

```yaml
all:
  hosts:
    node001:
      network_interfaces:
        - interface: eth1
          ip4: 10.10.3.1
          mac: 08:00:27:0d:44:90
          network: net-admin
        - interface: eth0
          skip: true
        - interface: ib0
          ip4: 10.20.3.1
          network: interconnect
          type: infiniband
```

More parameters are available for each network interface, see `nic` role README.md file for more details. Example given here is the bare minimum for roles to identify host.

**Important:** note that in interfaces list, the first one in the list is hostname resolution
interface, and first one connected to an administration network (net-XXXXX) is
default ssh interface from managements (Ansible is using ssh to push).
As a result, resolution ip and ssh ip can be the same, or different.

If you need to define a server BMC, use the following format:

```yaml
all:
  hosts:
    node001:
      bmc:
        name: node001-bmc
        ip4: 10.10.103.1
        mac: 08:00:27:0d:44:91
        network: net-admin
      network_interfaces:
        - interface: eth1
          ip4: 10.10.3.1
          mac: 08:00:27:0d:44:90
          network: net-admin
        - interface: eth0
          skip: true
        - interface: ib0
          ip4: 10.20.3.1
          network: interconnect
          type: infiniband
```

Some roles like dhcp_server, hosts_file, conman, powerman, etc., can identify hosts BMC using these data.


## Section 3: Groups

System admininstrator is free to create Ansible groups as needed. However, some specific groups are to be taken into account.

### 3.1: managements group

Admininstration/management servers must be member of the Ansible group `mg_managements`, to be identified as management servers.

### 3.2: equipments groups

Except for very simple clusters with fully hotorogenous equipment, hosts must be members of an equipment Ansible group.

An equipment group is always prefixed by `equipment_`. Each equipment group possess variables that define the specific hardware/OS related parameters of its members.
For example, in a cluster with 2 kind of servers (lets say supermicro A and gigabyte B), there will probably be 2 equipment groups: `equipment_supermicro_A` and `equipment_gigabyte_B`.

Many roles use equipment groups, the main one being pxe_stack role.

Example of variables stored in equipment groups:

```yaml
ep_ipxe_driver: {default|snp|snponly}
ep_ipxe_platform: {pcbios|efi}
ep_ipxe_embed: {standard|dhcpretry}

ep_preserve_efi_first_boot_device: {true|false}

ep_console:
ep_kernel_parameters:
ep_sysctl:

ep_access_control: {enforcing|permissive|disabled|...}
ep_firewall: {true|false}

ep_partitioning:
ep_autoinstall_pre_script:
ep_autoinstall_post_script:

ep_operating_system:
  distribution:
  distribution_major_version:
  distribution_version:      # Optional: define a minor distribution version to force (repositories/PXE)
  repositories_environment:  # Optional: add an environment in the repositories path (eg. production, staging) (repositories/PXE)

ep_equipment_type: {server|...}

ep_configuration:
  keyboard_layout:
  system_language:

ep_hardware:
  cpu:
    architecture:
    cores:
    cores_per_socket:
    sockets:
    threads_per_core:
  gpu:

ep_host_authentication:  # Authentication to BMC
  - protocol: IPMI
    user: ADMIN
    password: ADMIN
```

### 3.3: icebergs groups

These groups are for advanced clusters, using multiple icebergs mechanism. If not using icebergs, please ignore this part.

In case of multi-icebergs configuration, each host must also be a member of an
iceberg group (default prefix is `iceberg`).

Also, management networks must be prefixed by `netX-` with `X` being the iceberg number.

## Section 4: Global variables

There are few global variables that can be shared by roles. Note that if not set, roles will use their own dedicated variables.

* `bb_domain_name`: set a global domain name for the whole cluster.
