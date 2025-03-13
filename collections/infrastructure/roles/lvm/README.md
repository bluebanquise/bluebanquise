# LVM

## Description

This role configure local LVM storage: Physical Volumes, Volume Groups, and Logical Volumes.

Role assume standard LVM tree. For example:

```
  +---------+
  |   pv1   +-----+
  +---------+     |                         +---------+
                  |                    +--->+   lv1   |
                  |                    |    +---------+
  +---------+     |    +---------+     |
  |   pv2   +--------->+   vg1   +-----+
  +---------+     |    +---------+     |
                  |                    |    +---------+
                  |                    +--->+   lv2   |
  +---------+     |                         +---------+
  |   pv3   +-----+
  +---------+
```

## Instructions

All options from lvg and lvol ansible modules are supported. See:

* lvg: https://docs.ansible.com/ansible/latest/collections/community/general/lvg_module.html
* lvol: https://docs.ansible.com/ansible/latest/collections/community/general/lvol_module.html

To configure LVM on an host, use the following YAML structure:

```yaml
hosts:
  management1:
    network_interfaces:
      - interface: enp0s8
        ip4: 10.10.0.1
        mac: 08:00:27:36:c0:ac
        network: ice1-1
    lvm:
      vgs:
        - vg: data
          pvs:
            - /dev/sdb
            - /dev/sdc
        - vg: colors
          pvs:
            - /dev/sde
            - /dev/sdf
      lvs:
        - lv: test
          size: 200M
          vg: data
        - lv: test2
          size: 10G
          vg: data
        - lv: blue
          size: 100M
          vg: colors
```

At *vgs* level, all options from module **lvg** are available.
At *lvs* level, all options from module **lvol** are available.

For example, you can create a mirrored logical volume using:

```yaml
storage:
  lvm:
    vgs:
      - vg: data
        pvs:
          - /dev/sdb
          - /dev/sdc
    lvs:
      - lv: test
        size: 200M
        vg: data
        opts: -m 1
```

Which will produce a 2 mirror lv:

```
  root]# lvdisplay
  --- Logical volume ---
  LV Path                /dev/data/test
  LV Name                test
  VG Name                data
  LV UUID                Vqswy7-3Efo-VQcL-8pp7-fe7J-Okj8-leL0ZZ
  LV Write Access        read/write
  LV Creation host, time management1
  LV Status              available
  # open                 0
  LV Size                200.00 MiB
  Current LE             50
  Mirrored volumes       2
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     8192
  Block device           253:4
```

Etc.

## Changelog

* 1.1.1: Fix missing list. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
