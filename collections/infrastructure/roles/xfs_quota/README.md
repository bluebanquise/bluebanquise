# XFS Quota

## Description

Used to set default user and group disk quotas on an XFS filesystem used by a server.

These settings provide simply an interface to **xfs_quota** Ansible module https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html

## Observation

For these settings to work, the filesystem mount configurations must have the options uquota, gquota, pquota.

Example:

```
/dev/xvdb1 /xfs xfs rw,quota,gquota,pquota 0 0
```

## Instructions

Define quotas in the `xfs_quota` list, one entry per user, group or project quota, with the parameters of the
`xfs_quota` module:

```yaml
xfs_quota:
  - type: user
    name: nobody 
    mountpoint: /exports/nfs
    bsoft: 5G
    bhard: 6G
  - type: group
    name: nobody
    mountpoint: /exports/nfs
    bsoft: 5G
    bhard: 6G
```

See the [xfs_quota module](https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html) for the full list of available parameters.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `xfs_quota` | not set | Quotas to set (`type`, `mountpoint`, `name`, `bsoft`, `bhard`, `isoft`, `ihard`, `rtbsoft`, `rtbhard`, `state`). |
