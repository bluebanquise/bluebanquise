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
new munge key file. This file need to be the same on all nodes of the Slurm cluster, and so need to be spread by the role.

The role do not provide default munge key file, as it is considered a security risk.

The role supports currently 2 ways to provide key file:

* Provide plain file into `files` subfolder of executed playbook folder
* Provide base64 encoded string

First step for both methods is to generate a new munge.key file locally using (note that you need munge package to be installed on your system):

```
mungekey -c -k munge.key
```

Then, next step depends of method choose.

#### Provide plain file

Assuming your playbooks folder is `$HOME/playbooks`, create a `files` subfolder, and place your key inside:

```
mkdir -p $HOME/playbooks/files
mv munge.key $HOME/playbooks/files/munge.key
```

Role will spread this file across all nodes of the Slurm cluster.

#### Provide base64 encoded string

Get base64 encoded string from the key, using:

```
base64 -w 0 munge.key
```

You should get long string as a result (example, but DO NOT USE IT!! : `hYcbkjJgv5YyybNqKbo+JvXLakIY2zFcZhpopipS8JmLmeE3YHgMcbUO74LIGKqzpIgD7ILPgUKmzgSl8BOK9WHQcMxywvh2fY567+4TyEq/HEArVfqdsIPw1U/jodDt2DL3MTNvci5hTJ8JNJZZKrjJc2x/FBlF52hAt+KLm+g=`). Copy it (beware not copying anything, as the command do not generate a new line at the end), and create a variable called `slurm_munge_key_b64` in the inventory, with the copied string as content:

```yaml
slurm_munge_key_b64: hYcbkjJgv5YyybNqKbo+JvXLakIY2zFcZhpopipS8JmLmeE3YHgMcbUO74LIGKqzpIgD7ILPgUKmzgSl8BOK9WHQcMxywvh2fY567+4TyEq/HEArVfqdsIPw1U/jodDt2DL3MTNvci5hTJ8JNJZZKrjJc2x/FBlF52hAt+KLm+g=
```

Role will decode this string to generate key on all nodes of the Slurm cluster.

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
**slurm_slurm_conf_additional_content** list variable.

### Optional nodes tuning

It is possible to set variable **slurm_extra_nodes_parameters** under
**ep_hardware** in an *equipment_profile* to add more parameters on the nodes
definition line.

For example, setting:

```yaml
ep_hardware:
  cpu:
    architecture: x86_64
    cores: 24
    corespersocket: 10
    sockets: 2
    threadspercore: 1
  memory: 63500
  slurm_extra_nodes_parameters: Feature=XXXX Weight=YY
```

Would lead to:

```
NodeName=c[001-200] Procs=256 Sockets=8 CoresPerSocket=16 ThreadsPerCore=2 FeatureXXXX Weight=YY
```

In the final *slurm.conf* configuration file.

### Accounting

To enable Accounting the community.mysql ansible module is required:

```bash
ansible-galaxy collection install community.mysql
```

If you enable accounting, once the role has been applied on
controller, check existence of the cluster in the database:

```bash
sacctmgr list cluster
```

If cluster is not here, add it using (assuming cluster name is *algoric*):

```bash
sacctmgr add cluster algoric
```

And check again if the cluster exist:

```bash
sacctmgr list cluster
```

### GPU Gres

Unfortunately for now, this is only supported for NVIDIA GPUS.

To Enable GPU gres the GPUS needs to be defined on the equipment_profile. You can check the GPU names with the following command:

```bash
$ nvidia-smi -L
```

You need to add the Gres extra arguments for slurm as well, so you would add something like the following to your equipment_profile.yml file if you have 8x NVIDIA A100-SXM4-40GB on your hardawre for example:

```yaml
ep_hardware:
  slurm_extra_nodes_parameters: "Gres=gpu:8"
  [...]
  gpu:
    - NVIDIA A100-SXM4-40GB
    - NVIDIA A100-SXM4-40GB
    - NVIDIA A100-SXM4-40GB
    - NVIDIA A100-SXM4-40GB
    - NVIDIA A100-SXM4-40GB
    - NVIDIA A100-SXM4-40GB
    - NVIDIA A100-SXM4-40GB
    - NVIDIA A100-SXM4-40GB
```

To enable it on the slurm configuration its required to define `slurm_selecttype: "select/cons_tres"` and `slurm_grestypes: gpu`. For example:

```yaml
  slurm_cluster_name: bluebanquise
  slurm_control_machine: management1
  slurm_selecttype: "select/cons_tres"
  slurm_grestypes: gpu
  slurm_computes_groups:
    - equipment_typeC
  slurm_partitions_list:
    - computes_groups:
        - equipment_typeC
        - equipment_typeC_gpu
      partition_name: typeC
```

## Changelog

* 1.2.3: Fix old CamelCase variables. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.2: Improve partition definition readability in slurm.conf. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.1: Update to BB 2.0 format. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.0: Added GPU Gres configuration. Lucas Santos <lucassouzasantos@gmail.com>
* 1.1.1: Missing string filter in template. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Role major upgrade. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Update role, remove munge key. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
