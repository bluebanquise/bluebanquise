# Conman

## Description

These settings provide a conman daemon that logs ipmi serial consoles.

Conman is extremely efficient when managing large groups of hosts, to gather console logs, switch between consoles, share consoles, etc.

## Instructions

Files generated:

* /etc/conman.conf

These settings will automatically look for equipment profile variables and bmc registered of each hosts.

To make an host conman compatible in the inventory, ensure the `bmc` dict is set for the target host, and that target host as access (host_vars, group_vars, etc) to and `hw_board_authentication` list with IPMI protocol registered.

An ultra basic example would be:

```yaml
all:
  hosts:
    myserver1:
      bmc:
        name: bmyserver1
        ip4: 10.10.100.1
        network: net1-1
        mac: XX:XX:XX:XX:XX:XX
      network_interfaces:
        - interface: eno1
          ip4: 10.10.0.1
          network: net1-1
          mac: YY:YY:YY:YY:YY:YY
```

And:

```ini
[all:vars]
hw_board_authentication="[{'protocol': 'IPMI', 'user': 'ADMIN', 'password': 'ADMIN'}]"
```

Note however that `hw_board_authentication` was originally designed to be used for equipment profiles groups, but can be set this way if using BlueBanquise as a standalone collection.

### Conman usage

To login into a console, use:

```
conman mynode
```

To exit, simply press `Enter` then `&` then `.` .

### Resources limits

Be aware however that conman was NOT designed to manage too much hosts, due to the number of threads started. If you need to manage more than 1000 servers, it is recommended to split cluster into multiple icebergs (see BlueBanquise stack main documentation) to spread load over multiple conman instances.

Another solution, if system is strong enough, is to increase RLIMIT_NOFILE for conman user to greater values than default ones (https://github.com/dun/conman/issues/17). User can make usage of `pam_limits` BlueBanquise role to configure conman user rlimits.

```yaml
pam_limits:
  - domain: conman
    limit_type: soft
    limit_item: nofile
    value: unlimited
    use_max: yes
  - domain: conman
    limit_type: hard
    limit_item: nofile
    value: unlimited
    use_max: yes
```

Once these pam_limits parameter pushed, restart conman daemon.
