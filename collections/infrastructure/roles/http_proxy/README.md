# HTTP PROXY

![Squid Logo](squid_logo.png)

## Description

These settings provide a standard and simple http proxy based on Squid.
Squid is also able to act as a cache proxy.

This is useful in many cases. For example:

* Use external repositories for cluster hosts, as the cache mechanism allows to only download once packages to the main repo.
* Filter access to web for the cluster (allow for example pulls to dockerhub, but not from another registry, etc).
* Act as an intermediate between a central http server and clients to distribute load.
* Etc.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

### Proxy port

By default, Squid proxy will listen on port 3128. It is possible to change that (for example 8080) by setting the `http_proxy_port` key:

```yaml
http_proxy_port: 8080
```

### Networks

By default, all networks defined in `networks` dict will be added as allowed networks to use the proxy.
It is possible to prevent a network to be allowed (and so added into Squid configuration) by using the `http_proxy_server` key.
Setting this key to false will prevent network to be allowed to use the proxy (networks without `subnet` are ignored):

```yaml
networks:
  net-admin:     # << this network will be allowed to use the proxy
    subnet: 10.10.0.0
    prefix: 16
  ib0:           # << this network will NOT be allowed to use the proxy
    subnet: 10.20.0.0
    prefix: 16
    http_proxy_server: false
```

You can also add custom local networks to be allowed to use the proxy by setting them in the `http_proxy_allowed_networks` list:

```yaml
http_proxy_allowed_networks:
  - 192.168.0.0/16
```

### Allowed destination ports

By default, these settings will allow the following ports to transit through the proxy:

```
acl Safe_ports port 80		# http
acl Safe_ports port 21		# ftp
acl Safe_ports port 443		# https
acl Safe_ports port 70		# gopher
acl Safe_ports port 210		# wais
acl Safe_ports port 1025-65535	# unregistered ports
acl Safe_ports port 280		# http-mgmt
acl Safe_ports port 488		# gss-http
acl Safe_ports port 591		# filemaker
acl Safe_ports port 777		# multiling http
```

It is possible to disable that default by setting `http_proxy_default_allowed_ports` to `false`.

It is also possible to define custom ports to be allowed (in replacement of default ports or in addition to them) by setting the `http_proxy_allowed_ports` list:

```yaml
http_proxy_allowed_ports:
  - 80
  - 443
  - 8080
```

If `http_proxy_default_allowed_ports` is `false`, at least one port must be set in `http_proxy_allowed_ports`, else the role fails.

### Allowed tunnel ports

HTTPS requests, and any other tunnel (SSH, etc.), go through the proxy with the `CONNECT` method. By default,
tunnels are only allowed to port 443. Other ports can be allowed by setting the `http_proxy_ssl_ports` list
(ports must also be allowed above):

```yaml
http_proxy_ssl_ports:
  - 443
  - 8443  # a container registry
  - 22    # SSH
```

### Cache

By default, cache is disabled. To enable cache, set `http_proxy_cache_enable` key to `true`.

Once set to true, you can define the following parameters for cache (values given here are defaults):

```yaml
http_proxy_cache_storage_format: ufs
http_proxy_cache_storage_path: /var/spool/squid
http_proxy_cache_storage_size: 100 # MB
http_proxy_cache_storage_l1: 16
http_proxy_cache_storage_l2: 256
```

For more details on these parameters, please refer to http://www.squid-cache.org/Doc/config/cache_dir/

### Refresh patterns

You can set custom refresh patterns using the `http_proxy_refresh_patterns` list:

```yaml
http_proxy_refresh_patterns:
  - 'Packages\.bz2$    0       20%     4320 refresh-ims'
```

For more details on refresh patterns, please refer to http://www.squid-cache.org/Doc/config/refresh_pattern/

### Coredump

You can set CoreDump directory path by setting `http_proxy_coredump_dir`. Default is `/var/spool/squid`.

### Raw configuration

It is possible to add raw Squid configuration into final configuration file by setting the multi line string `http_proxy_raw_content`.

For example:

```yaml
http_proxy_raw_content: |
  # Logs are managed by logrotate
  logfile_rotate 0
```

The whole documentation is available at http://www.squid-cache.org/Doc/config/

The generated configuration is checked with `squid -k parse` before being installed: an invalid configuration
makes the role fail, and the running Squid is left untouched.

## Variables

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
