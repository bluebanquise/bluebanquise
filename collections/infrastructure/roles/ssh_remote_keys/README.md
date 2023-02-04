# SSH remote key

## Description

This role configure the ssh client authorized public key.

## Instructions

This role will ensure remote hosts is having currently defined ssh authorized public keys in their `/root/.ssh/authorized_keys` file
(or sudo user home if not using root user).

Keys are provided as a list:

```
ep_admin_ssh_keys:
  - ssh-ed25519 AAAAC....
  - ssh-ed25519 AAAAB....
```

/root/.ssh/authorized_keys contains ssh public keys from inventory

## Changelog

* 1.1.1: Allow keys to sudo user folder. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Rename role. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
