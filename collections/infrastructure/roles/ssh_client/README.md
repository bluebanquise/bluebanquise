# ssh client

## Description

This role configures the ssh access of inventory known hosts to ensure ssh
access through nodes main network.

## Instructions

Note that this file generation is kind of "sensible", and will surely be the
first one to break in case of incoherent inventory. If this happens, check your
inventory, fix it, if needed remove manually /root/.ssh/config and relaunch its
generation.

## Basic usage

This role will generate a configuration file in */root/.ssh/config*.

This file will contains all hosts of the Ansible inventory (or all hosts of the
current iceberg if using icebergs mode), with the following parameters:

```
Host freya
    Hostname %h-ice1-1
```

And possibly add more parameters if asked for:

* StrictHostKeyChecking
* UserKnownHostsFile
* LogLevel

See advanced usage for these parameters.

Note that for this example host, **freya**, the target hostname for ssh is
%h-ice1-1, which translates to **freya-ice1-1**. This can be seen when invoking
ssh with verbosity:

```
  [root@odin ]# ssh freya -vvv
  OpenSSH_7.8p1, OpenSSL 1.1.1 FIPS  11 Sep 2018
  debug1: Reading configuration data /root/.ssh/config
  debug1: /root/.ssh/config line 10: Applying options for freya
  debug1: Reading configuration data /etc/ssh/ssh_config
  debug3: /etc/ssh/ssh_config line 52: Including file /etc/ssh/ssh_config.d/05-redhat.conf depth 0
  debug1: Reading configuration data /etc/ssh/ssh_config.d/05-redhat.conf
  debug3: /etc/ssh/ssh_config.d/05-redhat.conf line 2: Including file /etc/crypto-policies/back-ends/openssh.config depth 1
  debug1: Reading configuration data /etc/crypto-policies/back-ends/openssh.config
  debug3: gss kex names ok: [gss-gex-sha1-,gss-group14-sha1-]
  debug3: kex names ok: [curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1]
  debug1: /etc/ssh/ssh_config.d/05-redhat.conf line 8: Applying options for *
  debug2: resolving "freya-ice1-1" port 22
  debug2: ssh_connect_direct
  debug1: Connecting to freya-ice1-1 [10.11.2.1] port 22.
```

You can see here ssh is not trying to reach **freya** but is using
**freya-ice-1-1**. This has been made to ensure whatever the direct resolution
is in /etc/hosts or DNS, ssh and so Ansible will always use the management
network of the target host.

Also, keep in mind that when redeploying an host, its SSH key changes, which
requires to remove the former host key from the known_hosts file, then add the
new key. It is possible to achieve this with the commands below:

```
# for host in $(nodeset -e $NODES); do \
    sed -i -e "/^${host}/d" /root/.ssh/known_hosts; \
done
# clush -o '-o StrictHostKeyChecking=no' -w $NODES dmidecode -s system-uuid
```

## Advanced usage

It is possible to set specific parameters at global and/or nodes level:

* StrictHostKeyChecking
* UserKnownHostsFile
* LogLevel
* UseRoaming
* ForwardX11Trusted
* StrictHostKeyChecking

To achieve that, the following variables are available:

* ssh_client_global_loglevel
* ssh_client_global_stricthostkeychecking
* ssh_client_global_userknownhostsfile
* ssh_client_global_network
* ssh_client_global_verifyhostkeydns
* ssh_client_global_forwardx11trusted
* ssh_client_global_useroaming

Which are evaluated at global level

For example, ssh_client_global_network can be used to configure in */root/ssh/config*
the same network for all hosts.

And:

* ssh_client_loglevel
* ssh_client_stricthostkeychecking
* ssh_client_userknownhostsfile
* ssh_client_verifyhostkeydns
* ssh_client_forwardx11trusted
* ssh_client_useroaming

Which are evaluated for each host.

For example, to disable host key checking for a specific host, set:

```
ssh_client_loglevel: QUIET
ssh_client_stricthostkeychecking: no
ssh_client_userknownhostsfile: /dev/null
```

At host hostvars level.

In case of issue, try adding verbosity to the ssh invocation to investigate (-vvv).

## Changelog

* 1.4.0: Add extra config options. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.3.0: Role simplification. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.3: infrastructure/ssh_client role: set a default network <jean-pascal.mazzilli@gmail.com>
* 1.2.2: Fixed ssh_client_userknownhostsfile host_vars. Leo Magdanello <lmagdanello40@gmail.com>
* 1.2.1: Fixed sudo user home directory. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.1: Fix issue with empty network interfaces. johnnykeats <johnny.keats@outlook.com>
* 1.1.0: Add more granularity to host key checking, improve role's performances. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.7: Rename role. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Prevent unsorted ranges. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Add custom config variable. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.4: Add ssh ProxyJump capability for icebergs. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
