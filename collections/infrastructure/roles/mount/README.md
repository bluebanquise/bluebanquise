# mount

## Description

These settings provide an interface to the [mount Ansible module](https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html) for managing mount points.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

Set needed mount points using the `mount` list in your inventory:

```yaml
mount:
  # Mount DVD read-only
  - path: /mnt/dvd
    src: /dev/sr0
    fstype: iso9660
    opts: ro,noauto
    state: present
  # Mount up device by label
  - path: /srv/disk
    src: LABEL=SOME_LABEL
    fstype: ext4
    state: present
  # Mount and bind a volume
  - path: /system/new_volume/boot
    src: /boot
    opts: bind
    state: mounted
    fstype: none
  # Mount an NFS volume
  - src: 192.168.1.100:/nfs/ssd/shared_data
    path: /mnt/shared_data
    opts: rw,sync,hard,intr
    state: mounted
    fstype: nfs
```

See the [mount module documentation](https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html) for the full list of available parameters.
