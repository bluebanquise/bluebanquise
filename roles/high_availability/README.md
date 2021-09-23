# High Availability

- [High Availability](#high-availability)
  * [1. Description](#1-description)
  * [2. Instructions to configure](#2-instructions-to-configure)
    + [2.1. HA cluster](#21-ha-cluster)
    + [2.2. Properties](#22-properties)
    + [2.3. Resources](#23-resources)
    + [2.4. Constraint](#24-constraint)
      - [2.4.1. Collocation constraint](#241-collocation-constraint)
      - [2.4.2. Location constraint](#242-location-constraint)
    + [2.5. Stonith](#25-stonith)
  * [3. Deploy HA](#3-deploy-ha)
  * [4. List of standard resources](#4-list-of-standard-resources)
    + [4.1. Repositories and PXE](#41-repositories-and-pxe)
    + [4.2. DHCP server](#42-dhcp-server)
    + [4.3. DNS server](#43-dns-server)
    + [4.4. Time server](#44-time-server)
    + [4.5. Log server](#45-log-server)
  * [5. Changelog](#5-changelog)

## 1. Description

This role deploy and Active-Passive HA cluster based on PCS (corosync-pacemaker).

The role creates HA cluster on requested nodes, and then populate it with
desired resources and constraint.

This role can be combined with DBRD role to obtain shared storage across nodes.

The target cluster is an `1+N` ha nodes. The example here is based on a cluster
of 3 ha servers working together.

```
  ┌────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │      ha1       │          │       ha2       │          │       ha3       │
  │                │          │                 │          │                 │
  │                │          │                 │          │                 │
  │                │          │                 │          │                 │
  │                │          │                 │          │                 │
  │                │          │                 │          │                 │
  └────────────┬───┘          └────────┬────────┘          └────┬────────────┘
               │                       │                        │
               │                       │                        │
               └───────────────────────┴────────────────────────┘
                                    Network
```

## 2. Instructions to configure

Ensure your nodes are able to install HA components (may require a special
 subscription on RHEL OS).

### 2.1. HA cluster

Create a group called `ha_cluster` that contains only your HA cluster nodes.
To do so, create file `inventory/cluster/groups/ha_cluster` with the following
content:

```
[ha_cluster]
ha1
ha2
ha3
```

Then in `inventory/group_vars/ha_cluster` folder, create a file
`ha_parameters.yml` with the following variables, tuned to your needs:

```yaml
high_availability_cluster_nodes:
  - name: ha1             # Hostname of the HA cluster nodes
    addrs:                # List of addresses to be used for HA ring (allow multiple rings for redundancy)
      - ha1
  - name: ha2
    addrs:
      - ha2
  - name: ha3
    addrs:
      - ha3
```

You can add multiple `addrs` instead of one, to allow multiple networks (rings)
to secure HA cluster in case one network fail:

```
 ┌────────────────┐          ┌─────────────────┐          ┌─────────────────┐
 │      ha1       │          │       ha2       │          │       ha3       │
 │                │          │                 │          │                 │
 │                │          │                 │          │                 │
 │                │          │                 │          │                 │
 │                │          │                 │          │                 │
 │                │          │                 │          │                 │
 └───────┬────┬───┘          └────────┬─────┬──┘          └────┬────┬───────┘
         │    │                       │     │                  │    │
         │    │                       │     │                  │    │
         │    └───────────────────────┴─────┼──────────────────┘    │
         │                         Network  │                       │
         │                                  │                       │
         └──────────────────────────────────┴───────────────────────┘
                                      2nd Network
```

So for example here:

```yaml
high_availability_cluster_nodes:
  - name: ha1             # Hostname of the HA cluster nodes
    addrs:                # List of addresses to be used for HA ring (allow multiple rings for redundancy)
      - ha1
      - ha1-2nd-network
  - name: ha2
    addrs:
      - ha2
      - ha2-2nd-network
  - name: ha3
    addrs:
      - ha3
      - ha3-2nd-network
```

You now need to select a reference node in this pool. This node will be the one
that initiate HA cluster, register the other nodes in it, and populate resources.
These actions can only be done by one member of the pool at a time.
Note that once the cluster is created, the reference node can be any one from
the pool that is already registered in the HA cluster.

To set reference node, you need to use variable `high_availability_reference_node`.
You can set the reference node in the `ha_parameters.yml`, and on need, use
`--extra-vars` at `ansible-playbook` invocation to use another one:

```yaml
high_availability_reference_node: ha1
```

Fianly, before deploying HA cluster, update
`high_availability_ha_cluster_password`variable with a new SHA512 password hash
(do not use default one for production).

```yaml
high_availability_ha_cluster_password: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
```

Now deploy the HA cluster with these parameters.

Check cluster status after role deployment using:

```
pcs status
```

All nodes should be online.

If all goes well, it is then possible to add properties, resources,
constraints and stonith.

### 2.2. Properties

Three kind of properties are supported currently by this role:

* pcs property
* psc resource op defaults
* pcs resource defaults

For each, it is possible to define a list of properties with their value. For
example:

```yaml
high_availability_pcs_property:
  - name: cluster-recheck-interval
    value: 250
high_availability_pcs_resource_op_defaults:
  - name: action-timeout
    value: 40
high_availability_pcs_resource_defaults:
  - name: resource-stickiness
    value: 4300
  - name: migration-threshold
    value: 1
  - name: failure-timeout
    value: 40
```

You can also skip this part and do not set any properties, to keep distribution
default values.

### 2.3. Resources

A resource is an event (a service running, a partition mounted, a virtual ip
  created, etc.) shared between nodes. These resources can be instructed to
run on a single node of the pool at a time, or to be running as clones on
multiple nodes at the same time.

Resources are to be defined under variable `high_availability_resources`.
The role manage resources using groups, which acts as colocation constraint
(resources of the same group MUST be running on the same host at the same time),
and using definition order under that groups, which acts as a start order
constraint (if the first resource in the list fail to start, the second one
  will not start, etc).

For example:

```yaml
high_availability_resources:
  - group: http
    resources:
      - id: vip-http
        type: IPaddr2
        arguments: "ip=10.10.0.7 cidr_netmask=255.255.0.0"
      - id: service-http
        type: systemd:httpd
  - group: dns
    resources:
      - id: vip-dns
        type: IPaddr2
        arguments: "ip=10.10.0.8 cidr_netmask=255.255.0.0"
      - id: service-dns
        type: systemd:named
```

In this example, resource `vip-http` and `service-http` belongs to the same
group `http`, and so will be running on the same host at the same time.
Also, since `vip-http` is listed before `service-http`, if `vip-http` fail to
start, then `service-http` will not start.

```
  ┌────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │      ha1       │          │       ha2       │          │       ha3       │
  │                │          │                 │          │                 │
  │                │          │                 │          │                 │
  │                │          │                 │          │                 │
  │                │          │                 │          │                 │
  │                │          │  httpd          │          │  named          │
  └────────────┬───┘          └────────┬────────┘          └────┬────────────┘
               │             10.10.0.7 │              10.10.0.8 │
               │                       │                        │
               └───────────────────────┴────────────────────────┘
                                    Network
```

A list of resources examples for BlueBanquise CORE is provided at the end of
this README.

### 2.4. Constraint

Now that cluster is running resources, it is possible to add specific constraint
on groups (on top of groups and start order constraint already in place).

Two kind of constraints are available with this role: collocation and location.

#### 2.4.1. Collocation constraint

Collocation allows to force a group to be close or not to another group.
The very common usage is to define collocation constraint that prevent some
group to be running on the same host than another.

For example, to set that `dns` group should never be running on the same host
than `http` group, add a colocation constraint on dns group this way:

```yaml
high_availability_resources:
  - group: http
    resources:
      - id: vip-http
        type: IPaddr2
        arguments: "ip=10.10.0.7 cidr_netmask=255.255.0.0"
      - id: service-http
        type: systemd:httpd
  - group: dns
    resources:
      - id: vip-dns
        type: IPaddr2
        arguments: "ip=10.10.0.8 cidr_netmask=255.255.0.0"
      - id: service-dns
        type: systemd:named
    colocations:
      - slave: http
        score: -INFINITY
```

#### 2.4.2. Location constraint

Location allows to set a preferred node for a group of resources. This can be
useful to ensure a good load balancing between the ha cluster nodes.

For example, to set that `http` groups should be running on ha 2 node:

```yaml
high_availability_resources:
  - group: http
    resources:
      - id: vip-http
        type: IPaddr2
        arguments: "ip=10.10.0.7 cidr_netmask=255.255.0.0"
      - id: service-http
        type: systemd:httpd
    locations:
      - type: prefers
        nodes:
          - ha2
```

Type can be `prefers` and `avoids`.

### 2.5. Stonith

Stonith (for "Shoot The Other Node In The Head") allows to prevent issues when a
node of the cluster is not working as expected or is unsynchronized with others.

It is possible to define stonith resources using this role. For example, to
define an IPMI stonith, use:

```yaml
high_availability_stonith:
  - name: fenceha1
    type: fence_ipmilan                                                # IPMI fencing
    pcmk_host_check: static-list
    pcmk_host_list: ha1                                                # Target host to be stonith if issues
    pcmk_reboot_action: reboot                                         # Ask for reboot if fencing
    parameters: ipaddr=10.10.102.1 login=ADMIN passwd=ADMIN cipher=3   # Target host BMC ip and auth parameters for IPMI fencing
    prefers: ha2                                                       # Where this resource should be running
    avoids: ha1                                                        # Avoid resource to be running on own host
```

## 3. Deploy HA

The HA cluster is expected to have an active-passive configuration.
The structure of this playbook named "ha-cluster.yml" can be used as a starting
point:

```yaml
- name: Roles for HA cluster
  hosts: "ha_cluster"
  vars:
    enable_services: false
    start_services: false
  roles:
    - (add roles to configure services in HA cluster)
    - role: high_availability
      tags: ha
```

By doing this, all ha compatible roles services will be disabled and not started.
Then HA cluster will be deployed, and populated with resources and properties.

First, start by configuring services in active mode on the reference node,
 set to ha1 for this example:

```
ansible-playbook ha-cluster.yml --limit ha1 --skip-tags ha -e "{'start_services': true}"
```

Now, deploy the HA cluster with the configured parameters, by running the full
playbook on all nodes. Note that other nodes will get the passive configuration,
so this playbook can be safely executed multiple times:

```
ansible-playbook ha-cluster.yml
```

## 4. List of standard resources

Bellow is a list of standard resources to be used with BlueBanquise. Note that
it can/must be adapted to needs (other kind of FS, multiple vip to handle multiple
  subnets, etc.).

### 4.1. Repositories and PXE

Since both repositories and PXE share the same service (http server), these must
be combined together in a same group.
Note that depending of tftp server used, service to set might be different.

Also, since bootset tool need to be usable from all nodes,
preboot_execution_environment folder should be in a separate volume, mounted and
exported through nfs, and mounted over nfs by all other HA cluster nodes.

So at the end, you need for this part 2 available FS shared between nodes, here
`/dev/repositories` and `/dev/pxe`, and a vip, here `10.10.77.1`.

```yaml
- group: http
  resources:
    - id: fs-repositories
      type: Filesystem
      arguments: "device='/dev/repositories' directory='/var/www/html/repositories/' fstype='ext4'"
    - id: fs-pxe
      type: Filesystem
      arguments: "device='/dev/pxe' directory='/exports/pxe/' fstype='ext4'"
    - id: vip-http
      type: IPaddr2
      arguments: "ip=10.10.77.1 cidr_netmask=255.255.0.0"
    - id: nfs-daemon-http
      type: nfsserver
      arguments: "nfs_shared_infodir=/exports/pxe/nfsinfo nfs_no_notify=true"
    - id: nfs-export-pxe
      type: exportfs
      arguments: "clientspec=* options=rw,sync,no_root_squash directory=/exports/pxe/ fsid=0"
    - id: service-http
      type: systemd:httpd
    - id: service-tftp
      type: systemd:atftpd

- group: pxe_mount
  resources:
    - id: nfs-mount-pxe
      type: Filesystem
      arguments: "device=10.10.77.1:/exports/pxe/ directory=/var/www/html/preboot_execution_environment/ fstype=nfs clone interleave=true"
```

So you should see something like this at the end for nfs-mount-pxe:

```
* Clone Set: nfs-mount-pxe-clone [nfs-mount-pxe]:
  * Started: [ ha1 ha2 ]
```

Where all nodes mount the nfs volumeZ.

### 4.2. DHCP server

DHCP server do not need a virtual ip, expect for very specific cases.
Resource is simple to declare as only dhcp service is needed.

```yaml
- group: dhcp
  resources:
    - id: service-dhcp
      type: systemd:dhcpd
```

### 4.3. DNS server

DNS server need a virtual ip, and the dns service.

```yaml
- group: dns
  resources:
    - id: vip-dns
      type: IPaddr2
      arguments: "ip=10.10.77.2 cidr_netmask=255.255.0.0"
    - id: service-dns
      type: systemd:named
```

### 4.4. Time server

Time server is a bit tricky.
Chrony daemon is running on both clients and servers, and is using the same
configuration file path.

To solve this, execute `time` role 2 times, but with different configuration
path and client/server setting. Switch is then made using a simple
`ocf_heartbeat_symlink` resource and collocation constraint.

In the playbook, use:

```yaml
roles:
  - role: time
    tags: time
    vars:
      time_profile: server
      time_chrony_custom_conf_path: /etc/chrony-server.conf
  - role: time
    tags: time
    vars:
      time_profile: client
      time_chrony_custom_conf_path: /etc/chrony-client.conf
tasks:
  - name: Remove base chrony configuration
    file:
      path: /etc/chrony.conf
      state: absent
```

This will generate both configurations, and ensure the default configuration is
not present. Then in HA resources, declare the following:

```yaml
- group: time-server
  resources:
    - id: vip-time-server
      type: IPaddr2
      arguments: "ip=10.10.77.3 cidr_netmask=255.255.0.0"
    - id: time-server-symlink
      type: ocf:heartbeat:symlink
      arguments: "target=/etc/chrony-server.conf link=/etc/chrony.conf"
    - id: service-time-server
      type: systemd:chronyd

- group: time-client
  resources:
    - id: time-client-symlink
      type: ocf:heartbeat:symlink
      arguments: "target=/etc/chrony-client.conf link=/etc/chrony.conf clone interleave=true"
    - id: service-time-client
      type: systemd:chronyd
  colocations:
    - slave: time-server
      score: -INFINITY
```

### 4.5. Log server

Log server act as time server, you need to create 2 files, one for server and
one for client.

In the playbook, use:

```yaml
roles:
  - role: log_server
    tags: log
    vars:
      log_server_rsyslog_custom_conf_path : /etc/rsyslog-server.conf
  - role: log_client
    tags: log
    vars:
      log_client_rsyslog_custom_conf_path : /etc/rsyslog-client.conf
tasks:
  - name: Remove base rsyslog configuration
    file:
      path: /etc/rsyslog.conf
      state: absent
```

This will generate both configurations, and ensure the default configuration is
not present. Then in HA resources, declare the following:

```yaml
- group: log-server
  resources:
    - id: fs-log-server
      type: Filesystem
      arguments: "device='/dev/log-server' directory='/var/log/rsyslog/' fstype='ext4'"
    - id: vip-log-server
      type: IPaddr2
      arguments: "ip=10.10.77.4 cidr_netmask=255.255.0.0"
    - id: log-server-symlink
      type: ocf:heartbeat:symlink
      arguments: "target=/etc/rsyslog-server.conf link=/etc/rsyslog.conf"
    - id: service-log-server
      type: systemd:rsyslog

- group: log-client
  resources:
    - id: log-client-symlink
      type: ocf:heartbeat:symlink
      arguments: "target=/etc/rsyslog-client.conf link=/etc/rsyslog.conf"
    - id: service-log-client
      type: systemd:rsyslog
  colocations:
    - slave: log-server
      score: -INFINITY
```

## 5. Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
