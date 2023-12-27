# Slurm (HPC cluster, render farm, etc)

Once BlueBanquise CORE has been deployed, it is possible to configure and
also deploy a **Slurm** infrastructure over the freshly created cluster.

Slurm is a job scheduler, used to share computational resources between users,
and ensure maximum usage of cluster. It is widely used in HPC field (High
Performance Computing) but is also very interesting for render farms like
Blender farms.

In the following documentation we are going to setup a cluster with a shared
space, basic users, and the Slurm job scheduler to allow users to share resources
(or if a single user, to easily stack jobs). As an example, we will install
Blender and render a nice 3D small video.

Users will launch jobs from the login node. Note that on very small clusters,
management node can also be used as the login node.

We will assume from this point that all nodes share a shared /opt/software to
store software and libraries, and /home to store users files.
We will also assume that users are present on all systems, even management node,
using method of your choice (users_basic role, LDAP, script, etc.).

This part of the documentation is focused on Slurm configuration and deployment.

##
