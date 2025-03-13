# HTTP PROXY

![Squid Logo](squid_logo.png)

## Description

This role provides a standard and simple http proxy based on Squid.
Squid is also able to act as a cache proxy.

This is useful in many cases. For example:

* Use external repositories for cluster nodes, as the cache mechanism allows to only download once packages to the main repo.
* Filter access to web for the cluster (allow for example pulls to dockerhub, but not from another registry, etc).
* Act as an intermediate between a central http server and clients to ditribute load.
* Etc.

This role needs at least RHEL (or equivalent) >= 9, Ubuntu >= 22.04, Debian >= 12 and OpenSuse Leap >= 15.5 due to requirements on Squid version.

## Instructions

### Proxy port

By default, Squid proxy will listen on port 3128. It is possible to change that (for example 8080) by setting the `http_proxy_port` key:

```yaml
http_proxy_port: 8080
```

### Networks

By default, all networks defined in `networks` dict will be added as allowed networks to use the proxy.
It is possible to prevent a network to be allowed (and so added into Squid configuration) by using the `http_proxy_server` key.
Setting this key to false will prevent network to be allowed to use the proxy:

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

### Allowed query ports

By default, the role will allow the following ports to transit through the proxy:

```
acl SSL_ports port 443
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

It is also possible to define custom ports to be allowed (in replacement of default port or in addition to them) by setting the `http_proxy_allowed_ports` list:

```yaml
http_proxy_allowed_ports:
  - 80
  - 443
  - 22
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
  - "Packages\.bz2$    0       20%     4320 refresh-ims"
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

## Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
