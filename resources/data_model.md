# BlueBanquise CORE inventory data model reference 3.0.0

## Introduction

This data model explains how core inventory data are expected by most of BlueBanquise roles.
To ease roles usage, this data model is split into sections. Each role uses none, a part, or all sections of this data model. Refer to roles' README.md files to know which sections should be considered.

All roles also have dedicated variables, detailed in each role's README.md file, and summarized in [Section 5](#section-5-roles-dedicated-variables).

## Notes before reading

This data model is frozen, and should evolve only if major need or when BlueBanquise evolves to a new major version.

Notes:

* When empty, variables values are assumed string. When needed, an example is provided.
* When defined choices exist, these choices are listed: `{choice1|choice2|choice3}`. When these choices are also open to other choices (depending of needs), `|...}` will be used.
* When variable is a list, this will be specified by `[]`.
* When a dictionary can repeat itself (with other data), `...` are added.

## Reserved variables

The following variables are reserved by the stack:

* `os_profile`
* `hw_profile`
* `ep_profile`
* `bb_nodes_profiles`
* `bb_equipments`
* `bb_nodes`

Also, nodes hardware and os groups names **cannot contain** the string `_with_`.

## Section 1: Networks

Networks are defined as followed:

```yaml
networks:
  net-admin:
    prefix: 16
    subnet: 10.10.0.0
    services:
      dns4:
        - ip4: 10.10.0.2
          hostname: mg1-dns
        ...
      pxe4:
        - ip4: 10.10.0.1
          hostname: mg1-pxe
      ntp4:
        - ip4: 10.10.0.4
          hostname: mg1-ntp
      ...
  interconnect:
    prefix: 16
    subnet: 10.20.0.0
  ...
```

Note: `4` or `6` at end of some keys are related to ipv4 or ipv6.

When the network name starts by `net-` then it is considered a **management network**, and has special consideration. Other networks are considered simple networks.

When a network is a management network, services linked to this network are added under `services` key. Each service kind is a list, and so can accept multiple entries (multiple DNS servers for example).

Service keys end with `4` for IPv4 endpoints (`dns4`, `pxe4`, `ntp4`, `log4`, `repositories4`, etc.), to leave room for IPv6 endpoints later (`dns6`, etc.). Keys without suffix (`dns`, `pxe`, ...) are deprecated, but still accepted by roles.

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

System administrator is free to create Ansible groups as needed. However, some specific groups are to be taken into account as they are mandatory.
Each **Ansible host** must be member of 3 specific groups:

* A function group
* An hardware group
* An operating system group

**Non Ansible hosts** (hosts that should simply be registered in services like DHCP/DNS, but not where an operating system has to be deployed, like a switch) can only be part of a function group if an hardware profile is not relevant.

The idea is to define an host with a function, an hardware profile, and an OS profile.

### 3.1: Function groups

Each host have to be in a function group. This group determine the function/purpose of the host.
Function groups are prefixed with `fn_`.

Function groups can be custom named as needed.
However, the `fn_management` function group is important and has to be named this way. It should contain all management hosts. Ansible will use this group to identify managements hosts and behave accordingly.

Example of function groups:

* fn_management
* fn_compute
* fn_login
* fn_storage
* fn_nfs
* fn_eth_switch
* fn_rack_manager
* ...

### 3.2: Hardware groups

Each host have to be in an hardware group. This group determine the hardware related parameters of the target host.

These groups are always prefixed by `hw_`. Hardware groups can be custom named as needed.

Example of hardware groups:

* hw_supermicro_X91HA_E5300_32G
* hw_asus_XZP4
* hw_nvidia_DGX_A100
* ...

Many roles use hardware groups, the main one being pxe_stack role.

Example of variables stored in hardware groups:

```yaml
hw_ipxe_driver: {default|snp|snponly}
hw_ipxe_platform: {pcbios|efi}
hw_ipxe_embed: {standard|dhcpretry}

hw_console:
hw_kernel_parameters:
hw_sysctl:

hw_equipment_type: {server|...}

hw_architecture: {x86_64|arm64}

hw_specs:
  cpu:
    architecture:
    cores:
    cores_per_socket:
    sockets:
    threads_per_core:
  gpu:

hw_board_authentication:  # Authentication to BMC
  - protocol: IPMI        # {IPMI|REDFISH}
    user: ADMIN
    password: ADMIN
    console_port: 22      # Optional, REDFISH only: SSH port of the BMC serial console (conman role)
    system_id:            # Optional, REDFISH only: Id of the system to manage if the BMC exposes several (bluebanquise_power role)
```

### 3.3: Operating system groups

Each host have to be in an operating system group. This group determine the OS related parameters of the target host.

These groups are always prefixed by `os_`. Operating system groups can be custom named as needed.

Example of operating system groups:

* os_ubuntu_24.04_gpu
* os_almalinux_9
* ...

Many roles use os groups, the main one being pxe_stack role.

Example of variables stored in os groups:

```yaml
os_preserve_efi_first_boot_device: {true|false}

os_access_control: {enforcing|permissive|disabled|...}
os_firewall: {true|false}

os_target_disk:
os_partitioning:

os_operating_system:
  distribution:
  distribution_major_version:
  distribution_version:      # Optional: define a minor distribution version to force (repositories/PXE)
  repositories_environment:  # Optional: add an environment in the repositories path (eg. production, staging) (repositories/PXE)

os_keyboard_layout:
os_system_language:
```

### 3.4: icebergs groups

These groups are for advanced clusters, using multiple icebergs mechanism. If not using icebergs, please ignore this part.

In case of multi-icebergs configuration, each host must also be a member of an
iceberg group (default prefix is `iceberg`).

Also, management networks must be prefixed by `netX-` with `X` being the iceberg number.

## Section 4: Global variables

These `bb_` prefixed variables are shared by multiple roles. When set, they apply to all roles at once.
A role's dedicated variable, when set, always takes precedence over the related global variable, which takes precedence over the role's default value.

| Variable | Used by | Description |
|----------|---------|-------------|
| `bb_domain_name` | dhcp_server, dns_client, dns_server, hosts_file, local_configuration | Domain name of the whole cluster. |
| `bb_time_zone` | pxe_stack, time | Time zone of the whole cluster. |
| `bb_repositories` | repositories | List of repositories to set on hosts. |
| `bb_enable_services` | all roles managing a service | Enable services at boot (`true` if unset). |
| `bb_start_services` | all roles managing a service | Start and restart services (`true` if unset). |
| `bb_services_firewall_zone` | all roles opening ports in the firewall | Firewalld zone services are added to (`public` if unset). |
| `bb_restrict_to_group` | bluebanquise_power, conman, dhcp_server, dns_server, hosts_file, pxe_stack, ssh_client | Restrict the hosts these roles take into account to an Ansible group (`all` if unset). |
| `bb_enable_flat_optimizations` | hosts_file | Use the optimized (flat) generation logic on very large clusters (`false` if unset). |
| `bb_iceberg_level` | time | Iceberg level of the host, when using the icebergs mechanism. |

## Section 5: Roles dedicated variables

This section lists, for each role of the `bluebanquise.infrastructure` collection, all its dedicated variables, so all possible settings of the collection are gathered in a single place.
Refer to each role's README.md file for details and examples.

Notes:

* `<role>_enable_services` and `<role>_start_services`, when listed, fall back to `bb_enable_services` and `bb_start_services`, then to `true`.
* Roles opening ports or services in firewalld do it only when `os_firewall` is `true` (default), in a `firewall` tagged block. If it fails (firewalld not installed or not running, Python bindings missing), the role stops with an explanatory message: install firewalld (for example using the **firewall** role), or set `os_firewall: false`.
* Roles `cluster_*`, `beegfs` and `nic_netplan` are not listed here yet.

### auditd

| Variable | Default | Description |
|----------|---------|-------------|
| `auditd_forward_audit_logs` | `false` | Forward audit logs to the local syslog daemon. |
| `auditd_config_root_log` | `false` | Log all commands executed by root (euid 0). |
| `auditd_enable_services` | `bb_enable_services`, else `true` | Enable auditd at boot. |
| `auditd_start_services` | `bb_start_services`, else `true` | Start auditd, and restart it on configuration change. |

### bluebanquise_power

| Variable | Default | Description |
|----------|---------|-------------|
| `bluebanquise_power_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only consider hosts of this Ansible group when generating the configuration. |

### cloudinit

| Variable | Default | Description |
|----------|---------|-------------|
| `cloudinit_configuration` | `{groups: [], users: []}` | cloud-init configuration to write. |
| `cloudinit_boot_script` | not set | Base64-encoded script to run at boot. When set, replaces `cloudinit_configuration`. |
| `cloudinit_enable_services` | `bb_enable_services`, else `true` | Enable cloud-init services at boot. |

### clustershell

| Variable | Default | Description |
|----------|---------|-------------|
| `clustershell_install_from_package` | `false` | Install ClusterShell using the system package manager. |
| `clustershell_prefix_path` | `""` | Prefix of the ClusterShell configuration path (`<prefix>/etc/clustershell`), for a custom virtual environment. |

### conman

| Variable | Default | Description |
|----------|---------|-------------|
| `conman_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only register hosts of this Ansible group. |
| `conman_redfish_console_port` | `22` | SSH port of Redfish BMCs consoles, when not set per hardware group (`console_port` key of `hw_board_authentication`). |
| `conman_user_uid` | `287` | UID of the conman user. |
| `conman_user_gid` | `287` | GID of the conman group. |
| `conman_user_home` | `/var/lib/conman` | Home of the conman user, storing its SSH configuration. |
| `conman_enable_services` | `bb_enable_services`, else `true` | Enable conman at boot. |
| `conman_start_services` | `bb_start_services`, else `true` | Start conman, and restart it on configuration change. |

### custom_packages

| Variable | Default | Description |
|----------|---------|-------------|
| `custom_packages_by_group` | `{}` | Dictionary of Ansible group names, each with the list of packages to install on hosts of this group. |

### dhcp_server

| Variable | Default | Description |
|----------|---------|-------------|
| `dhcp_server_lease_file` | `kea-leases4.csv` | Lease database file name, in `/var/lib/kea/`. |
| `dhcp_server_default_lease_time` | `600` | Default lease time, in seconds. |
| `dhcp_server_max_lease_time` | `7200` | Maximum lease time, in seconds. |
| `dhcp_server_ipxe_driver` | `snponly` | iPXE rom driver: `snponly`, `snp`, or default drivers. |
| `dhcp_server_ipxe_embed` | `dhcpretry` | iPXE rom embedded script: `dhcpretry`, `noshell`, `allretry`, or standard. |
| `dhcp_server_domain_name` | `bb_domain_name`, else `cluster.local` | Domain search list sent to clients. |
| `dhcp_server_listen_interfaces` | `["*"]` | Interfaces the DHCP server listens on. |
| `dhcp_server_match_client_id` | `false` | Track leases using client identifiers (option 61) instead of MAC addresses only. |
| `dhcp_server_log_severity` | `INFO` | Kea log severity: `FATAL`, `ERROR`, `WARN`, `INFO` or `DEBUG`. |
| `dhcp_server_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only register hosts of this Ansible group. |
| `dhcp_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewalld zone to open the DHCP service in. |
| `dhcp_server_firewall_services_to_add` | `["dhcp"]` | Firewalld services to open. |
| `dhcp_server_enable_services` | `bb_enable_services`, else `true` | Enable the DHCP server at boot. |
| `dhcp_server_start_services` | `bb_start_services`, else `true` | Start the DHCP server, and restart it on configuration change. |

Networks keys: `dhcp_server` (`false` to exclude the network), `dhcp_unknown_range`, `dhcp_match_client_id`, `shared_network`.

### dns_client

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_client_domain_name` | `bb_domain_name`, else `cluster.local` | Search domain. |
| `dns_client_servers` | `[]` | DNS servers to use, instead of the DNS services of the host network. |
| `dns_client_external_servers` | `[]` | DNS servers added after the cluster ones. |
| `dns_client_start_services` | `bb_start_services`, else `true` | Restart systemd-resolved / reload NetworkManager on configuration change. |

### dns_server

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_server_domain_name` | `bb_domain_name`, else `cluster.local` | Domain name of the forward zone. |
| `dns_server_recursion` | `false` | Enable recursion. Required by forwarders and overrides. |
| `dns_server_forwarders` | `[]` | Upstream DNS servers to forward queries to. |
| `dns_server_forward_only` | `false` | Never resolve recursively, only forward. |
| `dns_server_forward_only_domains` | not set | List of `{domain, forwarder_ip}`: domains forwarded to a dedicated server. |
| `dns_server_dnssec_validation` | `auto` | BIND `dnssec-validation` value: `auto`, `yes` or `no`. |
| `dns_server_listen_on_ip4` | `[]` | Additional IPs to listen on. |
| `dns_server_allow_query` | `[]` | Additional subnets (`subnet/prefix`) allowed to query. |
| `dns_server_enable_extended_names` | `true` | Write `<host>-<network>` records for each interface. |
| `dns_server_wildcard_records` | `[]` | List of `{hostname, ip4}` records added to the forward zone. |
| `dns_server_overrides` | not set | Dictionary of `name: ip` responses to override. Requires recursion. |
| `dns_server_raw_content` | not set | Raw content appended to `named.conf`. |
| `dns_server_raw_options_content` | not set | Raw content appended to the `options` block. |
| `dns_server_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only register hosts of this Ansible group. |
| `dns_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewalld zone to open the DNS service in. |
| `dns_server_firewall_services_to_add` | `["dns"]` | Firewalld services to open. |
| `dns_server_enable_services` | `bb_enable_services`, else `true` | Enable the DNS server at boot. |
| `dns_server_start_services` | `bb_start_services`, else `true` | Start the DNS server, and restart it on configuration change. |

Networks keys: `dns_server` (`false` to neither listen on nor allow queries from the network).

### drbd

| Variable | Default | Description |
|----------|---------|-------------|
| `drbd_resources` | `[]` | List of DRBD resources: `name`, `nodes`, `disk`, `device` (required), `port` (default `7789`), `metadisk` (default `internal`), `partitioning`, `logical_volumes`, `filesystem`, `mount` (optional). |

### firewall

| Variable | Default | Description |
|----------|---------|-------------|
| `os_firewall` | `true` | Enable firewalld and configure it (global variable, usually set in OS groups). |
| `firewall_zones` | not set | Zones settings: services, ports, rich rules, ICMP blocks, masquerade. |
| `firewall_policies` | `[]` | Firewalld policies, for traffic forwarded between zones. |
| `firewall_firewalld_allow_zone_drifting` | `false` | Value of firewalld `AllowZoneDrifting` setting. |
| `firewall_start_services` | `bb_start_services`, else `true` | Reload firewalld on configuration change. |

Networks keys: `firewall_zone` (optional, zone the network subnet is bound to).

### gpu

| Variable | Default | Description |
|----------|---------|-------------|
| `gpu_vendor` | not set | GPU vendor: `nvidia` or `amd`. Nothing is done if not set. |
| `gpu_nvidia_kernel_modules` | `open` | NVIDIA kernel modules: `open`, or `proprietary` (RHEL 8/9 only). |
| `gpu_nvidia_install_cuda` | `false` | Also install the CUDA toolkit (NVIDIA). |
| `gpu_amd_install_rocm` | `true` | Also install ROCm (AMD). |
| `gpu_reboot` | `false` | Reboot hosts after driver installation or update. |
| `gpu_reboot_timeout` | `600` | Reboot timeout, in seconds. |
| `gpu_enable_services` | `bb_enable_services`, else `true` | Enable `nvidia-persistenced` (NVIDIA). |
| `gpu_start_services` | `bb_start_services`, else `true` | Start `nvidia-persistenced` once the driver is loaded (NVIDIA). |

### grafana

| Variable | Default | Description |
|----------|---------|-------------|
| `grafana_address` | `0.0.0.0` | Listening address. |
| `grafana_port` | `3000` | Listening port. |
| `grafana_domain` | host FQDN | Domain name used to reach Grafana. |
| `grafana_admin_user` | `admin` | Admin user name. |
| `grafana_admin_password` | `admin` | Admin password, enforced at each run. |
| `grafana_configuration` | `{}` | Additional grafana.ini sections and options. |
| `grafana_ldap_configuration` | `""` | Content of `/etc/grafana/ldap.toml`. Enables LDAP authentication when set. |
| `grafana_plugins` | `[]` | Plugins to install. |
| `grafana_datasources` | `[]` | Datasources, in Grafana provisioning format. |
| `grafana_dashboards` | `[]` | Dashboards to download from grafana.com (`dashboard_id`, `revision_id`, `datasource`). |
| `grafana_dashboards_dir` | `""` | Folder of the Ansible host containing dashboards JSON files to install. |
| `grafana_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open the Grafana port in. |
| `grafana_enable_services` | `bb_enable_services`, else `true` | Enable Grafana service. |
| `grafana_start_services` | `bb_start_services`, else `true` | Start Grafana service, and enforce admin password. |

### haproxy

| Variable | Default | Description |
|----------|---------|-------------|
| `haproxy_global_parameters` | not set (role defaults) | Global section content, multi lines string. |
| `haproxy_defaults_parameters` | not set (role defaults) | Defaults section content, multi lines string. |
| `haproxy_resources` | `[]` | Frontends and backends, see Resources. |
| `haproxy_resources_raw` | `""` | Raw configuration, added as is. |
| `haproxy_enable_ip_nonlocal_bind` | `true` | Set `net.ipv4.ip_nonlocal_bind=1`, to listen on virtual IPs. |
| `haproxy_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open frontends ports in. |
| `haproxy_enable_services` | `bb_enable_services`, else `true` | Enable HAProxy service. |
| `haproxy_start_services` | `bb_start_services`, else `true` | Start HAProxy service, and reload it on configuration changes. |

### hosts_file

| Variable | Default | Description |
|----------|---------|-------------|
| `hosts_file_domain_name` | `bb_domain_name`, else `cluster.local` | Domain name of hosts. |
| `hosts_file_fqdn_first` | `true` | Write FQDN before short name (canonical name). |
| `hosts_file_enable_extended_names` | `true` | Also write all interfaces (`<hostname>-<network>`) and interfaces aliases. |
| `hosts_file_external_hosts` | `{}` | Hosts not in the inventory. |
| `hosts_file_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only write hosts of this group. |

### http_proxy

| Variable | Default | Description |
|----------|---------|-------------|
| `http_proxy_port` | `3128` | Listening port. |
| `http_proxy_allowed_networks` | `[]` | Networks allowed to use the proxy, in addition to inventory networks. |
| `http_proxy_default_allowed_ports` | `true` | Allow Squid default destination ports. |
| `http_proxy_allowed_ports` | `[]` | Additional allowed destination ports. |
| `http_proxy_ssl_ports` | `[443]` | Destination ports allowed for tunnels (`CONNECT`). |
| `http_proxy_cache_enable` | `false` | Enable disk cache. |
| `http_proxy_cache_storage_format` | `ufs` | Cache storage format. |
| `http_proxy_cache_storage_path` | `/var/spool/squid` | Cache folder. |
| `http_proxy_cache_storage_size` | `100` | Cache size, in MB. |
| `http_proxy_cache_storage_l1` | `16` | Number of first level cache sub folders. |
| `http_proxy_cache_storage_l2` | `256` | Number of second level cache sub folders. |
| `http_proxy_refresh_patterns` | `[]` | Custom refresh patterns. |
| `http_proxy_coredump_dir` | `/var/spool/squid` | Coredump folder. |
| `http_proxy_raw_content` | `""` | Raw Squid configuration, added at the end of the file. |
| `http_proxy_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open the proxy port in. |
| `http_proxy_enable_services` | `bb_enable_services`, else `true` | Enable Squid service. |
| `http_proxy_start_services` | `bb_start_services`, else `true` | Start Squid service, and restart it on configuration changes. |

Network key (in `networks`):

| Key | Default | Description |
|-----|---------|-------------|
| `http_proxy_server` | `true` | Allow this network to use the proxy. |

### http_server

| Variable | Default | Description |
|----------|---------|-------------|
| `http_server_listen` | not set | `auto`, or list of `ip:port`, `ip` or `port` to listen on. Not set: distribution default (port 80, all addresses). |
| `http_server_modules` | `[]` | Apache modules to enable (Debian, Ubuntu and Suse only). |
| `http_server_configurations_files` | `[]` | Raw configuration files (`name`, `configuration`). |
| `http_server_firewall_services_to_add` | `[http]` | Firewall services to open. |
| `http_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open services and ports in. |
| `http_server_enable_services` | `bb_enable_services`, else `true` | Enable Apache service. |
| `http_server_start_services` | `bb_start_services`, else `true` | Start Apache service, and restart it on configuration changes. |

### keepalived

| Variable | Default | Description |
|----------|---------|-------------|
| `keepalived_vrrp_instances` | `[]` | VRRP instances, see above. |
| `keepalived_conf_file` | `/etc/keepalived/keepalived.conf` | Configuration file path. |
| `keepalived_firewall_services_to_add` | `[vrrp]` | Firewall services to open. |
| `keepalived_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open services in. |
| `keepalived_enable_services` | `bb_enable_services`, else `true` | Enable keepalived service. |
| `keepalived_start_services` | `bb_start_services`, else `true` | Start keepalived service, and reload it on configuration changes. |

### lmod

| Variable | Default | Description |
|----------|---------|-------------|
| `lmod_path` | `[]` | Extra module search paths, appended to `MODULEPATH` of all users (`/etc/profile.d/modules_extra_path.sh`, removed when empty). |

### interconnect

| Variable | Default | Description |
|----------|---------|-------------|
| `interconnect_stack` | not set | Interconnect stack to deploy: `ofed`. Nothing is done if not set. |
| `interconnect_ofed_client` | `false` | Install InfiniBand client packages and set memlock limits. |
| `interconnect_ofed_memlock_soft` | `unlimited` | Soft memlock limit of all users. |
| `interconnect_ofed_memlock_hard` | `unlimited` | Hard memlock limit of all users. |
| `interconnect_ofed_subnet_manager` | `false` | Install and start OpenSM subnet manager. |
| `interconnect_ofed_subnet_manager_priority` | `0` | OpenSM priority, from 0 to 15. |
| `interconnect_ofed_subnet_manager_guids` | `[]` | Port GUIDs to run OpenSM on. Empty: distribution default. |
| `interconnect_enable_services` | `bb_enable_services`, else `true` | Enable OpenSM service. |
| `interconnect_start_services` | `bb_start_services`, else `true` | Start OpenSM service, and restart it on settings changes. |

### local_configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `local_configuration_hostname_fqdn` | `true` | Set FQDN hostname, else short hostname. |
| `local_configuration_hostname_domain_name` | `bb_domain_name`, else `cluster.local` | Domain name of the FQDN hostname. |
| `local_configuration_security` | not set | Security configuration: `access_control`, `admin_password_sha512`, `sudoers`, `sudoers_logging`. |
| `local_configuration_system` | not set | System configuration: `kernel_parameters`, `hw_kernel_parameters`, `sysctl`, `kernel_version`, `kernel_version_allow_reboot`, `modprobe`, `pam_limits`, `cron_jobs`, `packages`, `services`, `folders`, `files`, `templates`, `lineinfile`. |
| `local_configuration_storage` | not set | Storage configuration: `parted`, `lvm`, `filesystem`, `mount`. |
| `local_configuration_access_control_os_access_control` | `enforcing` | Access control state when neither `local_configuration_security.access_control` nor `os_access_control` is set. |
| `local_configuration_root_password_enable_root` | `false` | Set the admin password on root instead of the sudo user. |
| `local_configuration_root_password_sudo_user` | `bluebanquise` | User receiving the admin password when root is not enabled. |
| `local_configuration_sudoers_logging` | `false` | Default for `local_configuration_security.sudoers_logging`. |
| `local_configuration_kernel_config_sysctl_reload` | `true` | Reload sysctl after changes. |
| `local_configuration_kernel_version_meta_packages` | distribution default | Kernel meta-packages held with the kernel version lock (Debian, Ubuntu). |
| `local_configuration_lvm_packages_to_install` | `[lvm2]` | LVM packages. |

Global variables used when the matching key of the role dictionaries is not set: `os_access_control`,
`os_admin_password_sha512`, `os_kernel_parameters`, `hw_kernel_parameters`, `hw_console`, `os_sysctl`,
`os_kernel_version`, `os_kernel_version_allow_reboot`.

### logrotate

| Variable | Default | Description |
|----------|---------|-------------|
| `logrotate_global_daily` | `true` | Rotate daily. |
| `logrotate_global_weekly` | `false` | Rotate weekly. |
| `logrotate_global_monthly` | `false` | Rotate monthly. |
| `logrotate_global_rotate` | `7` | Number of rotations to keep. |
| `logrotate_global_compress` | `true` | Compress rotated logs. |
| `logrotate_global_delaycompress` | `false` | Delay compression by one rotation. |
| `logrotate_global_missingok` | `true` | Do not error if log file is missing. |
| `logrotate_global_notifempty` | `true` | Do not rotate empty log files. |
| `logrotate_global_create` | `""` | Mode, owner and group of new log files. Empty: same as rotated file. |
| `logrotate_global_su` | `""` (`root adm` on Ubuntu) | User and group used to rotate. |
| `logrotate_global_dateext` | `true` | Use date as extension for rotated logs. |
| `logrotate_global_dateformat` | `-%Y%m%d` | Date format for rotated log names. |
| `logrotate_global_extension` | `.log` | Extension kept at the end of rotated log names. |
| `logrotate_enable_xz` | `true` | Use xz compression instead of gzip. |
| `logrotate_custom_rules` | `[]` | Custom rules (`name`, `path`, `options`), written to `/etc/logrotate.d/<name>`. |

### loki

| Variable | Default | Description |
|----------|---------|-------------|
| `loki_ip` | `127.0.0.1` | Loki HTTP listening address. |
| `loki_port` | `3100` | Loki HTTP port. |
| `loki_grpc_port` | `9095` | Loki gRPC port. |
| `loki_data_dir` | `/var/lib/loki` | Loki data directory. |
| `loki_retention_period` | `0s` | Delete logs older than this duration, `0s` to keep them forever. |
| `loki_syslog_ip` | `127.0.0.1` | Alloy syslog listener address, receiving rsyslog traffic. |
| `loki_syslog_port` | `1514` | Alloy syslog listener port (TCP). |
| `loki_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open Loki port in, when `loki_ip` is not a loopback address. |
| `loki_enable_services` | `bb_enable_services`, else `true` | Enable loki and alloy services. |
| `loki_start_services` | `bb_start_services`, else `true` | Start loki and alloy services. |

### lustre_client

| Variable | Default | Description |
|----------|---------|-------------|
| `lustre_networks` | `[]` | LNET networks: `name` (LNET name), `network` (inventory network), `clients_groups`. |
| `lustre_mounts` | `[]` | Lustre filesystems: `name`, `path` (file system name, default `name`), `mount_path`, `lnet`, `mgs_servers`, `clients_groups`, `mount_opts`. |
| `lustre_multirail` | `false` | Deploy sysctl settings needed by LNET multi-rail. |

### mariadb

| Variable | Default | Description |
|----------|---------|-------------|
| `mariadb_root_password` | `""` | Root password to set, mandatory (use Ansible Vault). |
| `mariadb_enable_services` | `bb_enable_services`, else `true` | Enable mariadb service. |
| `mariadb_start_services` | `bb_start_services`, else `true` | Start mariadb service. |

Packages (`mariadb-server`, or `mariadb` on Suse, and the PyMySQL Python module used by Ansible) and the Unix
socket path are set per distribution in the role `vars/`.

### nfs

| Variable | Default | Description |
|----------|---------|-------------|
| `nfs_profile` | `[]` | `server` and/or `client`. |
| `nfs_shares` | not set | Shared file systems, see above. |
| `nfs_server_create_directories_if_not_exist` | `true` | Create exported directories on servers. |
| `nfs_server_tuning` | not set | `nfs.conf` sections and parameters. |
| `nfs_client_directories_state` | `mounted` | Mount state on clients. |
| `nfs_client_sebooleans` | `[use_nfs_home_dirs, httpd_use_nfs]` | SELinux booleans enabled on clients. |
| `nfs_server_firewall_services_to_add` | `[nfs, rpc-bind, mountd]` | Firewall services opened on servers. |
| `nfs_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone. |
| `nfs_enable_services` | `bb_enable_services`, else `true` | Enable NFS services. |
| `nfs_start_services` | `bb_start_services`, else `true` | Start NFS services, and apply changes. |

### nhc

| Variable | Default | Description |
|----------|---------|-------------|
| `nhc_packages_to_install` | `[lbnl-nhc]` | NHC packages. |
| `nhc_custom_packages_to_install` | `[]` | Additional packages needed by checks. |
| `nhc_checks` | `{}` | Checks and their arguments, written to `nhc.conf`. |
| `nhc_resources_manager` | not set (auto-detected) | Resources manager (`SLURM`, `PBS`...). |
| `nhc_files` | `[]` | Files (`name` relative to `/etc/nhc`, `content`) copied as is. |

### nic

| Variable | Default | Description |
|----------|---------|-------------|
| `network_interfaces` | (host inventory) | Interfaces to configure, see above and the data model. |
| `nic_reload_connections` | `false` | Reload changed connections. |
| `nic_force_nic_restart` | `false` | Down and up changed connections. |
| `nic_restart_timeout` | `2` | Seconds between down and up. |
| `nic_force_reboot` | `false` | Reboot once if any connection changed. |
| `nic_allow_reboot` | `true` | Allow the role to reboot the host. |
| `nic_reboot_timeout` | `600` | Reboot timeout, in seconds. |
| `nic_nmcli_device_is_connection_name` | `true` | Rename ethernet connections to their device name. |
| `nic_enforce_configuration` | `true` | Do not keep configurations made outside of NetworkManager (`keep-configuration=no`). |
| `nic_enable_services` | `bb_enable_services`, else `true` | Enable NetworkManager. |
| `nic_start_services` | `bb_start_services`, else `true` | Start NetworkManager. |

### pcs

| Variable | Default | Description |
|----------|---------|-------------|
| `pcs_ha_cluster_name` | `ha_cluster` | Cluster name. |
| `pcs_cluster_nodes` | (required) | Cluster nodes (`name`, `addrs`). |
| `pcs_reference_node` | (required) | Node creating the cluster and pushing its configuration. |
| `pcs_ha_cluster_password` | `root` | hacluster user password, used to authenticate nodes. |
| `pcs_ha_cluster_password_sha512` | hash of `root` | hacluster user password hash. |
| `pcs_autostart` | `false` | Enable corosync and pacemaker at boot. |
| `pcs_pcs_property` | `[]` | Cluster properties (`name`, `value`). |
| `pcs_pcs_resource_op_defaults` | `[]` | Resource operations defaults. |
| `pcs_pcs_resource_defaults` | `[]` | Resource defaults. |
| `pcs_resources` | `[]` | Resource groups, with their resources and constraints. |
| `pcs_stonith` | not set | Stonith resources. Not set: STONITH is disabled. |
| `pcs_cib_file_path` | `/root/ha_config.ansible.xml` | Working copy of the cluster configuration. |
| `pcs_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone of the `high-availability` service. |
| `pcs_enable_services` | `bb_enable_services`, else `true` | Enable pcsd. |
| `pcs_start_services` | `bb_start_services`, else `true` | Start pcsd, corosync and pacemaker. |

### pxe_stack

| Variable | Default | Description |
|----------|---------|-------------|
| `pxe_stack_diskful_os_redhat` / `_ubuntu` / `_suse` / `_debian` | `true` | Generate diskful deployment files for this distribution family. |
| `pxe_stack_diskful_os_rhcos` | `false` | Generate RHCOS deployment files. |
| `pxe_stack_enable_diskless` | `true` | Install diskless tools and NFS server. |
| `pxe_stack_diskless_nfs_path` | `/nfs/diskless` | Diskless NFS images path. |
| `pxe_stack_enable_clonezilla` / `_alpine` / `_memtest` | `true` | Provide these tools in the iPXE menu. |
| `pxe_stack_memtest_maxpasses` | `2` | Memtest passes. |
| `pxe_stack_clonezilla_nfs_export_server` / `_mount_point` | not set / `/nfs/cloned_images` | Clonezilla NFS images location. |
| `pxe_stack_time_zone` | `bb_time_zone`, else `Europe/Brussels` | Time zone of deployed hosts. |
| `pxe_stack_enable_root` | `false` | Deploy root access (password, ssh keys) instead of a sudo user. |
| `pxe_stack_sudo_user` / `_home` / `_uid` / `_gid` | `bluebanquise` / `/var/lib/bluebanquise` / `377` / `377` | Sudo user of deployed hosts. |
| `pxe_stack_sudo_is_passwordless` | `true` | Passwordless sudo for the sudo user. |
| `pxe_stack_ssh_allow_passwords` | `true` | Allow ssh password authentication on deployed hosts. |
| `pxe_stack_preserve_repositories` | `true` | Keep distribution repositories enabled after deployment. |
| `pxe_stack_post_install_action` | `reboot` | Action at the end of the installation (`reboot`, `poweroff`, `halt`). |
| `pxe_stack_post_install_boot_to_disk` | `true` | Report the end of installation, so that the host next boots on disk. |
| `pxe_stack_tftp_address` / `_options` / `_directory` | `0.0.0.0:69` / `--secure --verbose` / `/var/lib/tftpboot` | TFTP server settings. |
| `pxe_stack_os_*`, `pxe_stack_hw_*` | see `defaults/main.yml` | Defaults of `os_*` and `hw_*` inventory variables (operating system, console, kernel parameters, keyboard, language, admin password and ssh keys, partitioning, autoinstall content, scripts and repositories, proxies...). |
| `hw_ipxe_default_boot` | `disk` | Default boot entry of hosts. |
| `pxe_stack_ipxe_menu_custom` | `[]` | Custom iPXE menu entries. |
| `pxe_stack_inventory_tag` | not set | Tag written to `/etc/bluebanquise/tags/pxe_inventory` on deployed hosts. |
| `pxe_stack_daemon_port` | `7770` | PXE stack daemon port. |
| `pxe_stack_daemon_log_level` | `INFO` | PXE stack daemon log level. |
| `pxe_stack_daemon_user` | `bluebanquise-pxe` | PXE stack daemon system user, owner of host iPXE files. |
| `pxe_stack_daemon_script_path` / `_conf_path` | `/usr/local/sbin/bluebanquise-pxe-stack-daemon` / `/etc/bluebanquise/pxe_stack_daemon.conf` | PXE stack daemon paths. |
| `pxe_stack_restrict_to_group` | `bb_restrict_to_group`, else `all` | Group of hosts to generate files for. |
| `pxe_stack_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone to open services in. |
| `pxe_stack_enable_services` | `bb_enable_services`, else `true` | Enable services. |
| `pxe_stack_start_services` | `bb_start_services`, else `true` | Start services, and restart them on configuration changes. |

### podman

| Variable | Default | Description |
|----------|---------|-------------|
| `podman_packages_to_install` | `[podman]` | Packages to install. |
| `podman_search_registries` | `[]` | Registries searched for short image names. Empty: distribution default. |
| `podman_insecure_registries` | `[]` | Registries reached without TLS or certificate check. |
| `podman_blocked_registries` | `[]` | Blocked registries. |
| `podman_conf_cgroup_manager` | not set | containers.conf `[engine]` `cgroup_manager`. |
| `podman_conf_events_logger` | not set | containers.conf `[engine]` `events_logger`. |
| `podman_conf_namespace` | not set | containers.conf `[engine]` `namespace`. |
| `podman_containers_conf_content` | not set | Raw TOML content added to the containers.conf drop-in. |
| `podman_storage_driver` | not set | Storage driver. Not set: distribution storage configuration. |
| `podman_storage_mountopt` | not set | Overlay mount options. |
| `podman_users` | `{}` | Users subordinate uids and gids ranges (`user: "start:count"`). |
| `podman_configure_local_registry` | `false` | Deploy a local registry. |
| `podman_local_registry_dir` | `/var/lib/registry` | Local registry storage directory. |
| `podman_local_registry_port` | `5000` | Local registry port. |
| `podman_local_registry_owner` / `_group` | `root` | Owner and group of the registry storage directory. |
| `podman_registry_container_path` | `/var/www/html/images/registry-2.tgz` | Registry image archive. |
| `podman_registry_container` / `_tag` | `registry` / `2` | Registry image name and tag. |
| `podman_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone of the registry port. |
| `podman_enable_services` | `bb_enable_services`, else `true` | Enable the registry service. |
| `podman_start_services` | `bb_start_services`, else `true` | Start the registry service. |

### powerman

| Variable | Default | Description |
|----------|---------|-------------|
| `powerman_packages_to_install` | `[freeipmi, powerman]` | Packages to install. |
| `powerman_enable_ipmi_lan_2_0` | `false` | Use the IPMI 2.0 driver. |
| `powerman_restrict_to_group` | `bb_restrict_to_group`, else `all` | Group of hosts to manage. |
| `powerman_enable_services` | `bb_enable_services`, else `true` | Enable powerman service. |
| `powerman_start_services` | `bb_start_services`, else `true` | Start powerman service. |

### prometheus

| Variable | Default | Description |
|----------|---------|-------------|
| `prometheus_server` / `prometheus_client` | `false` | Deploy server part / client part. |
| `prometheus_server_manage_prometheus` | `true` | Deploy Prometheus. |
| `prometheus_server_manage_alertmanager` | `true` | Deploy Alertmanager. |
| `prometheus_server_manage_karma` | `true` | Deploy Karma. |
| `prometheus_server_manage_ipmi_exporter` | `false` | Deploy ipmi_exporter. |
| `prometheus_server_manage_snmp_exporter` | `false` | Deploy snmp_exporter. |
| `prometheus_server_manage_modbus_exporter` | `false` | Deploy modbus_exporter. |
| `prometheus_server_<tool>_host` | `localhost` | Host running each tool (`prometheus`, `alertmanager`, `karma`, `ipmi_exporter`, `snmp_exporter`, `modbus_exporter`). |
| `prometheus_server_modbus_exporter_listen_address` / `_port` | `prometheus_server_modbus_exporter_host` / `9602` | modbus_exporter listening address and port. |
| `prometheus_server_<tool>_user_uid` / `_user_gid` | `909` to `914` | uid and gid of each tool system user. |
| `prometheus_server_<tool>_launch_parameters` | see above | Launch parameters of each tool. |
| `prometheus_server_<tool>_packages_to_install` | see `defaults/main.yml` | Packages of each tool. |
| `prometheus_server_configuration_global` | see above | Prometheus `global` configuration. |
| `prometheus_server_prometheus_raw_jobs` | not set | Raw scrape jobs added to `prometheus.yml`. |
| `prometheus_server_prometheus_raw_configuration` | not set | Raw configuration added to `prometheus.yml`. |
| `prometheus_server_additional_alerts` | `[]` | Additional alerts files provided by the role (`ipmi_exporter`, `node_exporter`). |
| `prometheus_server_custom_alerts` | not set | Custom alerts file content. |
| `prometheus_server_alertmanager_raw_configuration` | see above | Alertmanager configuration. |
| `prometheus_server_karma_username` / `_password` | `admin` / `admin` | Karma credentials. |
| `prometheus_exporters_to_scrape` | `[]` | Exporters scraped by the server. |
| `prometheus_exporters_groups_to_scrape` | `{}` | Exporters installed on groups of hosts, and scraped by the server. |
| `prometheus_ipmi_scrape_hardware_groups` | `[]` | Hardware groups scraped through ipmi_exporter. |
| `prometheus_snmp_scrape_hardware_groups` | `[]` | Hardware groups scraped through snmp_exporter. |
| `prometheus_modbus_tcp_scrape_hardware_groups` | `[]` | Hardware groups scraped through modbus_exporter. |
| `prometheus_server_snmp_exporter_raw_configuration` | not set | snmp_exporter configuration (`snmp.yml`). |
| `prometheus_server_snmp_exporter_with_generator` | `false` | Install snmp_exporter generator build dependencies. |
| `prometheus_server_modbus_exporter_raw_configuration` | not set | modbus_exporter configuration (`modbus.yml`). |
| `prometheus_server_modbus_exporter_additional_modules` | `[]` | Additional modbus_exporter modules files. |
| `prometheus_firewall_open` | `false` | Open Prometheus, Alertmanager and Karma ports. |
| `prometheus_server_firewall_zone` / `prometheus_client_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zones of server and client ports. |
| `prometheus_server_enable_tls` | `false` | Enable Prometheus TLS. |
| `prometheus_server_tls_cert_file` / `_key_file` | `prometheus.crt` / `prometheus.key` | TLS certificate and key, relative to `/etc/prometheus`. |
| `prometheus_server_enable_basic_auth` | `false` | Enable Prometheus basic authentication. |
| `prometheus_server_basic_auth_user` / `_password` / `_hash_password` | `prometheus` / `prometheus` / bcrypt hash | Basic authentication credentials. |
| `prometheus_enable_services` | `bb_enable_services`, else `true` | Enable services. |
| `prometheus_start_services` | `bb_start_services`, else `true` | Start services, and restart them on configuration changes. |

### rasdaemon

| Variable | Default | Description |
|----------|---------|-------------|
| `rasdaemon_enable_services` | `bb_enable_services`, else `true` | Enable rasdaemon service. |
| `rasdaemon_start_services` | `bb_start_services`, else `true` | Start rasdaemon service. |

### singularity

| Variable | Default | Description |
|----------|---------|-------------|
| `singularity_packages_to_install` | `[singularity-ce]` | Packages to install. |
| `singularity_manage_conf_file` | `true` | Generate `singularity.conf`. |
| `singularity_manage_init_file` | `true` | Generate `init`. |
| `singularity_allow_setuid` | `"yes"` | `allow setuid`. |
| `singularity_allow_pid_ns` | `"yes"` | `allow pid ns`. |
| `singularity_config_passwd` / `_group` / `_resolv_conf` | `"yes"` | `config passwd`, `config group`, `config resolv_conf`. |
| `singularity_mount_proc` / `_sys` / `_dev` / `_devpts` / `_home` / `_tmp` | `"yes"` | `mount proc`, `mount sys`, etc. |
| `singularity_mount_hostfs` | `"no"` | `mount hostfs`. |
| `singularity_mount_slave` | `"yes"` | `mount slave`. |
| `singularity_bind_path` | `[/etc/localtime, /etc/hosts]` | `bind path` entries. |
| `singularity_user_bind_control` | `"yes"` | `user bind control`. |
| `singularity_enable_fusemount` | `"yes"` | `enable fusemount`. |
| `singularity_enable_overlay` | `"try"` | `enable overlay`. |
| `singularity_enable_underlay` | `"yes"` | `enable underlay`. |
| `singularity_init_log_tag` | `singularity` | Syslog tag of container runs. |
| `singularity_init_log_message` | see `defaults/main.yml` | Syslog message of container runs. |

### repositories

| Variable | Default | Description |
|----------|---------|-------------|
| `bb_repositories` | not set | Repositories, see above. |
| `repositories_network` | first `net-` network of the host | Network used to compute simple repositories URL. |
| `override_repositories_environment` | not set | Overrides `os_operating_system.repositories_environment`. |
| `repositories_apt_update_cache` | `true` | Update apt cache when repositories change (Debian, Ubuntu). |
| `repositories_disable_delta_rpm` | `true` | Disable delta RPMs (Suse). |

### rsyslog

| Variable | Default | Description |
|----------|---------|-------------|
| `rsyslog_profile` | (required) | `server` or `client`. |
| `rsyslog_port` | `514` | Syslog port (TCP and UDP). |
| `rsyslog_client_verbosity` | `info` | Minimum level of local messages written to `/var/log/messages`. |
| `rsyslog_server_ip4` | not set | Server to forward logs to, instead of network `log4`/`log` services. |
| `rsyslog_format` | `legacy` (`advanced` on RHEL 9) | Forwarding and imjournal configuration syntax. |
| `rsyslog_server_logrotate` | `true` | Rotate remote logs on servers. |
| `rsyslog_logrotate_config` | not set | Raw remote logs logrotate configuration. |
| `rsyslog_configuration_files` | not set | Additional configuration files (`name`, `content`, optional `path`). |
| `rsyslog_custom_conf_path` / `rsyslog_client_rsyslog_custom_conf_path` / `rsyslog_server_rsyslog_custom_conf_path` | not set | Override generated files paths. |
| `rsyslog_firewall_services_to_add` | `[syslog]` | Firewall services opened on servers. |
| `rsyslog_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone of servers. |
| `rsyslog_enable_services` | `bb_enable_services`, else `true` | Enable rsyslog service. |
| `rsyslog_start_services` | `bb_start_services`, else `true` | Start rsyslog service, and restart it on configuration changes. |

### slurm

Main variables (see the role `defaults/main.yml` and README for all of them):

| Variable | Default | Description |
|----------|---------|-------------|
| `slurm_profile` | (required) | `controller`, `compute` or `submitter`. |
| `slurm_cluster_name` | `bluebanquise` | Slurm cluster name. |
| `slurm_packages_source` | `bluebanquise` | `bluebanquise` or `distribution` packages (Debian, Ubuntu). |
| `slurm_user_uid` / `slurm_user_gid` | see `defaults/main.yml` | slurm user ids. |
| `slurm_computes_config` | `configfull` | `configless` or `configfull` compute nodes. |
| `slurm_enable_accounting` | `false` | Deploy slurmdbd. |
| `slurm_accounting_enable_local_mysql` | `true` | Deploy a local MariaDB for accounting. |
| `slurm_accounting_mysql_login_host` / `_port` | `127.0.0.1` / `3306` | External SQL server. |
| `slurm_accounting_mysql_login_user` / `_password` | not set (`root` with local MariaDB) | Account creating the database and slurm user. |
| `slurm_accounting_mysql_slurm_user` / `_password` | `slurm` / `ssap_slurm` | Database account of slurmdbd (change the password). |
| `slurm_accounting_mysql_create_database` / `_create_user` | `false` | Create the accounting database and user. |
| `slurm_slurmtld_port` / `slurm_slurmd_port` / `slurm_slurmdbd_port` | `6817` / `6818` / see `defaults/main.yml` | Daemons ports. |
| `slurm_acct_gather_*` | see `defaults/main.yml` | `acct_gather.conf` settings. |
| `slurm_enable_services` | `bb_enable_services`, else `true` | Enable services. |
| `slurm_start_services` | `bb_start_services`, else `true` | Start services. |

### ssh_client

| Variable | Default | Description |
|----------|---------|-------------|
| `ssh_client_global_*` | not set | Global parameters, see above. |
| `ssh_client_custom_config` | not set | Raw content added at the top of the file. |
| `ssh_client_restrict_to_group` | `bb_restrict_to_group`, else `all` | Group of hosts to write. |

### ssh_remote_keys

| Variable | Default | Description |
|----------|---------|-------------|
| `os_admin_ssh_keys` | not set | Public keys to authorize. |
| `ssh_remote_keys_os_admin_ssh_keys` | `[]` | Public keys to authorize when `os_admin_ssh_keys` is not set. |

### sshd

| Variable | Default | Description |
|----------|---------|-------------|
| `sshd_permitrootlogin` | not set | `PermitRootLogin` (`yes`, `no`, `prohibit-password`...). |
| `sshd_passwordauthentication` | not set | `PasswordAuthentication`. |
| `sshd_denyusers` / `sshd_allowusers` | not set | `DenyUsers` / `AllowUsers` (space separated). |
| `sshd_denygroups` / `sshd_allowgroups` | not set | `DenyGroups` / `AllowGroups` (space separated). |
| `sshd_raw` | not set | Raw directives, written first. |
| `sshd_server_firewall_services_to_add` | `[ssh]` | Firewall services to open. |
| `sshd_server_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone. |
| `sshd_server_enable_services` | `bb_enable_services`, else `true` | Enable sshd service. |
| `sshd_server_start_services` | `bb_start_services`, else `true` | Start sshd service, and restart it on configuration changes. |

### time

| Variable | Default | Description |
|----------|---------|-------------|
| `time_profile` | (required) | `server` or `client`. |
| `time_external_pools` | `[]` | External pools to use instead of internal servers. |
| `time_external_servers` | `[]` | External servers to use instead of internal servers (if no pool). |
| `time_additional_networks_allowed` | `[]` | Additional networks allowed to query the server (`subnet/prefix`). |
| `time_time_zone` | `bb_time_zone`, else `Europe/Brussels` | Time zone. |
| `time_chronyd_options` | not set | chronyd launch options. |
| `time_chrony_custom_conf_path` | not set | Override chrony configuration file path. |
| `time_firewall_services_to_add` | `[ntp]` | Firewall services to open. |
| `time_firewall_zone` | `bb_services_firewall_zone`, else `public` | Firewall zone. |
| `time_enable_services` | `bb_enable_services`, else `true` | Enable chrony service. |
| `time_start_services` | `bb_start_services`, else `true` | Start chrony service, and restart it on configuration changes. |

### update_reboot

| Variable | Default | Description |
|----------|---------|-------------|
| `update_reboot_upgrade_packages` | `false` | Upgrade all packages. |
| `update_reboot_reboot` | `false` | Reboot hosts when packages were upgraded. |
| `update_reboot_reboot_timeout` | `600` | Reboot timeout, in seconds. |

### users

| Variable | Default | Description |
|----------|---------|-------------|
| `users` | not set | Users to manage, see above. |
| `users_enable_ssh_authorized_keys` | `true` | Manage users `authorized_keys`. |

### xfs_quota

| Variable | Default | Description |
|----------|---------|-------------|
| `xfs_quota` | not set | Quotas to set (`type`, `mountpoint`, `name`, `bsoft`, `bhard`, `isoft`, `ihard`, `rtbsoft`, `rtbhard`, `state`). |
