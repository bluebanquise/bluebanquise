# haproxy

>>>>>>>>>>>>> BEN https://www.cyberciti.biz/faq/linux-bind-ip-that-doesnt-exist-with-net-ipv4-ip_nonlocal_bind/


## Description

This role deploy a basic haproxy configuration to be used 
in high availability context.

Example usage is to spread load on repositories and diskless images.

For details on how haproxy operate, please read https://www.digitalocean.com/community/tutorials/an-introduction-to-haproxy-and-load-balancing-concepts

## Instructions

There are multiple scenario possible:

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

### Advanced usage


## Changelog

* 1.0.1: Add TCP mode. Alexandra Darrieutort <alexandra.darrieutort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
