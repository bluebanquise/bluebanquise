# ClusterShel

## Description

This role optionally installs clustershell and setup groups for clustershell (based on Ansible inventory groups provided).
It can be used in combinaison with other BlueBanquise stack tools, like `bluebanquise-bootset`.

## Instructions

By default, role will not install Clustershell, since Clustershell is already a base
requirement for the BlueBanquise stack. However, if for any reasons you wish the role to install it,
set either variables `clustershell_install_from_pip` or `clustershell_install_from_package` to true.

`clustershell_install_from_pip` will uses pip to install Clustershell, while `clustershell_install_from_package`
will rely on system native packages manager to install it.

Once role has been deployed, check groups using:

```
nodeset -LL
```

## Custom nodeset Map

By default, the role generates ClusterShell groups based on the Ansible inventory.

However, you can generate custom groups with other names and also clusters (see man 5 groups.conf) using the role.

If you want to customize, you must configure as below:

1. Change the ``clustershell_custom_map`` variable to true inside the ``defaults`` folder.
2. Create an inventory called ``clush.yml`` inside ``inventory/group_vars/all/addons`` with the following structure:

```yaml
---
clush:
  all:
    all:
     - '@adm'
     - '@io'
     - '@computes'
  adm:
    mngt:
      - mngt0-1
      - mngt0-2
  io:
    oss:
      - oss[1-2]
    mds:
      - mds[1-2]
  computes:
    cpu:
      - cpu[1-10]
    gpu:
      - gpu[1-10]
```

**Comments:**

The first keys (which in the example are *all, adm, io and computes*) will be used to generate the name of the groups in ***local.cfg*** and the name of the roles in ***cluster.yaml***:

The second keys (which in the example are *mngt, oss, mds, cpu, gpu*) will be used to generate the name of the groups inside the ***cluster.yaml***.

You can use groups from the file itself. See below how we used the *adm*, *io* and *computes* keys to generate the group.

The above configuration would generate the following nodeset:

```shell
@adm mngt0-[1-2]
@all cpu[1-10],gpu[1-10],mds[1-2],mngt0-[1-2],oss[1-2]
@computes cpu[1-10],gpu[1-10]
@io mds[1-2],oss[1-2]
@all:all cpu[1-10],gpu,mds,mngt0-[1-2],oss[1-2]
@adm:mngt mngt0-[1-2]
@io:mds mds[1-2]
@io:oss oss[1-2]
@computes:cpu cpu[1-10]
@computes:gpu gpu[1-10]
```

With this configuration, you will be able to take advantage of customized names for your nodesets and also the Cluster functionality, which allows you to use ClusterShell in two different ways:

1. *Simple nodeset*:

```shell
[root@mngt0-1 ~]# clush -bw @io echo ok
---------------
mds[1-2],oss[1-2] (4)
---------------
ok
```

2. *Cluster nodeset*:

```shell
[root@mngt0-1 ~]# clush -bw @io:mds echo ok
---------------
mds[1-2] (2)
---------------
ok

[root@mngt0-1 ~]# clush -bw @io:oss echo ok
---------------
oss[1-2] (2)
---------------
ok
```

## To be done

Tree execution mode is missing.

## Changelog

* 1.2.1: Added cluster feature and custom nodeset mapping. Leonardo Araujo <lmagdanello40@gmail.com>
* 1.2.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Prevent dummy user to be included. Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
