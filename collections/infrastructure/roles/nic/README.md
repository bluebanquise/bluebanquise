# Network Interface Controllers - NIC

**WARNING!** Always keep in mind that using this role, you could lose connection! Always have a backup way to reach the system.

Important note: NetworkManager is know to have a small issue with gateways/routes. When you set a gateway or a route, in order for it to be updated, you often have to at least down and up the related interface, or even reboot the system. Please keep that in mind.

## Description

This role configure network interfaces to provide desired ip, prefix, gateway, etc.
The role also covers routes definitions on interfaces and other advanced settings.

This role relies on nmcli (NetworkManager) module from community.general collection will be used to configure network.The role should provide all features available in the main nmcli module.
Please refer to [nmcli module documentation]( https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html) .

## Instructions

### Specific behaviors

While we try to bind to nmcli module options for convention, some role's keys provide more integrated features:

* `conn_name`: is equal to `interface`, but has higher precedence over
  `interface` if both are set.
* `ifname`: is equal to `physical_device`, but has higher precedence over
  `ifname` if both are set.
* `type`: is set to **ethernet** by default.
* `ip4`: can be set using a simple ipv4, then role will use
  `networks[item.network]['prefix4']` or default to
  `networks[item.network]['prefix']` to complete address. You can force
  address with prefix if string `/` is present (example: 10.10.0.1/16).
* `ip4_manual`: allows to pass additional list of ip/prefix to role.
* `mtu`: has higher precedence over `networks[item.network]['mtu']` if
  both are set.
* `gw4`: has higher precedence over `networks[item.network]['gateway4']`
  if set which has higher precedence over `networks[item.network]['gateway']`
  if set. Note that gw4 is cannot be set at the same time than `never_default4`
  (mutually exclusives).
* `routes4`: is a list, that defines routes to be set on the interface. See
  examples bellow. It has higher precedence over
  `networks[item.network]['routes4']` if set.
* `route_metric4`: is to set general metric for gateway or routes (if not set
  on route level) for this interface. Has higher precedence over
  `networks[item.network]['route_metric4']` if set.
* `never_default4`: is related to ipv4.never-default nmcli parameter
  (DEFROUTE). Has higher precedence over
  `networks[item.network]['never_default4']` if set.

### Basic ipv4

```yaml
network_interfaces:
  - interface: eth0
    ip4: 10.10.0.1
    network: net-1
```

Or if not linked to a stack network:

```yaml
network_interfaces:
  - interface: eth0
    ip4: 10.10.0.1/16
```

### Force gateway and MTU

```yaml
network_interfaces:
  - interface: eth0
    ip4: 10.10.0.1
    network:net-1
    gw4: 10.10.2.1
    mtu: 9000
```

### Multiple ip

In multiple ip modes, you need to set the prefix yourself:

```yaml
network_interfaces:
  - interface: eth0
    ip4: 10.10.0.1
    ip4_manual: 
      - 10.10.0.2/16
      - 10.10.0.3/16
    network: net-1
```

Note: you can use `ip4_manual` without `ip4` only if 
the corresponding interface is not to be used as main resolution interface
or main interface (which means another interface with an ip4 and linked to 
a management network is set above in the *network_interfaces* list).

### Bond

```yaml
network_interfaces:
  - interface: bond0
    ip4: 10.10.0.1
    network: net-1
    type: bond
  - interface: eth0
    type: bond-slave
    master: bond0
  - interface: eth1
    type: bond-slave
    master: bond0
```

**WARNING**
  In BlueBanquise, as the roles are relying on network_interfaces list order,
  never place bond-slave above the bond master (here bond0 definition must be
  set above eth0 and eth1).

### Vlan

```yaml
network_interfaces:
  - interface: eth2.100
    type: vlan
    vlanid: 100
    vlandev: eth2
    ip4: 10.100.0.1
    network: net-100
```

Refer to [nmcli module documentation](https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html)
for more options.

### Routes

You can define routes at two levels:

* In networks.yml, inside a network. For example:

```yaml
networks:
  net-1:
    subnet: 10.10.0.0
    prefix: 16
    netmask: 255.255.0.0
    broadcast: 10.10.255.255
    routes4:
      - 10.11.0.0/24 10.10.0.2
      - 10.12.0.0/24 10.10.0.2 300
```

* Or under host definition, so in hostvars:

```yaml
hosts:
  management1:
    network_interfaces:
      - interface: enp0s8
        ip4: 10.10.0.1
        mac: 08:00:27:36:c0:ac
        network:net-1
        routes4:
          - 10.11.0.0/24 10.10.0.2
          - 10.12.0.0/24 10.10.0.2 300
```

Note: in route4 list, each element of the list is a tuple with the network
destination in first position, gateway in second position and optionally
the metric in third position.

### Apply changes

By default, if interfaces are down, the role will have them up, and at the same 
time set their configuration.

However, in some cases, users might need to force some updates (for example if 
you wish to set routes on the main interface, etc).

To achieve that, few variables are at disposal:

* `nic_reload_connections`: this variable will trigger a handler that will ask NetworkManager to reload its configuration.
* `nic_force_nic_restart`: this variable will trigger a task that will manually down and up interfaces. To be used with care.
* `nic_restart_timeout`: this variable is used with nic_force_nic_restart to specify the time to wait between connection down and up actions. Default value is 2s.
* `nic_reboot`: this variable will trigger a reboot if any nic configuration changed. To be used with care.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.11.0: Make NetworkManager default for all OS. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.10.1: Make the connection restart timeout configurable <jean-pascal.mazzilli@gmail.com>
* 1.9.1: Add missing slave_type key. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.0: Allow services and services_ip together. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.8.0: Add new nmcli keys. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.7.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.1: Add missing dns entry. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.0: Add OpenSuSE 12 and 15 support. Neil Munday <neil@mundayweb.com>
* 1.5.3: Improve Ubuntu compatibility. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.2: Add reboot capability, needed on some system. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.1: Add missing register of nic_nmcli_apply variable. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.5.0: Add ip4_manual entry. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Add DNS4 and DNS4_SEARCH vars logic. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Rewrite logic to prevent crash and ease code reading. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Add routes4, route_metric4, never_default4 and zone. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Add routes support on NIC. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Rewamp full role to handle all nmcli module features. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Adding Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
