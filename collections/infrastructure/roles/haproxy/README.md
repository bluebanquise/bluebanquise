# haproxy

## Description

This role deploys a HAProxy configuration, to be used in a high availability context (usually with the
`keepalived` role providing virtual IPs), or as a load balancing mechanism.

Example usage is to spread load on packages repositories, diskless images, etc.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

For details on how HAProxy operates, please read [An introduction to HAProxy and load balancing concepts](https://www.digitalocean.com/community/tutorials/an-introduction-to-haproxy-and-load-balancing-concepts).

## Instructions

The role offers 2 sets of parameters and 4 resource types:

* Parameters:
  * global
  * defaults
* Resources:
  * frontend
  * backend
  * http_simple
  * http_load_balancer

This allows simple or advanced usage.

The generated configuration is checked with `haproxy -c` before being installed: an invalid configuration
makes the role fail, and the running HAProxy is left untouched. Configuration changes are applied with a
reload, without dropping established connections.

The bind port of each `frontend`, `http_simple` and `http_load_balancer` resource is opened in the firewall
(zone `haproxy_firewall_zone`, else `bb_services_firewall_zone`, else `public`). Ports used in
`haproxy_resources_raw` must be opened using the `firewall` role.

By default, the role allows binding on IP addresses not present on the host (`net.ipv4.ip_nonlocal_bind`),
so that HAProxy can listen on a virtual IP held by another host. Set `haproxy_enable_ip_nonlocal_bind: false`
to leave this kernel setting untouched.

## Parameters

### Global parameters

By default, the role uses the following global settings:

```
    log stdout format raw local0
    user haproxy
    group haproxy
    chroot /var/lib/haproxy
    stats socket /var/lib/haproxy/stats user haproxy group haproxy mode 660 level admin
    nbthread 4
    maxconn 50000
```

Logs are sent to the systemd journal (`journalctl -u haproxy`).

To use different settings, set `haproxy_global_parameters` as a multi lines string, to **fully replace** these settings. The template indents the content as needed.

For example, if a very minimal configuration is preferred:

```yaml
haproxy_global_parameters: |
  log stdout format raw local0
  user haproxy
  group haproxy
```

Please refer to the [official documentation](https://docs.haproxy.org/2.8/configuration.html) for available settings.

### Defaults parameters

By default, the role uses the following defaults settings:

```
    timeout connect 10s
    timeout client 30s
    timeout server 30s
    log global
    mode http
    option httplog
    maxconn 5000
```

To use different settings, set `haproxy_defaults_parameters` as a multi lines string, to **fully replace** these settings. The template indents the content as needed.

For example:

```yaml
haproxy_defaults_parameters: |
  timeout connect 20s
  mode tcp
  maxconn 100
```

## Resources

All resources are listed in the `haproxy_resources` list. Their `type` key determines how the template manages them.

### Frontend

Frontends are listeners that transmit requests to backends.

User can add as many frontends as needed:

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

When needed, the `parameters` key (multi lines string) can be added to override defaults settings.
Remember to also define each backend set here as default backend. If `ip4` is not set, the frontend listens on all addresses.

### Backend

Backends are lists of servers where requests are forwarded to.

User can define as many backends as needed in the `haproxy_resources` list.

```yaml
haproxy_resources:
  - type: backend
    name: fmg1b
    servers:
      - hostname: mg1
        ip4: 10.10.0.1
        port: 80
      - hostname: mg2
        ip4: 10.10.0.2
        port: 80
        parameters: check backup weight 100
      - hostname: mg3
        ip4: 10.10.0.3
        port: 80
        parameters: check backup weight 200
```

When needed, the backend `parameters` key (multi lines string) can be added to override defaults settings.
Also, for each server, a `parameters` key (single line string) can be added to define more detailed server
configuration. It defaults to `check` (health check enabled).

### http_simple

This resource generates a combined frontend/backend in one shot. HAProxy proxies requests to servers.

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

A **roundrobin** balance mechanism is used, and servers are health checked.

### http_load_balancer

With `http_simple`, all data goes through HAProxy, which can become a bandwidth bottleneck. With
`http_load_balancer`, HAProxy only answers to clients with an HTTP 302 redirection to one of the servers,
in round robin, and clients then download directly from this server. This has great benefits when multiple
clients request a lot of huge files at the same time (diskless images, packages, etc.).

Step 1: client requests a file at `http://10.10.0.7:80/myfile`.

Step 2: HAProxy answers with a redirection to the next available server: HTTP 302, location `http://10.10.0.1:80/myfile`.

```
 http server1                 http server2                 http server3
 10.10.0.1:80                 10.10.0.2:80                 10.10.0.3:80
      ▲         round robin        ▲                            ▲
      └──────────────┬─────────────┴────────────────────────────┘
                     │ 302 redirection
             dedicated server0
                  haproxy
                10.10.0.7:80
                     ▲
                     │
                http request
```

Step 3: client directly connects to server1 at `http://10.10.0.1:80/myfile` and downloads the file from this
server, without using bandwidth of the HAProxy host. If the same client requests the same file at
`10.10.0.7:80` again, it is redirected this time to server2, etc. (round robin).

Servers are health checked: a server not answering is not used anymore, until it comes back. The path and
query string of the request are kept in the redirection. Only `GET` and `HEAD` requests are redirected,
other requests are proxied.

Configuration is the same as `http_simple`:

```yaml
haproxy_resources:
  - type: http_load_balancer
    name: cluster2
    bind:
      ip4: 10.10.0.78
      port: 80
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

Server `port` is optional (default is the frontend port).

Note: previous versions of this role used local redirection frontends, configured by `local_ports_first`.
This key is now ignored, and can be removed.

### Raw resources

Any additional configuration (`listen` sections, etc.) can be added as is, as a multi lines string, after
global and defaults sections:

```yaml
haproxy_resources_raw: |
  listen stats
      bind :8404
      stats enable
      stats uri /stats
```

## Variables

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
