# SSH remote key

## Description

These settings configure the ssh client authorized public keys.
## Instructions

These settings will ensure remote hosts have the currently defined ssh authorized public keys in their `/root/.ssh/authorized_keys` file
(or sudo user home if not using root user).

Keys are provided as a list:

```
os_admin_ssh_keys:
  - ssh-ed25519 AAAAC....
  - ssh-ed25519 AAAAB....
```

/root/.ssh/authorized_keys contains ssh public keys from inventory
