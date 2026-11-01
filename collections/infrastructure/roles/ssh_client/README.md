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

This role generates the ssh client configuration file of the user running Ansible (`~/.ssh/config` of the sudo user
when using `become`, or root).

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

By default, the file only contains settings explicitly set (see below). To make ssh reach hosts through a given
network, whatever the resolution of their hostname, set `ssh_client_global_network` (or `ssh_client_network` at host
level) to this network name:

```yaml
ssh_client_global_network: net-admin
```

Hosts then get:

```
Host c001
    Hostname %h-net-admin
```

ssh then connects to `c001-net-admin`, the name of the host on this network, provided by the **hosts_file** and
**dns_server** roles. This can be seen when invoking ssh with verbosity (`ssh c001 -vvv`).

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

It is possible to set specific parameters at global and/or hosts level:

| Global variable (all hosts) | Host variable | ssh option |
|-----------------------------|---------------|------------|
| `ssh_client_global_network` | `ssh_client_network` | `Hostname %h-<network>` |
| `ssh_client_global_stricthostkeychecking` | `ssh_client_stricthostkeychecking` | `StrictHostKeyChecking` |
| `ssh_client_global_userknownhostsfile` | `ssh_client_userknownhostsfile` | `UserKnownHostsFile` |
| `ssh_client_global_loglevel` | `ssh_client_loglevel` | `LogLevel` |
| `ssh_client_global_verifyhostkeydns` | `ssh_client_verifyhostkeydns` | `VerifyHostKeyDNS` |
| `ssh_client_global_forwardx11trusted` | `ssh_client_forwardx11trusted` | `ForwardX11Trusted` |
| | `ssh_client_user` | `User` |

Hosts settings are written before global ones (`Host *`), so that they take precedence: ssh uses the first value
found for each option.

For example, to disable host key checking for a specific host, set at host level:

```yaml
ssh_client_loglevel: QUIET
ssh_client_stricthostkeychecking: "no"
ssh_client_userknownhostsfile: /dev/null
```

Raw content can be added at the top of the file with `ssh_client_custom_config`.

The `UseRoaming` option is not supported anymore: it was removed from OpenSSH 7.2, and makes ssh fail with
`Bad configuration option`.

In case of issue, try adding verbosity to the ssh invocation to investigate (-vvv).

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssh_client_global_*` | not set | Global parameters, see above. |
| `ssh_client_custom_config` | not set | Raw content added at the top of the file. |
| `ssh_client_restrict_to_group` | `bb_restrict_to_group`, else `all` | Group of hosts to write. |
