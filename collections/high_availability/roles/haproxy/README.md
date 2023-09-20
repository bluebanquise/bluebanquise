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
      - name: mg1
        ip4: 10.10.0.1
        port: 80
        parameters: check
      - name: mg2
        ip4: 10.10.0.2
        port: 80
        parameters: check backup weight 100
      - name: mg3
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
      - name: mg1
        ip4: 10.10.0.1
        port: 80
      - name: mg2
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
      - name: mg1
        ip4: 10.10.0.1
        port: 80
      - name: mg2
        ip4: 10.10.0.2
        port: 80
      - name: mg3
        ip4: 10.10.0.3
        port: 80
```

`local_ports_first` defines the ports ranges to be locally used as redirection frontends. In this example, local port used would be 8081, 8082 and 8083. Note that these ports do not need to be open in the firewall, as the usage is strictly internal to haproxy.


<!--
## Deal with local http 80 port on non dedicated nodes

When using haproxy directly on a target http server, there could be conflicts between ports.
 
There are multiple scenario possible

* Do you have a separated haproxy physical server, or is haproxy running on the http servers themselfs?
* Do you need everything to be on 80/443 port, or are you able to change ports?
* Etc.

Depending on all these questions, final configuration will be different.

The following architectures will be describe here:

* haproxy with a dedicated server
* haproxy without a dedicated server but with ports changes
* haproxy without a dedicated server and without ports changes
* haproxy combined with keepalived

Note that the role provides defaults for each level of parameters.
See advanced usage for more details.

### Prepare web servers for testing

Simply create a file called `hatest.html` with
web server hostname as content inside, on each webserver.

For example, on `server1`, do:

```
echo $(hostname) > /var/www/html/hatest.html
```

And the same on `server2`. Adapt path depending of your Linux distribution.

This will allow you to test haproxy configuration.

### haproxy with a dedicated server

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

This is the simplest case. We simply need to ensure haproxy bind to 
10.10.0.7:80 on server0, and dispatch requests on server1 and server2.
We assume that client have access to all servers on the network as haproxy will 
simply send redirect instructions.

Deploy haproxy role on server0 with the following parameters:

```yaml
haproxy_mode: http

haproxy_resources:
  - name: myhttp
    frontend:
      ip4: 10.10.0.7
      port: 80
    backend:
      servers:
        - hostname: server1
          ip4: 10.10.0.1
          port: 80
        - hostname: server2
          ip4: 10.10.0.2
          port: 80
```

Test it works as expected:

```
curl http://10.10.0.7/hatest.html
```

This command should answer `server1` or `server2` in a round robin manner
if you execute it multiple time.

### haproxy without a dedicated server but with ports changes

```
                              http server2
                              10.10.0.2:80
                round robin        ▲
      ┌──────────────┬─────────────┘
      ▼              │
10.10.0.1:80  nodedicated server1
                  haproxy
                10.10.0.7:8080
                     ▲
                     │
                     │
                     │
                http request
```

In this configuration, since http server by default listen on all 
interfaces, we need to use another port for haproxy to avoid conflicts.

We need to ensure haproxy bind to 
10.10.0.7:8080 on server0, and dispatch requests on server1 and server2.
We assume that client have access to all servers on the network as haproxy will 
simply send redirect instructions.

Deploy haproxy role on server1 with the following parameters:

```yaml
haproxy_mode: http

haproxy_resources:
  - name: myhttp
    frontend:
      ip4: 10.10.0.7
      port: 8080
    backend:
      servers:
        - hostname: server1
          ip4: 10.10.0.1
          port: 80
        - hostname: server2
          ip4: 10.10.0.2
          port: 80
```

Test it works as expected:

```
curl http://10.10.0.7:8080/hatest.html
```

This command should answer `server1` or `server2` in a round robin manner
if you execute it multiple time.

### haproxy without a dedicated server and without ports changes

```
                              http server2
                              10.10.0.2:80
                round robin        ▲
      ┌──────────────┬─────────────┘
      ▼              │
10.10.0.1:80  nodedicated server1
                  haproxy
                10.10.0.7:80
                     ▲
                     │
                     │
                     │
                http request
```

For some legacy applications, it is not possible to change http port to be used.

If you also need to host haproxy on one of the http servers, only solution then is to
prevent http server (assuming apache here) to listen on ip used by haproxy, and so restrict it to 
some dedicated ip.

This role can configure apache to only listen on a set of ip.

To do so, simply set the following variable, that should match the host running haproxy.

```yaml
haproxy_apache_restrict_to_ip4:
  - 10.10.0.1
```

If you are using something else than basic 80 http port, add it after ip:

```yaml
haproxy_apache_restrict_to_ip4:
  - 10.10.0.1:8888
  - 10.10.0.1:443
```

This way, once role is deployed, apache will only bind on 10.10.0.1 ip and let haproxy
open port 80 on 10.10.0.7.

Then deploy haproxy role on server1 with the following parameters:

```yaml
haproxy_mode: http

haproxy_resources:
  - name: myhttp
    frontend:
      ip4: 10.10.0.7
      port: 80
    backend:
      servers:
        - hostname: server1
          ip4: 10.10.0.1
          port: 80
        - hostname: server2
          ip4: 10.10.0.2
          port: 80
```

Test it works as expected:

```
curl http://10.10.0.7/hatest.html
```

This command should answer `server1` or `server2` in a round robin manner
if you execute it multiple time.

### haproxy combined with keepalived

```
 http server1   round robin    http server2
 10.10.0.1:80 ◄──────┬───────► 10.10.0.2:80
                     │
   haproxy ─ ─ ─ ─ ─ ┴────────  haproxy
 10.10.0.7:80                 10.10.0.7:80 (floating)
      ▲                            ▲
      └─ ─ ─ ─ ─ ─ ─ ┬─────────────┘
                     │
                     │
                     │
                http request
```

In this configuration, haproxy is running on both servers, and
keepalived is in charge of moving a floating ip between both servers
to ensure high availability.

This configuration has the advantage of ensuring robust and simple solution.

To deploy this configuration, set `haproxy_apache_restrict_to_ip4` for both 
server1 and server2, but with different values, which means you will have to set 
this variable under each hosts Ansible hostvars.

In the ansible inventory, if not exist, create a folder called `host_vars`.
Create then inside this folder 2 folders, called `server1` and `server2`.

No, inside `host_vars/server1/haproxy.yml` file, add the following content:

```yaml
haproxy_apache_restrict_to_ip4:
  - 10.10.0.1
```

And inside `host_vars/server2/haproxy.yml` file, add the following content:

```yaml
haproxy_apache_restrict_to_ip4:
  - 10.10.0.2
```

Now, configure role with the following parameters:

```yaml
haproxy_mode: http

haproxy_resources:
  - name: myhttp
    frontend:
      ip4: 10.10.0.7
      port: 80
    backend:
      servers:
        - hostname: server1
          ip4: 10.10.0.1
          port: 80
        - hostname: server2
          ip4: 10.10.0.2
          port: 80
```

And deploy role on both server1 and server2 systems.

Once keepalived has been deployed and 10.10.0.7 ip is up (please refer to keepalived role documentation)
you can start requesting haproxies:

Test it works as expected:

```
curl http://10.10.0.7/hatest.html
```

This command should answer `server1` or `server2` in a round robin manner
if you execute it multiple time.

### Advanced usage -->


## Changelog

* 1.1.0: Rewrite role to allow more advanced usages. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Add TCP mode. Alexandra Darrieutort <alexandra.darrieutort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
