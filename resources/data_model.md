# BlueBanquise CORE inventory data model reference 1.0.0

This data model is frozen, and should evolve only if major need.

Notes:

* When empty, variables values are assumed string. When needed, an example is provided.
* When defined choices exist, these choices are listed: `{choice1|choice2|choice3}`. When these choices are also open to other choices (depending of needs), `|...}` will be used.
* When variable is a list, this will be specified by `[]`.
* When a dictionary can repeat itself (with other data), `...` are added.

## Groups

Each host must be member of at least a unique *master_group* (default prefix is `mg_`) and
a unique *equipment_profile* group (default prefix is `equipment_`) **children of
this master_group**.

Note: if these requirements are achieved, system administrator is free to manage
groups the way desired.

In case of multi-icebergs configuration, each host must also be a member of an
iceberg group (default prefix is `iceberg`).

## Available variables for each host (hostvars level)

These variables are optional. Using them depend of Ansible roles used.

```yaml
  # Alias, included in hosts_file
  global_alias: []         # Global alias is present on all icebergs
  alias: []                # Alias is present inside host iceberg

  # BMC configuration
  bmc:
    name:                      # BMC name
    ip4:                       # BMC ip4
    mac:                       # BMC mac or/and dhcp_client_identifier or/and host_identifier or/and match
    dhcp_client_identifier:
    host_identifier:
    match:
    network:                   # BMC logical network

  # Host NIC configuration
  network_interfaces:          # Example
    - interface: eth1
      ip4: 10.10.3.1
      mac: 08:00:27:0d:44:90
      network: ice1-1
    - interface: eth0
      ip4: 10.11.3.1
      mac: 08:00:27:0d:44:91   # interface mac or/and dhcp_client_identifier or/and host_identifier or/and match
      network: ice1-2
      dhcp_client_identifier:
      host_identifier:
      match:
      gw4:
      mtu:
    - interface: eth2
      ip4: 10.10.0.1/16,10.10.0.2/16  # Multiple ip possible
      network: ice1-1
    - interface: bond0
      ip4: 10.10.0.1
      network: ice1-1
      type: bond
    - interface: eth3
      type: bond-slave
      master: bond0
    - interface: eth4
      type: bond-slave
      master: bond0
    - interface: eth2.100
      type: vlan
      vlanid: 100
      vlandev: eth2
      ip4: 10.100.0.1
      network: net-100
    - interface: enp0s8
      ip4: 10.10.0.1
      mac: 08:00:27:36:c0:ac
      network: ice1-1
      routes4:
        - 10.11.0.0/24 10.10.0.2
        - 10.12.0.0/24 10.10.0.2 300

  # Host LVM configuration
  lvm:
    vgs:
      - vg:
        pvs: []
      ...
    lvs:
      - lv:
        size:
        vg:
      ...
```

More parameters are available for each network interface, see nic_nmcli role
readme.

Note that in interfaces list, the first one in the list is hostname resolution
interface, and first one connected to an administration network (iceX-Y) is
default ssh interface from managements (Ansible is using ssh to push).

## To be defined at group_vars/equipment_profiles group level

### equipment_profiles

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
  distribution_version:              # Optional: define a minor distribution version to force (repositories/PXE)
  repositories_environment:          # Optional: add an environment in the repositories path (eg. production, staging) (repositories/PXE)

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

ep_equipment_authentication:
  user:
  password:
```

### Authentication

```yaml
authentication_root_password_sha512:
authentication_ssh_keys: []
```

## To be defined at group_vars/all group level

### General

```yaml
cluster_name:

time_zone:

icebergs_system: {true|false}

enable_services: {true|false}
start_services: {true|false}

hosts_file:
  range: {all|iceberg}
```

### Network

```yaml
domain_name:

networks:

  ice1-1:
    subnet:
    prefix:
    netmask:
    broadcast:
    dhcp_unknown_range: 10.10.254.1 10.10.254.254
    gateway:
    is_in_dhcp: {true|false}
    is_in_dns: {true|false}
    services_ip:
      pxe_ip:
      dns_ip:
      repository_ip:
      authentication_ip:
      slurm_ip:
      monitoring_ip:
      time_ip:
      log_ip:

  ...
```

### Security

```yaml
security:
  ssh:
    hostkey_checking: {true|false}
```

### Repositories

repositories: []

### External integration

```yaml
external_time:
  time_server:
    pool: []
    server: []
  time_client:
    pool: []
    server: []

external_dns:
  dns_server: []
  dns_client: []

external_hosts:
  hostname: ip
  ...
```

### Network File System

```yaml
nfs_settings:
  selinux:
    use_nfs_home_dirs: {true|false}

nfs:
  softwares:
    mount:
    export:
    server:
    clients_groups: []
    take_over_network:
    export_arguments:
    mount_arguments:
  ...
```

### Internal variables

```yaml
iceberg_naming:
equipment_naming:
management_networks_naming:
master_groups_naming:
managements_group_name:
```

## Advanced usage

### j2_ available variables

These are internal stack variables, for developers only.

```yaml
j2_master_groups_list: List of master groups.
j2_equipment_groups_list: List of equipment groups.

j2_icebergs_groups_list: List of icebergs groups.
j2_number_of_icebergs: Total number of icebergs.
j2_current_iceberg: Iceberg host is member of. (only one) (icebergX)
j2_current_iceberg_number: Iceberg number host is member of. (X)
j2_current_iceberg_network: Iceberg network host is member of (iceX)

j2_node_main_resolution_network: Main resolution network. The network on which host can be ping by direct name. (ex: ping c001).
j2_node_main_network: Main network. The network used by Ansible to deploy configuration (related to ssh).
j2_node_main_network_interface: Main network interface. Same as main network, but provides interface name instead of network.
j2_management_networks: List of management networks.
```

## Next version (2.0.0)

* Support for externaly defined bmc
* Support for `ep_host_authentication` variable. `ep_equipment_authentication` deprecated and removed.

```
ep_host_authentication:
  - protocol: SNMP
    user: snmpuser
    password: snmppass
  - protocol: SSH
    user: sshuser
    password: sshpass
  - protocol: IPMI
    user: ADMIN
    password: ADMIN
```
