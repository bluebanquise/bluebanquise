# Changelog

## 1.3.0

### Breaking changes:

* Introduce new network_interfaces format.

Current:

```
          network_interfaces:
            enp0s3:
              ip4: 10.10.0.1
              mac: 08:00:27:dc:f8:f5
              network: ice1-1
            ib0:
              ip4: 10.20.0.1
              network: interconnect-1
```

Become:

```
          network_interfaces:
            - interface: enp0s3
              ip4: 10.10.0.1
              mac: 08:00:27:dc:f8:f5
              network: ice1-1
            - interface: ib0
              ip4: 10.20.0.1
              network: interconnect-1
```

With the following rules:

1. First item in the list is the hosts main resolution network (here, c001 for example will be on the same line than c001-ice1-1 in the hosts file).
2. First management network related item in the list will be the ansible mains ssh target interface (from ssh_master role), and also the main management network interface for the client (services_ip to target on client side).

If I wish direct resolution to be on interconnect-1 here, I simply move it first in the list. Ansible ssh will still use ice1-1 network, but ping c001 will be through interconnect-1.
