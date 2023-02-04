# Slurm (HPC cluster, render farm, etc)

Once BlueBanquise CORE has been deployed, it is possible to configure and
also deploy a **Slurm** infrastructure over the freshly created cluster.

Slurm is a job scheduler, used to share computational resources between users,
and ensure maximum usage of cluster. It is widly used in HPC field (High
Performance Computing) but is also very interesting for render farms like
Blender farms.

In the following documentation we are going to setup a cluster with a shared
space, basic users, and the Slurm job scheduler to allow users to share resources
(or if a single user, to easily stack jobs). As an example, we will install
Blender and render a nice 3D small video.

Users will launch jobs from the login node. Note that on very small clusters,
management node can also be used as the login node.

First, we need a shared folder between nodes.

## Shared folders

Two shared folders are required between all nodes: first one will store software,
and second one users /home so users data.

First one can be /opt/software, and for second one /home is a good candidate.

Use nfs_server/client CORE role to achieve that. Edit file
*group_vars/all/general_settings/nfs.yml* to the following:

	nfs_settings:
	  selinux:
	    use_nfs_home_dirs: true
	nfs:
	  softwares:
	    mount: /opt/software                        # Which path clients should mount this NFS
	    export: /opt/software                       # What path server should export
	    server: management1                         # The server that export this storage space
	    clients_groups:                             # Can be an equipment group, or a main group (mg), or any other ansible group
	      - mg_computes
	      - mg_logins
	    take_over_network: ice1-1                   # Network used to share this storage space
	    export_arguments: ro,no_root_squash,async   # Arguments for the server (export)
	    mount_arguments: ro,intr,nfsvers=4.2,bg     # Arguments for the client (mount)
	  home:
	    mount: /home
	    export: /home
	    server: management1
	    clients_groups:
	      - mg_computes
	      - mg_logins
	    take_over_network: ice1-1
	    export_arguments: rw,no_root_squash,sync
	    mount_arguments: rw,intr,rsize=32768,wsize=32768,nfsvers=4.2,bg

Basically, management1 node will export these folders, and nodes member of
groups *mg_computes* or *mg_logins* will mount it.

Create the folders to be exported on management1:

mkdir /opt/software
mkdir /home

Then deploy **nfs_server** role on management1 (assuming nfs_server role is
listed in management.yml playbook with tag *nfs_server*):

ansible-playbook /etc/bluebanquise/playbooks/management.yml -t nfs_server

And ensure management1 indeed export folders using showmount command:

showmount -e management1

Output should be:

>>>>>>>>>>>>>>>>>>>>>>>>

Now execute **nfs_client** role on all *mg_computes* and *mg_logins* nodes and
ensure folders are mounted:

ansible-playbook /etc/bluebanquise/playbooks/computes.yml -t nfs_client
ansible-playbook /etc/bluebanquise/playbooks/logins.yml -t nfs_client

Ensure it is mounted on one node. For example, on login1 node, check using:

df -h

And output should contain:

>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Now that we have a shared storage, we need a user to launch jobs.
