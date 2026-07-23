# mariadb

## Description

These settings install MariaDB server and performs a minimal secure installation: sets the root password, removes anonymous users, and drops the test database.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Requirements

The `ansible.mysql` Ansible collection must be installed:

```
ansible-galaxy collection install ansible.mysql
```

## Instructions

Set `mariadb_root_password` in your inventory (use Ansible Vault to encrypt it):

```yaml
mariadb_root_password: "mysecretpassword"
```

These settings connect to MariaDB via Unix socket for initial setup, so no password is required on first deployment.

## Variables

| Variable                | Default        | Description                              |
|:------------------------|:---------------|:-----------------------------------------|
| mariadb_root_password   | ""             | Root password to set (use Ansible Vault) |
| mariadb_packages        | see vars/      | Packages to install (OS-specific)        |
| mariadb_enable_services | bb_enable_services | Whether to enable the mariadb service |
| mariadb_start_services  | bb_start_services  | Whether to start the mariadb service  |

## Output

Packages installed:

* mariadb-server (or mariadb on Suse)
* python3-pymysql (required by ansible.mysql modules)
