
# BeeGFS

- [BeeGFS role](#slurm)
  * [Introduction](#introduction)
  * [Description](#description)
  * [Instructions](#instructions)
    + [Repository](#repository)
    + [Ansible variables](#ansible-variables)
    + [Ansible inventory](#ansible-inventory)
    + [To know](#to-know)
    + [Nodes Tuning](#nodes-tuning)
    + [BeeGFS deployment](#beegfs-deployment)
    + [BeeGFS basic command](#beegfs-basic-command)

  * [Testing environment](#testing-environment)
  * [Documentations](#documentations)
  * [Changelog](#changelog)

## Introduction

![Logo](https://www.beegfs.io/c/wp-content/uploads/2020/03/logo.png)

BeeGFS (Bee Giant File System) is an open-source parallel file system designed for HPC environments.

BeeGFS provides a distributed file system architecture that allows data to be spread across multiple servers or storage nodes. This makes it possible to achieve high levels of performance and scalability.

BeeGFS is designed to support large-scale HPC workloads and is used in a variety of industries, including scientific research, media and entertainment, finance, and energy.

Key features of BeeGFS :
- Distributed File Contents and Metadata
- Scalability
- Optimized for Highly Concurrent Access
- POSIX-compliant file system interfaces
- Performance
- Easy to Use
- RDMA Supports

## Description

This role provides the deployment of the BeeGFS a distributed filesystem with these following features:
- Deployment of metadata servers
- Tuning of metadata servers
- Deployment of storages targets
- Tuning of storages targets
- Mount BeeGFS filesystems on clients
- BeeGFS cluster purge (***Beware this will delete all data !***)


## Instructions

### Repository

Add a new repository and the GPG key on BlueBanquise inventory:

```bash
cat /etc/bluebanquise/inventory/group_vars/all/general_settings/repositories.yml
repositories:
  - bluebanquise
  - os
  - name: beegfs
    gpgkey: 'http://10.10.0.1/repositories/redhat/8.8/x86_64/beegfs/GPG-KEY-beegfs'
```

Download the BeeGFS packages and GPG key. For el8 distribution the files are available at :
- https://www.beegfs.io/release/beegfs_7.4.1/dists/rhel8/noarch/
- https://www.beegfs.io/release/beegfs_7.4.1/gpg/GPG-KEY-beegfs
- https://www.beegfs.io/release/beegfs_7.4.1/dists/rhel8/x86_64/

Create repodata on your local server.

```bash
cd /var/www/html/repositories/redhat/8.8/x86_64/beegfs/

createrepo --database -v .

ls -al
total 12
-rw-r--r--. 1 root root 3159 Oct 14  2022 GPG-KEY-beegfs
drwxr-xr-x. 2 root root 4096 Apr  3 11:56 packages
drwxr-xr-x. 2 root root 4096 Apr  3 11:56 repodata
```

Propagate via ansible the new repo addition.

```bash
cd /etc/bluebanquise
ansible-playbook playbooks/storages.yml -t repositories_client
```

### Ansible inventory

Create this file ```/etc/bluebanquise/inventory/cluster/beegfs/cluster.yml``` and paste the following example.

```yaml
beegfs_cluster:
  children:
    mgmtd:          # A group representing the management resource.
      hosts:
        bee-meta1:
    metadata:       # A group representing a metadata resource. To add additional metadata resources, define
      hosts:
        bee-meta1:  # Dictionary of nodes that may run this metadata resource
        bee-meta2:
    store:          # A group representing a storage resource. To add additional storage resources, define
      hosts:
        bee-store1: # Dictionary of nodes that may run this storage resource
        bee-store2:
        bee-store3:
        bee-store4:
    client:         # A group representing a client resource.
      hosts:
        compute1:   # Dictionary of nodes that may run this client resource
        compute2:
        compute3:
```

Check that the new group ```beegfs_cluster``` has been added to the ansible inventory.

```bash
cd /etc/bluebanquise/
ansible-inventory --gr beegfs_cluster

@beegfs_cluster:
  |--@client:
  |  |--compute1
  |  |--compute2
  |  |--compute3
  |--@metadata:
  |  |--bee-meta1
  |  |--bee-meta2
  |--@mgmtd:
  |  |--bee-meta1
  |--@store:
  |  |--bee-store1
  |  |--bee-store2
  |  |--bee-store3
  |  |--bee-store4
```

### Ansible variables

Create this file ```/etc/bluebanquise/inventory/group_vars/all/beegfs/beegfs_vars.yml``` and paste the following example.

```yaml
beegfs_vars:
  high_availability: false                        # Define to enable support for High Availability
  high_availability_autostart: yes                # Define the HA services will be activated on reboot
  mgmtd_vip:                                      # Define the Virtual IP for management service
  mgmtd_vip_prefix:                               # Define the prefix of the VIP (16 = 255.255.0.0)
  rdma: true                                      # Define to enable support for BeeGFS data transport over RDMA
  mgmtd_path_prefix: /data/beegfs/beegfs_mgmtd/   # Define the Management directory path
  meta_path_prefix: /data/beegfs/beegfs_meta      # Define the Metadata directory path
  store_path_prefix: /data/beegfs/beegfs_storage  # Define the Storage directory path
  log_path_prefix: /var/log/beegfs/               # Define the log directory path
  global_directory: /beegfs/scratch               # Define the global directory path
  meta_directory: /beegfs/metadata                # Define the Metadata directory path
  store_directory: /beegfs/storage                # Define the Storage directory path

beegfs_vm_tuning:                                 # Define tuning settings for Metadata and Storage nodes
  vm.dirty_background_ratio: 5                    # See https://www.kernel.org/doc/html/next/admin-guide/sysctl/vm.html
  vm.dirty_ratio: 70
  vm.vfs_cache_pressure: 50
  vm.min_free_kbytes: 262144
  vm.zone_reclaim_mode: 1
  vm.watermark_scale_factor: 1000

beegfs_devices:                                   # List all devices on all BeeGFS targets
  - "/dev/sdb"
  - "/dev/sdc"
  - "/dev/sdd"
  - "/dev/sde"
  - "/dev/sdf"
  - "/dev/sdg"
  - "/dev/sdh"
```

```beegfs_devices:``` You must list all the disk names of all your target storages that will be used by BeeGFS.
Don't put the duplicate disk names. Use the command: ```lsblk -d ```

### To know

**IMPORTANT**: We provide the BeeGFS authentication file, but for security reasons we recommend that you generate a new one via the following command: 
```bash
dd if=/dev/random of=/etc/bluebanquise/roles/custom/beegfs_deploy/files/connauthfile bs=128 count=1
```
You must provide a directory already mounted for BeeGFS for Metadata and Targets data.
Ideally an XFS filesystem in RAID 5 for Targets and EXT4 with RAID 1 for Metadata.

**Storage node partitionning options**
```bash
mkfs.xfs -d su=72k,sw=18 -l version=2,su=128k -i size=512 /dev/gdg0n1 -f
```
`sw=18` number of disks without parity disks (in this case 18 disks and 2 parity disks, total 20 disks in RAID 6)

more details: https://doc.beegfs.io/latest/advanced_topics/storage_tuning.html?highlight=mkfs#formatting-options

**Storage node mounting options**
```bash
mount -o noatime,nodiratime,logbufs=8,logbsize=256k,largeio,inode64,swalloc,allocsize=131072k /dev/gdg0n1 /beegfs/storage
```
**Metadata partitionning options**
```bash
mkfs.ext4 -i 2048 -I 1024 -J size=400 -Odir_index,filetype,large_dir <device>
```
more details: https://doc.beegfs.io/latest/advanced_topics/metadata_tuning.html?highlight=mkfs#formatting-options

**Metadata mounting options**
```bash
mount -onoatime,nodiratime /dev/md/bee-queen1\:beegfs-metadata-ok /beegfs/metadata
```
The directory to mount for Metadata is defined here
```/etc/bluebanquise/inventory/group_vars/all/beegfs/beegfs_vars.yml```, in the ```meta_directory: /beegfs/metadata``` variable.

The directory to mount for the Targets is defined here
```inventory/group_vars/all/beegfs/beegfs_vars.yml```, in the ```store_directory: /beegfs/storage ``` variable.

**Size of Metadata directory**

It recommend having about **0.3% to 0.5%** of the total storage capacity for metadata (more information: https://doc.beegfs.io/latest/system_design/system_requirements.html#metadata-nodes)

For example, for a storage capacity of 100 TB, 300 GB to 500 GB of Metadata capacity will be sufficient.

As a rule of thumb, 500GB of metadata capacity are sufficient for about 150 million files, if the underlying metadata storage is formatted with ext4.


### Nodes Tuning

A service (```beegfs-tuning.service```) is deployed on the Metadata and Storage Target Nodes by the role.
This service define a tuning on disks and kernel level and is able to know if the disks are HDD or SSD and to define an appropriate tuning.

For performance reasons please make sure that the service is enabled.

For more information, please refer to these pages:
- https://doc.beegfs.io/latest/advanced_topics/storage_tuning.html
- https://doc.beegfs.io/latest/advanced_topics/metadata_tuning.html

### BeeGFS deployment

```bash
cd /etc/bluebanquise
ansible-playbook playbooks/storages.yml -t beegfs_deploy
```
### BeeGFS basic command

**Check the cluster statu:**

```bash
[root@mgmtd ~]# beegfs-check-servers
Management
==========
bee-meta1[ID: 1]: reachable at 172.16.10.2:8008 (protocol: TCP)

Metadata
==========
bee-meta1[ID: 1]: reachable at 172.16.10.2:8005 (protocol: RDMA)
bee-meta2 [ID: 2]: reachable at 172.16.10.1:8005 (protocol: RDMA)

Storage
==========
bee-store1 [ID: 1]: reachable at 172.16.10.3:8003 (protocol: RDMA)
bee-store2 [ID: 2]: reachable at 172.16.10.4:8003 (protocol: RDMA)
bee-store3 [ID: 3]: reachable at 172.16.10.5:8003 (protocol: RDMA)
bee-store4 [ID: 4]: reachable at 172.16.10.6:8003 (protocol: RDMA)
```
**Optimization: Configure the striping**

Stripe files across 4 storage targets with a chunk size of 1 MB, run:
```bash
beegfs-ctl --setpattern --numtargets=4 --chunksize=1M /beegfs/scratch/
```
**Check the free space** 

```bash
[root@mgmtd ~]# beegfs-df
METADATA SERVERS:
TargetID   Cap. Pool        Total         Free    %      ITotal       IFree    %
========   =========        =====         ====    =      ======       =====    =
       1      normal    7826.4GiB    7684.5GiB  98%     4294.0M     3615.5M  84%
       2      normal    7826.4GiB    7686.7GiB  98%     4294.0M     3645.5M  85%

STORAGE TARGETS:
TargetID   Cap. Pool        Total         Free    %      ITotal       IFree    %
========   =========        =====         ====    =      ======       =====    =
       1      normal  257535.2GiB  196310.4GiB  76%     5400.9M     5183.8M  96%
       2      normal  257535.2GiB  196311.4GiB  76%     5400.9M     5183.8M  96%
       3      normal  257535.2GiB  196312.6GiB  76%     5400.9M     5183.8M  96%
       4      normal  257535.2GiB  196310.7GiB  76%     5400.9M     5183.8M  96%
```
**IOR benchmark**

```bash
module load mpi/openmpi-x86_64
export OMPI_MCA_btl=^openib
export OMPI_MCA_mca_base_component_show_load_errors=0

[root@compute1 ~]# /usr/lib64/openmpi/bin/mpirun  --allow-run-as-root  -np 256 -map-by node -hostfile /tmp/nodefile /root/ior-3.3.0/src/ior -wr -i1 -t1M -b 25G -F -g -e --posix.odirect -o /beegfs/scratch/
IOR-3.3.0: MPI Coordinated Test of Parallel I/O
Began               : Thu Sep 28 18:15:53 2023
Command line        : /root/ior-3.3.0/src/ior -wr -i1 -t1M -b 25G -F -g -e --posix.odirect -o /beegfs/scratch/
Machine             : Linux bee-queen1
TestID              : 0
StartTime           : Thu Sep 28 18:15:53 2023
Path                : /beegfs/scratch
FS                  : 1509.0 TiB   Used FS: 0.9%   Inodes: 0.0 Mi   Used Inodes: -nan%
 
Options:
api                 : POSIX
apiVersion          :
test filename       : /beegfs/scratch/
access              : file-per-process
type                : independent
segments            : 1
ordering in a file  : sequential
ordering inter file : no tasks offsets
nodes               : 8
tasks               : 256
clients per node    : 32
repetitions         : 1
xfersize            : 1 MiB
blocksize           : 25 GiB
aggregate filesize  : 6.25 TiB
 
Results:
 
access    bw(MiB/s)  IOPS       Latency(s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
------    ---------  ----       ----------  ---------- ---------  --------   --------   --------   --------   ----
write     75215      75230      0.003248    26214400   1024.00    0.010004   87.11      0.007280   87.13      0
remove    -          -          -           -          -          -          -          -          0.863602   0
Max Write: 75215.15 MiB/sec (78868.80 MB/sec)
 
Summary of all tests:
Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev   Max(OPs)   Min(OPs)  Mean(OPs)     StdDev    Mean(s) Stonewall(s) Stonewall(MiB) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt   blksiz    xsize aggs(MiB)   API RefNum
write       75215.15   75215.15   75215.15       0.00   75215.15   75215.15   75215.15       0.00   87.13138         NA            NA     0    256  32    1   1     0        1         0    0      1 26843545600  1048576 6553600.0 POSIX      0
Finished            : Thu Sep 28 18:17:21 2023
````

**Metadata benchmark**

```bash
module load mpi/openmpi-x86_64
export OMPI_MCA_btl=^openib
export OMPI_MCA_mca_base_component_show_load_errors=0

[root@bee-meta1~]# /usr/lib64/openmpi/bin/mpirun --allow-run-as-root -hostfile /tmp/nodefile --map-by node -np 32 /root/ior-4.0.0rc1/src/mdtest -C -T -F -r -E -d /begfs/metadata/ -I 12500 -z 2 -b 64 -L -u -e 100 -w 100 -i 1
-- started at 10/05/2023 14:16:00 --
 
mdtest-4.0.0rc1 was launched with 32 total task(s) on 1 node(s)
Command line used: /root/ior-4.0.0rc1/src/mdtest '-C' '-T' '-F' '-r' '-E' '-d' '/beegfs/metadata/' '-I' '12500' '-z' '2' '-b' '64' '-L' '-u' '-e' '100' '-w' '100' '-i '1'
Path                : /beegfs/metadata/
FS                  : 7.6 TiB   Used FS: 0.0%   Inodes: 4095.1 Mi   Used Inodes: 0.0%
Nodemap: 11111111111111111111111111111111
32 tasks, 1638400000 files
 
SUMMARY rate: (of 1 iterations)
   Operation                     Max            Min           Mean        Std Dev
   ---------                     ---            ---           ----        -------
   File creation                9028.799       9028.799       9028.799          0.000
   File stat                  355963.122     355963.122     355963.122          0.000
   File read                  306151.314     306151.314     306151.314          0.000
   File removal               172238.187     172238.187     172238.187          0.000
   Tree creation                4585.244       4585.244       4585.244          0.000
   Tree removal                   36.595         36.595         36.595          0.000
-- finished at 10/07/2023 22:06:46 --
```


## Testing environment

This role has been tested on the following environment:

```bash
OS:             Red Hat Enterprise Linux 8.8 (Ootpa)
Kernel:         4.18.0-477.27.1.el8_8.x86_64
BeeGFS version: 7.4.1
Ansible:        2.11.12
Python:         3.6.8
BlueBanquise:   1.6.0
pacemaker:      2.1.4-5.el8_7.2
pcs:            0.10.14
corosync:       3.1.5
DRBD_KERNEL:    9.1.13
DRBDADM:        9.23.1
```

## Documentations

- https://doc.beegfs.io/latest/index.html
- https://docs.netapp.com/us-en/beegfs/index.html


## Changelog

* 1.0.0: Role creation. Hamid Merzouki <hamid.merzouki@naverlabs.com>

