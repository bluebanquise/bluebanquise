# mariadb

## Description

This role installs MariaDB server and performs a minimal secure installation: sets the root password, removes anonymous users, and drops the test database.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Requirements

The `ansible.mysql` Ansible collection must be installed:

```
ansible-galaxy collection install ansible.mysql
```

## Instructions

Set `mariadb_root_password` in your inventory (use Ansible Vault to encrypt it). It is mandatory: the role
fails if it is empty, as an empty password would allow any local user to connect as root.

```yaml
mariadb_root_password: "mysecretpassword"
```

The role connects to MariaDB as root through the Unix socket. On first deployment, root has no password and
is authenticated as the system root user (`unix_socket` authentication). Once the password is set, the role
uses it on next runs. After the first run, root must use its password, even from the system root account.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `mariadb_root_password` | `""` | Root password to set, mandatory (use Ansible Vault). |
| `mariadb_enable_services` | `bb_enable_services`, else `true` | Enable mariadb service. |
| `mariadb_start_services` | `bb_start_services`, else `true` | Start mariadb service. |

Packages (`mariadb-server`, or `mariadb` on Suse, and the PyMySQL Python module used by Ansible) and the Unix
socket path are set per distribution in the role `vars/`.
