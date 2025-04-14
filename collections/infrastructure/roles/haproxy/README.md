# haproxy

## Description

This role deploy a basic haproxy configuration to be used in high availability context. It can be used as pure high availability, or as a load balancing mechanism.

Example usage is to spread load on packages repositories, diskless images, etc.

For details on how haproxy operate, please read https://www.digitalocean.com/community/tutorials/an-introduction-to-haproxy-and-load-balancing-concepts

## Instructions

This role offers currently 2 main parameters and 4 resources type to be set:

* Parameters:
  * Globals
  * Defaults
* Resources:
  * frontend
  * backend
  * http_simple
  * http_load_balancer

This allows for simple or advanced usage.

## Parameters

### Global parameters

By default, role will use conservative settings from HAproxy online documentation:

```
    log /dev/log local0
    user        haproxy
    group       haproxy
    chroot      /var/lib/haproxy
    stats socket /run/haproxy/admin.sock user haproxy group haproxy mode 660 level admin
    nbproc      2
    nbthread    4
    maxconn     50000
    ssl-default-bind-ciphers PROFILE=SYSTEM
    ssl-default-server-ciphers PROFILE=SYSTEM
    daemon
```

If you with to use something different, you can set variable `haproxy_global_parameters` as a multiple lines string to **fully replace** these settings. Note that template will automatically indent the content as needed.

For example, if a very minimal configuration is preferred:

```yaml
haproxy_global_parameters: |
  log 127.0.0.1 local2
  user        haproxy
  group       haproxy
```

Please refer to official documentation for more details on available settings: https://www.haproxy.com/documentation/hapee/latest/configuration/config-sections/

Note that the following page might be better as much more detailed: https://docs.haproxy.org/2.6/configuration.html

### Defaults parameters

By default, role will use the following settings from HAproxy online documentation:

```
    timeout connect 10s
    timeout client 30s
    timeout server 30s
    log global
    mode http
    option httplog
    maxconn 5000
```

If you with to use something different, you can set variable `haproxy_defaults_parameters` as a multiple lines string to **fully replace** these settings. Note that template will automatically indent the content as needed.

For example:

```yaml
haproxy_defaults_parameters: |
  timeout connect 20s
  mode tcp
  maxconn 100
```

Please refer to official documentation for more details on available settings: https://www.haproxy.com/documentation/hapee/latest/configuration/config-sections/

Note that the following page might be better as much more detailed: https://docs.haproxy.org/2.6/configuration.html

## Resources

All resources are listed in `haproxy_resources` list variable. Their `type` key will determine how template manage them.

### Frontend

Frontend are listeners that transmit requests to backends.

User can add as many frontend as needed:

```yaml
haproxy_resources:
  - type: frontend
    name: fmg1
    bind:
      ip4: 10.10.0.79
      port: 80
    default_backend: fmg1b
  - type: frontend
    name: ftest
    bind:
      ip4: 10.10.0.10
      port: 8080
    parameters: |
      mode tcp
    default_backend: btest
```

When needed, the `parameters` key (multi lines string variable) can be added to override defaults settings.
Remember to also define each backend set here as default backend.

### Backend

Backends are lists of servers where to forward requests to.

User can define as many backend as needed, bellow frontends in `haproxy_resources` list.

```yaml
haproxy_resources:
  - type: backend
    name: fmg1b
    parameters:
    servers:
      - hostname: mg1
        ip4: 10.10.0.1
        port: 80
        parameters: check
      - hostname: mg2
        ip4: 10.10.0.2
        port: 80
        parameters: check backup weight 100
      - hostname: mg3
        ip4: 10.10.0.3
        port: 80
        parameters: check backup weight 200
```

When needed, the global backend `parameters` key (multi lines string variable) can be added to override defaults settings. Also, for each server, a `parameters` key (single line string variable) can be added to define more detailed servers configurations.

### http_simple

This resource is a simplified resource to generates a combined frontend/backend in one shot.

```
 http server1                 http server2
 10.10.0.1:80                 10.10.0.2:80
      ▲         round robin        ▲
      └──────────────┬─────────────┘
                     │
             dedicated server0
                  haproxy
                10.10.0.7:80
                     ▲
                     │
                     │
                     │
                http request
```

For example:

```yaml
haproxy_resources:
  - type: http_simple
    name: cluster1
    bind:
      ip4: 10.10.0.7
      port: 80
    servers:
      - hostname: mg1
        ip4: 10.10.0.1
        port: 80
      - hostname: mg2
        ip4: 10.10.0.2
        port: 80
```

A **roundrobin** balance mechanism is by default enabled when using this `http_simple` resource.

### http_load_balancer

`http_load_balancer` resource uses local haproxy to use 301 redirection to clients based on a roundrobin balance mechanism. While default haproxy configuration uses haproxy server as proxy and so act as a bandwidth limitation, http load balancer only send to client 301 answers, allowing clients to directly reach target http servers. This has great benefits when multiple clients requests a lot of huge files at the same time (diskless, packages, etc.).

Step 1: client request a file at http://10.10.0.7:80/myfile

```
             dedicated server0
                  haproxy
                10.10.0.7:80
                     ▲
                     │
                     │
                     │
                http request
```

Step 2: haproxy proxy this request to localhost:8081 frontend, that is configured to be a 301 redirection on 10.10.0.1:80, and so haproxy answers : http 301, redirect to http://10.10.0.1:80/myfile


```
 http 301 to server1          http 301 to server2          http 301 to server3
 localhost:8081               localhost:8082               localhost:8083
      ▲         round robin        ▲                            ▲
      └──────────────┬─────────────┴────────────────────────────┘
                     │
             dedicated server0
                  haproxy
                10.10.0.7:80
                     ▲
                     │
                     │
                     │
                http request
```

Step 3: client directly connect to server1 at http://10.10.0.1:80/myfile and download the file from this server, without using bandwidth of the haproxy load balancer. If same client request the same file at 10.10.0.7:80 again, it will be redirected this time to server2, so 10.10.0.2:80, etc (round robin).

Configuration is similar to `http_simple`, with few additional keys to be set:

```yaml
haproxy_resources:
  - type: http_load_balancer
    name: cluster2
    bind:
      ip4: 10.10.0.78
      port: 80
    local_ports_first: 8081
    servers:
      - hostname: mg1
        ip4: 10.10.0.1
        port: 80
      - hostname: mg2
        ip4: 10.10.0.2
        port: 80
      - hostname: mg3
        ip4: 10.10.0.3
        port: 80
```

`local_ports_first` defines the ports ranges to be locally used as redirection frontends. In this example, local port used would be 8081, 8082 and 8083. Note that these ports do not need to be open in the firewall, as the usage is strictly internal to haproxy.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.1.0: Rewrite role to allow more simple and advanced usages. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Add TCP mode. Alexandra Darrieutort <alexandra.darrieutort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
