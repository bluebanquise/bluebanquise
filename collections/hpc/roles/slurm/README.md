# Slurm

Role compatibility:

|      OS      | Version | Supported |
|:-------------|:--------|:---------:|
| Ubuntu       |   20.04 |    yes (does not support local MYSQL installation) |
| Ubuntu       |   22.04 |    yes (does not support local MYSQL installation) |
| RHEL         |       7 |    yes    |
| RHEL         |       8 |    yes    |
| RHEL         |       9 |    yes    |
| OpenSuseLeap |      15 |    yes    |
| Debian       |      11 |    yes    |

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
    + [Acct Gather](#acct-gather)
  * [Changelog](#changelog)

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 3.2 (Hardware Groups)

## Description

This role provides slurm configuration for controller (server),
computes (client) and submitters (often called login) nodes.

## Instructions

### Setting slurm user id

You can specify slurm user gid/uid by setting the following variables, or keep it default (777):

```yaml
slurm_user_gid: 777
slurm_user_uid: 777
```

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

In any case, if your `inventory` or `playbooks/files/` folders are hosted on a sensitive server or stored in a version controlled repository (git, ...), you should **strongly** consider encrypting the key file or the inventory files with an [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html).

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

Then, in the inventory addons folder (inventory/group_vars/all/ that should
be created if not exist), add a slurm.yml file with the following minimal content,
tuned according to your needs:

```yaml
slurm_cluster_name: bluebanquise
slurm_control_machine: management1
slurm_partitions_list:
  - computes_groups:
      - fn_compute
    partition_name: all
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
slurm_partitions_list:
  - computes_groups:
      - os_debian12
      - os_debian11
    partition_name: debian
    partition_configuration:
      State: UP
      MaxTime: "72:00:00"
      DefaultTime: "24:00:00"
  - computes_groups:
      - rack1
      - rack2
      - rack3
    partition_name: rack_room1
    partition_configuration:
      State: UP
  - computes_groups:
      - fn_compute
    partition_name: all
    partition_configuration:
      State: UP
      Default: yes
```

### Review default settings

Check content of *defaults/main.yml* file and precedence variables you need to
tune.

### Additional slurm.conf settings

It is possible to add more content into *slurm.conf* file using the multi-lines
**slurm_slurm_conf_additional_content** list variable.

Example:

```yaml
slurm_slurm_conf_additional_content:
  - KillWait=60
  - KillOnBadExit=1
```

### Additional slurmdbd.conf settings

It is possible to add more content into *slurmdbd.conf* file using the multi-lines
**slurm_slurmdbd_conf_additional_content** list variable, the same way **slurm_slurm_conf_additional_content** is used.

Example:

```yaml
slurm_slurmdbd_conf_additional_content:
  - ArchiveSteps=yes
```

### Raw cgroup.conf content

By default, a small *cgroup.conf* file is generated by the role, providing very basic but working configuration.
It is possible to define a whole cgroup.conf content using the multilines string `slurm_cgroup_conf_raw` variable.

For example:

```yaml
slurm_cgroup_conf_raw: |
  ConstrainCores=yes
  ConstrainDevices=yes
  ConstrainRAMSpace=yes
  ConstrainSwapSpace=yes
```

### Optional nodes tuning

It is possible to set variable **slurm_extra_nodes_parameters** under
**hw_specs** in an *equipment_profile* to add more parameters on the nodes
definition line.

For example, setting:

```yaml
hw_specs:
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

Then, set `slurm_enable_accounting` variable to **true**.

Configuration then depends on your needs.

#### Database and login user settings

Note that if you wand the role to create Slurm related database or Slurm related user into the MYSQL database, you need to set the following variables to true:

* `slurm_accounting_mysql_create_database`: if **true**, create **"slurm_acct_db"** database if not existing in MYSQL.
* `slurm_accounting_mysql_create_user`: if **true**, create needed user (set by `slurm_accounting_storage_user`) into MYSQL. This user will have rights on the **"slurm_acct_db"** database.

Also, set the following variables to configure Slurm database user settings:

* `slurm_accounting_storage_user`: user to be used by slurmdbd process to login into databse. Default: **slurm**.
* `slurm_accounting_storage_pass`: password to be used by slurmdbd process to login into database. Default: **ssap_slurm**. Please be sure to change this value in production.

You can then either choose to use a distant MYSQL server, or ask the role to deploy one locally.

#### Using an external MYSQL database server

Ensure variable `slurm_enable_local_mysql` is set to **false**.

Then, set the following variables to configure remote server settings:

* `slurm_accounting_mysql_login_host`: MYSQL server remote server address or hostname.
* `slurm_accounting_mysql_login_port`: MYSQL server remote server port (leave empty if default).
* `slurm_accounting_mysql_login_user`: MYSQL server remote server user to login.
* `slurm_accounting_mysql_login_password`: MYSQL server remote server password to login.

#### Deploying and using a local MYSQL database server

Ensure variable `slurm_enable_local_mysql` is set to **true**.

You should be able to let all `slurm_accounting_mysql_login_*` variables to default.

#### Commands to be used once deployed

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

You need to add the Gres extra arguments for slurm as well, so you would add something like the following to your equipment_profile.yml file if you have 8x NVIDIA A100-SXM4-40GB on your hardware for example:

```yaml
hw_specs:
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
  slurm_partitions_list:
    - computes_groups:
        - hw_gpus
      partition_name: gpu_partoche
```

### Acct Gather

For example, to monitor the power and energy usage of compute nodes, you can use RAPL (Running Average Power Limit) method.
But this method monitors CPUs and RAM only.
This is enabled in slurm by setting these variables:

```
slurm_acct_gather_node_freq: 30
slurm_acct_gather_energy_type: rapl
```

Do a `scontrol reconfig` and the power values become available:

```
$ scontrol show node n123
...
   CurrentWatts=239 LowestJoules=17445 ConsumedJoules=2581586467
```

Note: For some types of plugins it will be necessary to define some associated options which can be found in the slurm configuration file acct_gather.conf.
See more explanation on https://slurm.schedmd.com/acct_gather.conf.html

## Changelog

* 1.6.1: Add missing handler for scrontrol. Code from @vedmonds. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.0: Add slurmdbd.conf additional content, raw cgroup.conf, and job_submit.lua. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.0: Add ability to define slurm user id. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.2: Improve code. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.1: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.0: Add capacity to bind to an external MYSQL database. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Added acct_gather plugin configuration. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.5: RedHat 9 packages file. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.4: Set accounting host name in `slurm.conf` in order to allow submitters to connect. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.3: Fix old CamelCase variables. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.2: Improve partition definition readability in slurm.conf. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.1: Update to BB 2.0 format. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.2.0: Added GPU Gres configuration. Lucas Santos <lucassouzasantos@gmail.com>
* 1.1.1: Missing string filter in template. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Role major upgrade. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Update role, remove munge key. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
