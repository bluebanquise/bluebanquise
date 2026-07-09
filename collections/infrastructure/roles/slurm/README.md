# Slurm

OS compatibility:

|      OS      | Version | Supported |
|:-------------|:--------|:---------:|
| Ubuntu       |   20.04 |    yes (does not support local MYSQL installation) |
| Ubuntu       |   22.04 |    yes    |
| RHEL         |       7 |    yes    |
| RHEL         |       8 |    yes    |
| RHEL         |       9 |    yes    |
| OpenSuseLeap |      15 |    yes    |
| Debian       |      11 |    yes    |

- [Slurm](#slurm)
  * [Description](#description)
  * [Instructions](#instructions)
    + [Munge key](#munge-key)
    + [Apply](#apply)
    + [Configure main parameters](#configure-main-parameters)
    + [Review default settings](#review-default-settings)
    + [Additional slurm.conf settings](#additional-slurmconf-settings)
    + [Optional hosts tuning](#optional-hosts-tuning)
    + [Accounting](#accounting)
    + [Acct Gather](#acct-gather)
## Description

These settings provide slurm configuration for controller (server),
computes (client) and submitters (often called login) hosts.

## Instructions

### Setting slurm user id

You can specify slurm user gid/uid by setting the following variables, or keep it default (777):

```yaml
slurm_user_gid: 777
slurm_user_uid: 777
```

### Munge key

**IMPORTANT**: before using these settings, first thing to do is to generate a
new munge key file. This file need to be the same on all hosts of the Slurm cluster, and so need to be spread by these settings.

These settings do not provide default munge key file, as it is considered a security risk.

These settings support currently 2 ways to provide key file:

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

These settings will spread this file across all hosts of the Slurm cluster.

#### Provide base64 encoded string

Get base64 encoded string from the key, using:

```
base64 -w 0 munge.key
```

You should get long string as a result (example, but DO NOT USE IT!! : `hYcbkjJgv5YyybNqKbo+JvXLakIY2zFcZhpopipS8JmLmeE3YHgMcbUO74LIGKqzpIgD7ILPgUKmzgSl8BOK9WHQcMxywvh2fY567+4TyEq/HEArVfqdsIPw1U/jodDt2DL3MTNvci5hTJ8JNJZZKrjJc2x/FBlF52hAt+KLm+g=`). Copy it (beware not copying anything, as the command do not generate a new line at the end), and create a variable called `slurm_munge_key_b64` in the inventory, with the copied string as content:

```yaml
slurm_munge_key_b64: hYcbkjJgv5YyybNqKbo+JvXLakIY2zFcZhpopipS8JmLmeE3YHgMcbUO74LIGKqzpIgD7ILPgUKmzgSl8BOK9WHQcMxywvh2fY567+4TyEq/HEArVfqdsIPw1U/jodDt2DL3MTNvci5hTJ8JNJZZKrjJc2x/FBlF52hAt+KLm+g=
```

These settings will decode this string to generate key on all hosts of the Slurm cluster.

### Apply

To use these settings for all 3 types of hosts, simply add a vars in the playbook
when loading these settings. Extra vars is **slurm_profile**.

For a controller (server), use:

```yaml
- role: slurm
  tags: slurm
  vars:
    slurm_profile: controller
```

For a compute host (client), use:

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
slurm_controller_hostname: management1
slurm_partitions_list:
  - computes_groups:
      - fn_compute
    partition_name: all
    partition_configuration:
      State: UP
      Default: "YES"
```

Note: **partition_configuration** can cover all Slurm's available parameters for
a partition.

If you wish to create partitions, it is possible to define them. **computes_groups**
can be any groups of hosts, as long as all hosts used in these groups are included
in the groups defined under **slurm_computes_groups**. For example:

```yaml
slurm_cluster_name: bluebanquise
slurm_controller_hostname: management1
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
      Default: "YES"
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

By default, a small *cgroup.conf* file is generated by these settings, providing very basic but working configuration.
It is possible to define a whole cgroup.conf content using the multilines string `slurm_cgroup_conf_raw` variable.

For example:

```yaml
slurm_cgroup_conf_raw: |
  ConstrainCores=yes
  ConstrainDevices=yes
  ConstrainRAMSpace=yes
  ConstrainSwapSpace=yes
```

### Optional hosts tuning

It is possible to set variable **slurm_extra_nodes_parameters** under
**hw_specs** in an *equipment_profile* to add more parameters on the hosts
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

You also need to specify the user that will be used to query the database, and its password, using:

* `slurm_accounting_mysql_slurm_user`: Default: **slurm**. User used to connect to SQL database.
* `slurm_accounting_mysql_slurm_password`: Default: **ssap_slurm**. Please be sure to change this value in production. User password to connect to SQL database.

#### Database settings

You can then either choose to use a distant MYSQL server, or ask these settings to deploy one locally.

##### Using an external SQL database server

Ensure variable `slurm_accounting_enable_local_mysql` is set to **false**.

Then, first, set the following variables to configure remote server settings:

* `slurm_accounting_mysql_login_host`: SQL server remote server address or hostname. Default: 127.0.0.1
* `slurm_accounting_mysql_login_port`: SQL server remote server port (leave empty if default). Default: 3306

##### Deploying and using a local SQL database server

Ensure variable `slurm_accounting_enable_local_mysql` is set to **true**.

You should be able to let all `slurm_accounting_mysql_login_*` variables to default since these settings will use in this particular case local socket to communicate with the DB.

#### Setup slurm db and slurm user in database

If you wand these settings to create Slurm related database or Slurm related user into the SQL database, you need to set the following variables to true:

* `slurm_accounting_mysql_create_database`: if **true**, create **"slurm_acct_db"** database if not existing in MYSQL.
* `slurm_accounting_mysql_create_user`: if **true**, create needed user (set by `slurm_accounting_mysql_slurm_user` and `slurm_accounting_mysql_slurm_password`) into SQL database. This user will have rights on the **"slurm_acct_db"** database.

Then, if you set variable `slurm_accounting_enable_local_mysql` to **false** (which means you are using an external SQL DB), you will also need to set the following variable, to be able to connect to the external SQL server and create the slurm related database.

* `slurm_accounting_mysql_login_user`: SQL server remote user to login with a user able to create databases.
* `slurm_accounting_mysql_login_password`: SQL server remote user's password to login.

#### Specific port

You can choose to run the slurmdbd on a specific port using `slurm_dbd_port` key. By default, value is 6819.

#### Commands to be used once deployed

If you enable accounting, once these settings have been applied on
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

### Access restriction - pam_slurm_adoption

pam_slurm_adoption is a pam module created to make sure that users only can access cluster resources that are allocated to them. 

This means that users that dont have resources allocated on a compute host, wont be able to login into it. Also, when the user does have resources allocated, all his processes will be restricted to the same cgroup restrictions, what means that even if the user ssh into the host, it will be restricted by his allocated resources 

By default, pam_slurm_adoption is disabled, to enable it, change the following variable on your inventories:

```yaml
slurm_pam_slurm_adopt_enable: true
```

example in your slurm configuration:

```yaml
slurm_cluster_name: bluebanquise
slurm_controller_hostname: management1
slurm_pam_slurm_adopt_enable: true
slurm_partitions_list:
  - computes_groups:
      - os_debian12
      - os_debian11
    partition_name: debian
    partition_configuration:
      State: UP
      MaxTime: "72:00:00"
      DefaultTime: "24:00:00"
```

By default on EL8 systems, the local users on the system will not be afected by this configuration, including the root user.

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
  slurm_controller_hostname: management1
  slurm_selecttype: "select/cons_tres"
  slurm_grestypes: gpu
  slurm_partitions_list:
    - computes_groups:
        - hw_gpus
      partition_name: gpu_partoche
```

### AutoDetect nvml

If you wish to enable the auto-detection of GPU gres, you can do (example with GB200):
```yaml
hw_specs:
  slurm_extra_nodes_parameters: "Gres=gpu:nvidia_gb200:4"
```

To enable it on the slurm configuration its required to define the previous chapter options plus `slurm_grestypes_nvml: True`.

### Acct Gather

For example, to monitor the power and energy usage of compute hosts, you can use RAPL (Running Average Power Limit) method.
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
