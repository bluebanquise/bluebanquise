# HPC cluster

It is assumed here that you already deployed a generic cluster of nodes (see [dedicated tutorial]())

### 3.4. Computational resources management

The **job scheduler** is the conductor of computational resources of the cluster.

A **job** is a small script, that contains instructions on how to execute the calculation program, and that also contains information for to the job scheduler (required job duration, how much resources are needed, etc.).
When a user ask the job scheduler to execute a **job**, which is call **submitting a job**, the job enter **jobs queue**.
The job scheduler is then in charge of finding free computational resources depending of the needs of the job, then launching the job and monitoring it during its execution. Note that the job scheduler is in charge of managing all jobs to ensure maximum usage of computational resources, which is why sometime, the job scheduler will put some jobs on hold for a long time in a queue, to wait for free resources.
In return, after user has submitted a job, the job scheduler will provide user a **job ID** to allow following job state in the jobs queue and during its execution.


## 8. Slurm

Let's install now the cluster job scheduler, Slurm.

First, we need to build packages. Grab Munge and Slurm sources.
Munge will be used to handle authentication between Slurm daemons.

Note: beware, links may change over time, especially Slurm from Schemd. You may need to update URLs.

```
wget https://github.com/dun/munge/releases/download/munge-0.5.14/munge-0.5.14.tar.xz
dnf install bzip2-devel openssl-devel zlib-devel -y
wget https://github.com/dun.gpg
wget https://github.com/dun/munge/releases/download/munge-0.5.14/munge-0.5.14.tar.xz.asc
rpmbuild -ta munge-0.5.14.tar.xz
```

Now install munge, as it is needed to build slurm:

```
cp /root/rpmbuild/RPMS/x86_64/munge-* /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
createrepo /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
dnf clean all
dnf install munge munge-libs munge-devel
```

Now build slurm packages:

```
wget https://download.schedmd.com/slurm/slurm-20.11.7.tar.bz2
dnf install munge munge-libs munge-devel
dnf install pam-devel readline-devel perl-ExtUtils-MakeMaker
dnf install mariadb mariadb-devel
rpmbuild -ta slurm-20.11.7.tar.bz2
cp /root/rpmbuild/RPMS/x86_64/slurm* /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
createrepo /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
dnf clean all
```

Slurm controller side is called slurmctld while on compute nodes, it is called slurmd .
On the "submitter" node, no daemon except munge is required.

Tip: if anything goes wrong with slurm, proceed as following:

1. Ensure time is exactly the same on nodes. If time is different, munge based authentication will fail.
2. Ensure munge daemon is started, and that munge key is the same on all hosts (check md5sum for example).
3. Stop slurmctld and stop slurmd daemons, and start them in two different shells manually in debug + verbose mode: `slurmctld -D -vvvvvvv` in shell 1 on controller server, and `slurmd -D -vvvvvvv` in shell 2 on compute node.

### 8.1. Controller

Install munge needed packages:

```
dnf install munge munge-libs
```

And generate a munge key:

```
mungekey -c -f -k /etc/munge/munge.key
chown munge:munge /etc/munge/munge.key
```

We will spread this key over all servers of the cluster.

Lets start and enable munge daemon:

```
systemctl start munge
systemctl enable munge
```

Now install slurm controller `slurmctld` packages:

```
dnf install slurm slurm-slurmctld -y
groupadd -g 567 slurm
useradd  -m -c "Slurm workload manager" -d /etc/slurm -u 567 -g slurm -s /bin/false slurm
mkdir /etc/slurm
mkdir /var/log/slurm
mkdir -p /var/spool/slurmd/StateSave
chown -R slurm:slurm /var/log/slurm
chown -R slurm:slurm /var/spool/slurmd
```

Lets create a very minimal slurm configuration.

Create file `/etc/slurm/slurm.conf` with the following content:

```
# Documentation:
# https://slurm.schedmd.com/slurm.conf.html

## Controller
ClusterName=valhalla
ControlMachine=odin

## Authentication
SlurmUser=slurm
AuthType=auth/munge
CryptoType=crypto/munge

## Files path
StateSaveLocation=/var/spool/slurmd/StateSave
SlurmdSpoolDir=/var/spool/slurmd/slurmd
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmdPidFile=/var/run/slurmd.pid

## Logging
SlurmctldDebug=5
SlurmdDebug=5

## We don't want a node to go back in pool without sys admin acknowledgement
ReturnToService=0

## Using pmi/pmi2/pmix interface for MPI
MpiDefault=pmi2

## Basic scheduling based on nodes
SchedulerType=sched/backfill
SelectType=select/linear

## Nodes definition
NodeName=valkyrie01 Procs=1
NodeName=valkyrie02 Procs=1

## Partitions definition
PartitionName=all MaxTime=INFINITE State=UP Default=YES Nodes=valkyrie01,valkyrie02
```

Also create file `/etc/slurm/cgroup.conf` with the following content:

```
CgroupAutomount=yes
ConstrainCores=yes
```

And start slurm controller:

```
systemctl start slurmctld
systemctl enable slurmctld
```

Using `sinfo` command, you should now see the cluster start, with both computes nodes down for now.

### 8.2. Computes nodes

On both `valkyrie01,valkyrie02` nodes, install munge the same way than on controller.

```
clush -bw valkyrie01,valkyrie02 dnf install munge -y
```

Ensure munge key generated on controller node is spread on each client. From `odin`, scp the file:

```
clush -w valkyrie01,valkyrie02 --copy /etc/munge/munge.key --dest /etc/munge/munge.key
clush -bw valkyrie01,valkyrie02 chown munge:munge /etc/munge/munge.key
```

And start munge on each compute node:

```
clush -bw valkyrie01,valkyrie02 systemctl start munge
clush -bw valkyrie01,valkyrie02 systemctl enable munge
```

Now on each compute node, install slurmd needed packages:

```
clush -bw valkyrie01,valkyrie02 dnf clean all
clush -bw valkyrie01,valkyrie02 dnf install slurm slurm-slurmd -y
```

Now again, spread same slurm configuration files from `odin` to each compute nodes:

```
clush -bw valkyrie01,valkyrie02 groupadd -g 567 slurm
clush -bw valkyrie01,valkyrie02 'useradd  -m -c "Slurm workload manager" -d /etc/slurm -u 567 -g slurm -s /bin/false slurm'
clush -bw valkyrie01,valkyrie02 mkdir /etc/slurm
clush -bw valkyrie01,valkyrie02 mkdir /var/log/slurm
clush -bw valkyrie01,valkyrie02 mkdir -p /var/spool/slurmd/slurmd
clush -bw valkyrie01,valkyrie02 chown -R slurm:slurm /var/log/slurm
clush -bw valkyrie01,valkyrie02 chown -R slurm:slurm /var/spool/slurmd
clush -w valkyrie01,valkyrie02 --copy /etc/slurm/slurm.conf --dest /etc/slurm/slurm.conf
clush -w valkyrie01,valkyrie02 --copy /etc/slurm/cgroup.conf --dest /etc/slurm/cgroup.conf
```

And start on each compute node slurmd service:

```
clush -bw valkyrie01,valkyrie02 systemctl start slurmd
clush -bw valkyrie01,valkyrie02 systemctl enable slurmd
```

And simply test cluster works:

```
scontrol update nodename=valkyrie01,valkyrie02 state=idle
```

Now, sinfo shows that one node is idle, and srun allows to launch a basic job:

```
[root@odin ~]# sinfo
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
all*         up   infinite      1   unk* valkyrie02
all*         up   infinite      1   idle valkyrie01
[root@odin ~]# srun -N 1 hostname
valkyrie01.cluster.local
[root@odin ~]#
```

### 8.3. Submitter

Last step to deploy slurm is to install the login node, `heimdall`, that will act as
a submitter.

A slurm submitter only need configuration files, and an active munge.

Install munge the same way than on controller.

```
dnf install munge
```

Ensure munge key generated on controller node is spread here:

```
scp /etc/munge/munge.key heimdall:/etc/munge/munge.key
```

And start munge on `heimdall`:

```
systemctl start munge
systemctl enable munge
```

No install minimal slurm packages:

```
dnf install slurm
```

Now again, spread same slurm configuration files from `odin` to `heimdall`:

```
scp /etc/slurm/slurm.conf heimdall:/etc/slurm/slurm.conf
scp /etc/slurm/cgroup.conf heimdall:/etc/slurm/cgroup.conf
```

Nothing to start here, you can test `sinfo` command from `heimdall` to ensure it works.

Slurm cluster is now ready.

### 8.4. Submitting jobs

To execute calculations on the cluster, users will rely on Slurm to submit jobs and get calculation resources.
Submit commands are `srun` and `sbatch`.

Before using Slurm, it is important to understand how resources are requested.
A calculation node is composed of multiple calculation cores. When asking for resources, it is possible to ask the following:

* I want this much calculations processes (one per core), do what is needed to provide them to me -> use `-n`.
* I want this much nodes, I will handle the rest -> use `-N`.
* I want this much nodes and I want you to start this much processes per nodes -> use `-N` combined with `--ntasks-per-node`.
* I want this much calculations processes (one per core), and this much processes per nodes, calculate yourself the number of nodes required for that -> use `--ntasks-per-node` combined with `-n`.
* Etc.

`-N`, `-n` and `--ntasks-per-node` are complementary, and only two of them should be used at a time (slurm will deduce the last one using number of cores available on compute nodes as written in the slurm configuration file).
`-N` specifies the total number of nodes to allocate to the job, `-n` the total number of processes to start, and `--ntasks-per-node` the number of processes to launch per node.

```
n=N*ntasks-per-node
```

Here, we will see the following submittion ways:

1. Submitting without a script
2. Submitting a basic job script
3. Submitting a serial job script
4. Submitting an OpenMP job script
5. Submitting an MPI job script
6. A real life example with submitting a 3D animation render on a cluster combining Blender and Slurm arrays.

#### 8.4.1. Submitting without a script

It is possible to launch a very simple job without a script, using the `srun` command. To do that, use `srun` directly, specifying the number of nodes required. For example:

```
srun -N 1 hostname
```

Result can be: `valkyrie01`

```
srun -N 2 hostname
```

Result can be :

```
valkyrie01
valkyrie02
```

Using this method is a good way to test cluster, or compile code on compute nodes directly, or just use the compute and memory capacity of a node to do simple tasks on it.

#### 8.4.2. Basic job script

To submit a basic job scrip, user needs to use `sbatch` command and provides it a script to execute which contains at the beginning some Slurm information.

A very basic script is:

```
#!/bin/bash                                                                                    
#SBATCH -J myjob                                                                              
#SBATCH -o myjob.out.%j                                                                       
#SBATCH -e myjob.err.%j                                                                       
#SBATCH -N 1                                                                                   
#SBATCH -n 1                                                                                   
#SBATCH --ntasks-per-node=1                                                                    
#SBATCH -p all                                                                        
#SBATCH --exclusive                                                                            
#SBATCH -t 00:10:00                                                                            

echo "###"                                                                                     
date                                                                                           
echo "###"                                                                                     

echo "Hello World ! "
hostname
sleep 30s
echo "###"
date
echo "###"
```

It is very important to understand Slurm parameters here:
*	`-J` is to set the name of the job
*	`-o` to set the output file of the job
*	`-e` to set the error output file of the job
*	`-p` to select partition to use (optional)
*	`--exclusive` to specify nodes used must not be shared with other users (optional)
*	`-t` to specify the maximum time allocated to the job (job will be killed if it goes beyond, beware). Using a small time allow to be able to run a job quickly in the waiting queue, using a large time will force to wait more
*	`-N`, `-n` and `--ntasks-per-node` were already described.

To submit this script, user needs to use sbatch:

```
sbatch myscript.sh
```

If the script syntax is ok, `sbatch` will return a job id number. This number can be used to follow the job progress, using `squeue` (assuming job number is 91487):

```
squeue -j 91487
```

Check under ST the status of the job. PD (pending), R (running), CA (cancelled), CG (completing), CD (completed), F (failed), TO (timeout), and NF (node failure).

It is also possible to check all user jobs running:

```
squeue -u myuser
```

In this example, execution results will be written by Slurm into `myjob.out.91487` and `myjob.err.91487`.

#### 8.4.3. Serial job

To launch a very basic serial job, use the following template as a script for `sbatch`:

```
#!/bin/bash
#SBATCH -J myjob
#SBATCH -o myjob.out.%j
#SBATCH -e myjob.err.%j
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive
#SBATCH -t 03:00:00

echo "############### START #######"
date
echo "############### "

/home/myuser/./myexecutable.exe

echo "############### END #######"
date
echo "############### "
```

#### 8.4.4. OpenMP job

To launch an OpenMP job (with multithreads), assuming the code was compiled with openmp flags, use:

```
#!/bin/bash
#SBATCH -J myjob
#SBATCH -o myjob.out.%j
#SBATCH -e myjob.err.%j
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive
#SBATCH -t 03:00:00

## If compute node has 24 cores
export OMP_NUM_THREADS=24
## If needed, to be tuned to needs
export OMP_SCHEDULE="dynamic, 100"

echo "############### START #######"
date
echo "############### "

/home/myuser/./myparaexecutable.exe

echo "############### END #######"
date
echo "############### "
```

Note that it is assumed here that a node has 24 cores.

#### 8.4.5. MPI job

To submit an MPI job, assuming the code was parallelized with MPI and compile with MPI, use (note the `srun`, replacing the `mpirun`):

```
#!/bin/bash
#SBATCH -J myjob
#SBATCH -o myjob.out.%j
#SBATCH -e myjob.err.%j
#SBATCH -N 4
#SBATCH --ntasks-per-node=24
#SBATCH --exclusive
#SBATCH -t 03:00:00

echo "############### START #######"
date
echo "############### "

srun /home/myuser/./mympiexecutable.exe

echo "############### END #######"
date
echo "############### "
```

`srun` will act as `mpirun`, but providing automatically all already tuned arguments for the cluster.

#### 8.4.6. Real life example with Blender job

Blender animations/movies are render using CPU and GPU. In this tutorial, we will focus on CPU since we do not have GPU (or if you have, lucky you).

We will render an animation of 40 frames.

We could create a simple job, asking Blender to render this animation. But Blender will then use a single compute node. We have a cluster at disposal, lets take advantage of that.

We will use Slurm job arrays (so an array of jobs) to split these 40 frames into chuck of 5 frames. Each chuck will be a unique job. Using this method, we will use all available computes nodes of our small cluster.

Note that 5 is an arbitrary number, and this depend of how difficult to render each frame is. If a unique frame takes 10 minutes to render, then you can create chink of 1 frame. If on the other hand each frame takes 10s to render, it is better to group them by chunk as Blender as a "starting time" for each new chunk.

First download Blender and the demo:

```
wget https://download.blender.org/demo/geometry-nodes/candy_bounce_geometry-nodes_demo.blend
wget https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.93/blender-2.93.1-linux-x64.tar.xz
```

Extract Blender into `/software` and copy demo file into `/home`:

```
cp candy_bounce_geometry-nodes_demo.blend /home
tar xJvf blender-2.93.1-linux-x64.tar.xz -C /software
```

Now lets create the job file. Create file `/home/blender_job.job` with the following content:

```
#!/bin/bash
#SBATCH -J myjob
#SBATCH -o myjob.out.%j
#SBATCH -e myjob.err.%j
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive
#SBATCH -t 01:00:00

set -x

# We set chunk size to 5 frames
chunk_size=5

# We calculate frames span for each job depending of ARRAY_TASK_ID
range_min=$(((SLURM_ARRAY_TASK_ID-1)*chunk_size+1))
range_max=$(((SLURM_ARRAY_TASK_ID)*chunk_size))

# We include blender binary into our PATH
export PATH=/software/blender-2.93.1-linux-x64/:$PATH

# We start the render
# -b is the input blender file
# -o is the output target folder, with files format
# -F is the output format
# -f specify the range
# -noaudio is self explaining
# IMPORTANT: Blender arguments must be given in that specific order.

eval blender -b /home/candy_bounce_geometry-nodes_demo.blend -o /home/frame##### -F PNG -f $range_min..$range_max -noaudio

# Note: if you have issues with default engine, try using CYCLES. Slower.
# eval blender -b /home/candy_bounce_geometry-nodes_demo.blend -E CYCLES -o /home/frame##### -F PNG -f $range_min..$range_max -noaudio

```

This job file will be executed for each job.
Since we have 40 frames to render, and we create 5 frames chunk, this means we need to ask Slurm to create a job array of `40/5=8` jobs.

Launch the array of jobs:

```
sbatch --array=1-8 /home/blender_job.job
```

If all goes well, using `squeue` command, you should be able to see the jobs currently running, and the ones currently pending for resources.

You can follow jobs by watching their job file (refreshed by Slurm regularly).
And after few seconds/minutes depending of your hardware, you should see first animation frames as PNG images in /home folder.

![Animation](resources/animation.gif)

This example shows how to use Slurm to create a Blender render farm.
