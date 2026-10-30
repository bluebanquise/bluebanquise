# Conman

## Description

This role provides a conman daemon that logs hosts serial consoles, through their BMC: IPMI Serial Over LAN, or SSH for Redfish based BMCs.

Conman is extremely efficient when managing large groups of hosts, to gather console logs, switch between consoles, share consoles, etc.

## Instructions

Files generated:

* /etc/conman.conf
* /etc/logrotate.d/conman (only if not already provided by the conman package)
* /var/lib/conman/.ssh/config (SSH options used to reach Redfish BMCs consoles)

The role registers in conman.conf each host (with `hw_equipment_type` set to `server`, the default) that has:

* A `bmc` entry with a `name`. Console connections use this name, which must be resolvable from the management host (typically through the `hosts_file` or `dns_server` roles).
* A `hw_board_authentication` list, usually set in its hardware group, with an `IPMI` or `REDFISH` protocol entry. If both protocols are defined, IPMI is used.

An ultra basic example would be:

```yaml
all:
  hosts:
    myserver1:
      bmc:
        name: bmyserver1
        ip4: 10.10.100.1
        network: net-admin
        mac: XX:XX:XX:XX:XX:XX
      network_interfaces:
        - interface: eno1
          ip4: 10.10.0.1
          network: net-admin
          mac: YY:YY:YY:YY:YY:YY
```

And in the host hardware group variables (for example `group_vars/hw_supermicro_X1/hw.yml`):

```yaml
hw_board_authentication:
  - protocol: IPMI
    user: ADMIN
    password: ADMIN
```

With Redfish, the console is reached using SSH to the BMC, on port `conman_redfish_console_port` (default 22), which can be set per hardware group using the `console_port` key:

```yaml
hw_board_authentication:
  - protocol: REDFISH
    user: ADMIN
    password: ADMIN
    console_port: 2200
```

On RedHat family systems, the conmand daemon runs as the `conman` user instead of root (systemd drop-in `/etc/systemd/system/conman.service.d/user.conf`).

### Conman usage

To login into a console, use:

```
conman mynode
```

To exit, simply press `Enter` then `&` then `.` .

### Resources limits

Be aware however that conman was NOT designed to manage too many hosts, due to the number of threads started. If you need to manage more than 1000 servers, it is recommended to split cluster into multiple icebergs (see BlueBanquise stack main documentation) to spread load over multiple conman instances.

Another solution, if system is strong enough, is to increase RLIMIT_NOFILE for conman user to greater values than default ones (see [conman issue 17](https://github.com/dun/conman/issues/17)). User can make usage of the `local_configuration` BlueBanquise role's PAM limits support to configure conman user rlimits.

```yaml
local_configuration_system:
  pam_limits:
    - domain: conman
      limit_type: soft
      limit_item: nofile
      value: unlimited
      use_max: true
    - domain: conman
      limit_type: hard
      limit_item: nofile
      value: unlimited
      use_max: true
```

Once these pam_limits parameters are pushed, restart the conman daemon.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `conman_restrict_to_group` | `bb_restrict_to_group`, else `all` | Only register hosts of this Ansible group. |
| `conman_redfish_console_port` | `22` | SSH port of Redfish BMCs consoles, when not set per hardware group (`console_port` key of `hw_board_authentication`). |
| `conman_user_uid` | `287` | UID of the conman user. |
| `conman_user_gid` | `287` | GID of the conman group. |
| `conman_user_home` | `/var/lib/conman` | Home of the conman user, storing its SSH configuration. |
| `conman_enable_services` | `bb_enable_services`, else `true` | Enable conman at boot. |
| `conman_start_services` | `bb_start_services`, else `true` | Start conman, and restart it on configuration change. |
