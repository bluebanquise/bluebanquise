# haproxy

## Description

This role deploy a basic haproxy configuration to be used in high availability
context.
The role will restrict http server ip to non virtual ones, and configure
haproxy to listen on a virtual ip and send requests to defined nodes, in a
round robin configuration.

Basic usage is to spread load with repositories and diskless.

## Instructions

### Basic usage

Basic configuration is the following:

```
haproxy_bind_ip: 10.10.0.7     # Virtual ip on which haproxy should listen

haproxy_nodes:                 # List of http servers, and ip:port to receive haproxy requests
  - name: ha1
    ip: 10.10.0.1
    port: 80
  - name: ha2
    ip: 10.10.0.2
    port: 80
```

Note: `haproxy_bind_ip` ip must be the one matching `services_ip.repository_ip`
of your main network in networks configuration.

This will create the following configuration:

```
 http server                  http server
     ha1                          ha2
  10.10.0.1                    10.10.0.2
      ▲         round robin        ▲
      └──────────────┬─────────────┘
                     │
                  haproxy
                 10.10.0.7
                     ▲
                     │
                     │
                     │
                http request
```

Note that by default, the configuration done on http servers simply disable
listen on all interfaces, and restrict listening to all ip defined in
`network_interfaces` variable of each server.

It is possible to further restrict http server to only ip defined under `haproxy_nodes`
by setting variable `haproxy_restrict_nodes_http_listen` to `true`.

The role will not start haproxy service, as it should be defined in an active-passive
HA implementation (for example using the high_availability role of the stack).

### Integration in high_availability role

First, ensure no httpd resources are registered into PCS.

Then, add haproxy new resource into HA configuration inside inventory:

```
high_availability_resources:
  - group: haproxy
    resources:
      - id: vip-haproxy
        type: IPaddr2
        arguments: "ip=10.10.0.7 cidr_netmask=255.255.0.0"
      - id: service-haproxy
        type: systemd:haproxy
```

And push these new resources into PCS using the `high_availability` role.

If ip was changed during the process, ensure `vip-haproxy` still match
`services_ip.repository_ip` of your main network in networks configuration.

## Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
