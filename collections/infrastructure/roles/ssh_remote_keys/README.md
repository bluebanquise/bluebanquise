# SSH remote keys

## Description

These settings add the inventory ssh public keys to the `authorized_keys` file of the user running Ansible on remote
hosts (the sudo user when using `become`, or root).

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Keys are provided as a list, usually in the `os_*` groups (same variable as the **pxe_stack** role uses to deploy hosts):

```yaml
os_admin_ssh_keys:
  - ssh-ed25519 AAAAC....
  - ssh-ed25519 AAAAB....
```

Keys are only added: keys already present in `authorized_keys` are kept.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `os_admin_ssh_keys` | not set | Public keys to authorize. |
| `ssh_remote_keys_os_admin_ssh_keys` | `[]` | Public keys to authorize when `os_admin_ssh_keys` is not set. |
