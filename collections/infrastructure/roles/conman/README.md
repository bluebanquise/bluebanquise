# Conman

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 2 (Hosts definition)
* Section 3.2 (Hardware Groups)

## Description

This role provides a conman daemon that logs ipmi serial consoles.

Conman is extremly efficient when managing large group of hosts, to gather consols logs, switch between consoles, share consoles, etc.

## Instructions

Files generated:

* /etc/conman.conf

Conman role will automatically look for equipment profile variables and bmc registered of each hosts.

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
hw_board_authentication="[{'protocol': 'IPMI', 'user': 'ADMIN', 'pass': 'ADMIN'}]"
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

## Changelog

* 1.7.0: Added ssh config file for user conman. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.6.0: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.1: Fix logrotate paths. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.5.0: Add logrotate file. Matthieu Isoard <indigoping4cgmi@gmail.com>
* 1.4.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Add OpenSuSE support. Neil Munday <neil@mundayweb.com>
* 1.1.0: Implement support for externaly defined BMC. johnnykeats <johnny.keats@outlook.com>
* 1.0.6: Force conman user gid/uid. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Prevent unsorted ranges. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.4: Run the conman service with user conman. Bruno Travouillon <devel@travouillon.fr>
* 1.0.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.2: Tested on ubuntu 18.04 and validated. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
