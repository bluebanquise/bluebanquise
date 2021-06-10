# Slurm

- [Slurm](#slurm)
  * [Description](#description)
  * [Instructions](#instructions)
    + [Munge key](#munge-key)
    + [Apply role](#apply-role)
    + [Configure main parameters](#configure-main-parameters)
    + [Review default settings](#review-default-settings)
    + [Additional slurm.conf settings](#additional-slurmconf-settings)
    + [Optional nodes tuning](#optional-nodes-tuning)
    + [Accounting](#accounting)
  * [Changelog](#changelog)

## Description

This role provides slurm configuration for controller (server),
computes (client) and submitters (often called login) nodes.

Note: this role requires *bluebanquise_filters* package to be installed.

## Instructions

### Munge key

**IMPORTANT**: before using the role, first thing to do is to generate a
new munge key file. To do so, generate a new munge.key file using:

```
dd if=/dev/urandom bs=1 count=1024 > munge.key
mungekey -c -k /etc/bluebanquise/roles/community/slurm/files/munge.key
```

I do not provide default munge key file, as it is considered a security risk.
(Too much users were using the example key).

### Apply role

To use this role for all 3 types of nodes, simply add a vars in the playbook
when loading the role. Extra vars is **slurm_profile**.

For a controller (server), use:

```yaml
  - role: slurm
    tags: slurm
    vars:
      slurm_profile: controller
```

For a compute node (client), use:

```yaml
  - role: slurm
    tags: slurm
    vars:
      slurm_profile: compute
```

And for a submitter (passive client, login), use:

```yaml
  - role: slurm
    tags: slurm
    vars:
      slurm_profile: submitter
```

### Configure main parameters

Then, in the inventory addons folder (inventory/group_vars/all/addons that should
be created if not exist), add a slurm.yml file with the following minimal content,
tuned according to your needs:

```yaml
  slurm_cluster_name: bluebanquise
  slurm_control_machine: management1
  slurm_computes_groups:
    - equipment_typeC
  slurm_all_partition:
      enable: true
      partition_configuration:
        State: UP
        Default: yes
```

Note: **partition_configuration** can cover all Slurm's available parameters for
a partition.

If you wish to create partitions, it is possible to define them. **computes_groups**
can be any groups of nodes, as long as all nodes used in these groups are included
in the groups defined under **slurm_computes_groups**. For example:

```yaml
  slurm_cluster_name: bluebanquise
  slurm_control_machine: management1
  slurm_computes_groups:
    - equipment_typeC
  slurm_partitions_list:
    - computes_groups:
        - equipment_typeC
        - equipment_typeC_gpu
      partition_name: typeC
      partition_configuration:
        State: UP
        MaxTime: "72:00:00"
        DefaultTime: "24:00:00"
        Default: yes
    - computes_groups:
        - rack1
        - rack2
        - rack3
      partition_name: rack_room1
      partition_configuration:
        State: UP
  slurm_all_partition:
      enable: true
      partition_configuration:
        State: UP
        MaxTime: "72:00:00"
        DefaultTime: "24:00:00"
```

This will work as long as all nodes included in groups `rack1 + rack2 + rack3`
are all contained in groups `equipment_typeC + equipment_typeC_gpu`.

### Review default settings

Check content of *defaults/main.yml* file and precedence variables you need to
tune.

### Additional slurm.conf settings

It is possible to add more content into *slurm.conf* file using the multi-lines
**slurm_slurm_conf_additional_content** variable.

### Optional nodes tuning

It is possible to set variable **slurm_extra_nodes_parameters** under
**ep_hardware** in an *equipment_profile* to add more parameters on the nodes
definition line.

For example, setting:

```yaml
ep_hardware:
  slurm_extra_nodes_parameters: Feature=XXXX Weight=YY
```

Would lead to:

```
NodeName=c[001-200] Procs=256 Sockets=8 CoresPerSocket=16 ThreadsPerCore=2 FeatureXXXX Weight=YY
```

In the final *slurm.conf* configuration file.

### Accounting

If you enable accounting, once the role has been applied on
controller, check existence of the cluster in the database:

```
sacctmgr list cluster
```

If cluster is not here, add it using (assuming cluster name is *algoric*):

```
sacctmgr add cluster algoric
```

And check again if the cluster exist:

```
sacctmgr list cluster
```

## Changelog

* 1.1.0: Role major upgrade. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Update role, remove munge key. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
