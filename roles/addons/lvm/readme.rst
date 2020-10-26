LVM
---

Description
^^^^^^^^^^^

This role configure local LVM stack: Physical Volumes, Volume Groups, and Logical Volumes.

Role assume standard LVM tree, with *vg* at center of it. For example:

.. code-block:: text

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

Instructions
^^^^^^^^^^^^

All options from lvg and lvol ansible modules are supported. See: 

* lvg: https://docs.ansible.com/ansible/latest/collections/community/general/lvg_module.html
* lvol: https://docs.ansible.com/ansible/latest/collections/community/general/lvol_module.html

To add LVM to an host, use the following YAML structure:

.. code-block:: yaml

      hosts:
        management1:
          network_interfaces:
            - interface: enp0s8
              ip4: 10.10.0.1/16,10.10.0.2/16
              mac: 08:00:27:36:c0:ac
              network: ice1-1
          storage:
            lvm:
              - vg: data
                pvs:
                  - /dev/sdb
                  - /dev/sdc
                lvs:
                  - lv: test
                    size: 200M
                  - lv: test2
                    size: 10G
              - vg: colors
                pvs:
                  - /dev/sde
                  - /dev/sdf
                lvs:
                  - lv: blue
                    size: 100M

At *vg* level, all options from module **lvg** are available.
At *lv* level, all options from module **lvol** are available.

.. note::
  Of course, options *vg* and *pvs* of module lvol are not available at *lv* level, 
  as they are implicitely set here in the yaml structure.

For example, you can create a mirrored logical volume using:

.. code-block:: yaml

          storage:
            lvm:
              - vg: data
                pvs:
                  - /dev/sdb
                  - /dev/sdc
                lvs:
                  - lv: test
                    size: 200M
                    opts: -m 1

Which will produce a 2 mirrir lv:

.. code-block:: text

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

Etc.

.. note::
  LVM mirroring recovering is documented in the story section of the main
  BlueBanquise documentation.

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* storage[item]
   * vg
   * pvs
   * lvs[item]
      * lv
      * size

Optional inventory vars:

**hostvars[inventory_hostname]**

* storage[item]
   * force
   * pesize
   * pv_options
   * pvresize
   * state
   * vg_options
   * lvs[item]
      * active
      * force
      * opts
      * resizefs
      * shrink
      * snapshot
      * state
      * thinpool

^^^^^^

Packages installed:

* lvm management tools package

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
