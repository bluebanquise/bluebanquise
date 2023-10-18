# User environment

This practical session is focused on understanding and setting a user environment for HPC usage.

This is an introduction, to provide you main guidelines.

## SSH

We need a secure way to reach a remote system and interact with it (shell and data). Ssh allows secured authentication and data transfer between client an server.

### Keys

In order to ssh to a remote cluster, it is key to understand the concept of public key cryptography. Please read the concept of keys at https://en.wikipedia.org/wiki/Public-key_cryptography 
It is important to understand difference between asymmetric and symmetric cryptography.

Once understood, on your local system, generate a new ssh key pair using:

```
ssh-keygen -t ed25519
```

And press enter multiple time to answer all questions and also do not provide a passphrase for now.
The passphrase is useful later to protect your key from being easily stolen by someone.

Once generated, you should have on your local system 2 new files in your $HOME/.ssh/ folder: id_ed25519 and id_ed25519.pub. The first file is your private key, that you MUST keep secure and not shared with anyone. The second file is the public key, that can be shared. It is also the public key that we will register on the remote ssh server to be able to login without password.

Get content of the public key file, and keep it somewhere:

```
cat $HOME/.ssh/id_ed25519.pub
```

ssh on your remote system, using password, and once logged, create .ssh folder if not existing, and add key into authorized_keys file into this folder:

```
mkdir -p $HOME/.ssh/
vi $HOME/.ssh/authorized_keys  # Copy past content of id_ed25519.pub in the file at this step
chmod 600 $HOME/.ssh/authorized_keys
```

Then exit, and try to login again. You should now be able to login without password, using only your private key. You can see the authentication exchange during ssh connection by adding -vvv.

### Port forwarding

SSH allows port forwarding. Its an effective feature to "link" distant port to your local system, and be able to reach an external server (http or anything else) from your local system.
It is also an efficient way to bypass some network restrictions or start a socks 5 proxy. Please keep in mind that badly used, ssh port forwarding can lead to serious security issues!

To test this feature, on a remote system, start a web browser with a custom page, on port 8888, in a dedicated shell:

```
sudo apt-get install python3 -y
echo "Hello from my remote server!" > index.html
python3 -m http.server 8888
```

Now, open another shell on your local system, and ssh on the remote system binding your local port 8080 to the distant port 8888:

```
ssh my_user@my_server -L 8080:localhost:8888
```

And let this shell alive.

Now, on your local web browser, if you connect to your local host, on port 8080 (http://localhost:8080), you should see the web page.

This port forwarding can also be used in reverse (be extra careful regarding security when using reverse !!!) or using -D to open a socks 5 proxy (extremely useful to be used as a proxy for web browsers). Port forwarding allows to bypass many firewalls restrictions, but to be used with extreme care.

## Linux environment

It is important as parallel developer, HPC clusters users, and system administrators to master basic Linux environment. A nice training can be found here, and it should only take around 10-15 min.

https://networking.ringofsaturn.com/Unix/learnUNIXin10minutes.php

## Bash basics

Bash basics are important to know how to create simple scripts to manipulate data, automate tasks, etc.
An interesting tutorial can be found at https://www.learnshell.org . You should at least do the Basics section for now. Advanced usages can be seen later when needed.

## Vim

Vim is one of the most popular tools to edit text files on remote systems. Prefer Vim to Vi, as Vim is way easier to manipulate and use in day to day usage.

Install the tool:

```
sudo apt-get install vim -y
```

And follow the online tutorial to learn how to use basic vim: https://www.openvim.com/

Note that while the tutorial advertise usage of hjku keys to navigate, you can use standard arrows on the keyboard.

Note also that while it seem a difficult to use editor at first sight, after few usages it should become easier, and even mandatory once mastered, since the tool offer so much features.

## Scripting

Bash scripting is a mandatory knowledge to manipulate distant Linux systems.

### Hello

Lets create a simple script. Create file hello with the following content:

```bash
#!/usr/bin/env bash
echo "Hello world!"
```

And make it executable:

```
chmod +x hello
```

Now, if you execute it, you should see the message "Hello world!".

### Calculator

A second example is to make a basic interactive calculator.

```bash
#!/usr/bin/env bash

echo "Please enter operation to perform (like 4+3 or 2*4):"
read operation
echo "You requested to perform $operation calculation."
eval echo Result is: $(($operation))
```

Make it executable and test it. Note that eval allows to evaluate a line before executing it.

### Loops and arrays

```bash
#!/usr/bin/env bash

a=(1 2 3 4 5)
b=(6 7 8 9 10)

for (( i=0; i<5; i++ ))
do
        c[$i]=$((a[i] + b[i]))
done

echo ${c[@]}
```

### Pipes

Pipes are useful to accumulate commands on the output and filter it.

For example:

```bash
echo -e "Hello\nthis is\na message\nfor you" | grep -v Hello | sed 's/message/note/' | grep "^a" | awk -F ' ' '{print $2}'
```

Try adding the commands from the left to right one by one and execute it each time, to visualize the progress of filtering.

###

Colors allow you to create nice scripts output, or simply show Errors/Warnings more effectively.

You can copy and past the following commands to see the effect on output. Note that not all shells support all features.

```bash
echo -e "\e[1mBold Text\e[0m"
echo -e "\e[4mUnderlined Text\e[0m"
echo -e "\e[31mRed Text\e[0m"
echo -e "\e[42mGreen Background\e[0m"
echo -e "\e[5mBlinking Text\e[0m"
```

For more details on colors, you can refer to https://www.shellhacks.com/bash-colors/

## Modules

Modules can be loaded using Lmod tool.

Install Lmod:

```
sudo apt-get install lmod -y
```

Environment Modules are useful to load environment variables, and unload them for a specific library or software made available to users. They are also efficient at loading dependencies needed for a specific element.

You need to source lmod to activate it:

```
source /usr/share/lmod/lmod/init/bash
```

This can be added in .bashrc file for auto sourcing at user logging.

Create 2 naive example tools, 1 needing the other one to run.
Create first file basic_tool_1 in folder /tmp/basic_tools/bin (you will need to create this folder) with the following content:

```bash
#!/usr/bin/env bash
echo Value is 4
```

And make it executable:

```bash
chmod +x /tmp/basic_tools/basic_tool_1
```

Then create another tool, that needs the first one to run. Create folder /tmp/advanced_tools/ and add in this folder file advanced_tool_1 with the following content:

```bash
#!/usr/bin/env bash
initial_value=$(basic_tool_1 | awk -F ' ' '{print $3}')
echo Final value is $((4 * initial_value))
```

If you execute now basic_tool_1, you can see it will work. However, advanced_tool_1 will fail: /tmp/`advanced_tools/advanced_tool_1: line 2: basic_tool_1: command not found`.

Lets create 2 modules files, one for our first tool first.
Create folder and file for basic tools:

```
mkdir $HOME/.modules/basic_tools/ -p
vi $HOME/.modules/basic_tools/1.0.0.lua
```

And add the following content to file:

```lua
help([[
"Our basic tools"
]])
prepend_path("PATH", "/tmp/basic_tools/")
```

Then create advanced tools folder and file:

```
mkdir $HOME/.modules/advanced_tools/ -p
vi $HOME/.modules/advanced_tools/1.0.0.lua
```

And add the following content to file:

```
help([[
"Our advanced tools"
]])
prepend_path("PATH", "/tmp/advanced_tools/")
load("basic_tools")
```

Now, add this module tree to lmod environment variable so lmod can find it:

```
module use $HOME/.modules
```

You can now list modules:

```
$ module avail

-------------------------------------------------- /home/oxedions/.modules ---------------------------------------------------
   advanced_tools/1.0.0    basic_tools/1.0.0
```

You can also check that no modules are loaded for now using module list.

Load basic_tools module, and check if basic_tool_1 command is now available without having to use its full path:

```
module load basic_tools
basic_tool_1
```

You can now see using `module list` command that basic_tools is loaded.
You can also see that advanced_tool_1 is not available. Unload basic_tools module now:

```
module unload basic_tools
```

Now, lets load the advanced_tools module:

```
module load advanced_tools
```

You can see using `module list` command that Lmod loaded advanced_tools, but also its dependencies, so basic_tools.

Now, the command advanced_tool_1 is available and is functional.

```
~$ advanced_tool_1
Final value is 16
~$
```

For more details on how to create module files, please refer to official Lmod documentation: https://lmod.readthedocs.io/

## Slurm cluster

For this part of the training, we need a slurm cluster. We are going to configure a very minimal cluster, with a single node, that will act as both controller and worker.

### Install munge and generate a key

Install munge, that is used by slurm to authenticate between nodes, and generate its needed key.
Then start the service.

```
sudo apt-get install munge libmunge-dev libmunge2
sudo mungekey -f
sudo systemctl start munge
```

### Install Slurm

Now install slurm and configure it with a very minimal cluster.

```
sudo apt install slurmd slurmctld slurm-client
sudo mkdir /etc/slurm
sudo mkdir /var/log/slurm
sudo mkdir -p /var/spool/slurmd/StateSave
sudo chown -R slurm:slurm /var/log/slurm
sudo chown -R slurm:slurm /var/spool/slurmd
```

Now create a very minimal file in `/etc/slurm/slurm.conf` with the following content.
We will assume here that your node hostname is `mgt1`. You need to update it to your real node name for slurm to start. You can get your real node name using command `hostnamectl` (You nee the Static hostname)

```
# Documentation:
# https://slurm.schedmd.com/slurm.conf.html

## Controller
ClusterName=valhalla
ControlMachine=mgt1

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
NodeName=mgt1 Procs=2

## Partitions definition
PartitionName=all MaxTime=INFINITE State=UP Default=YES Nodes=mgt1
```

Then create file `/etc/slurm/cgroup.conf` with the following content:

```
CgroupAutomount=yes
ConstrainCores=yes
```

And start slurm controller and worker daemons:

```
sudo systemctl start slurmctld
sudo systemctl status slurmctld
sudo systemctl start slurmd
sudo systemctl status slurmd
```

Note that if you encounter any errors, you can try to launch these manually to get the exact error:

```
sudo slurmctld -D -vvvvvvv
```

or

```
sudo slurmd -D -vvvvvvv
```

You should now see the cluster using command `sinfo`.

### Submit jobs

#### Submitting without a script

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

#### Basic job script

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

#### Serial job

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

#### OpenMP job

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

#### MPI job

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
