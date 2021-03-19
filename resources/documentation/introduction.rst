============
Introduction
============

**BlueBanquise** is a generic stack, based on Ansible, whose purpose is to
deploy and manage clusters of hosts.
These clusters can be from few workstations in enterprise to very large HPC or
servers farm clusters.

**BlueBanquise** is the result of a need. A need for a very simple task, not
based on multi languages scripts difficult to maintain, that can keep simplicity
while managing very complex architecture.

Ansible was chosen for its simplicity and its security.
The Ansible inventory groups/variables mechanism can cover from very simple to
very sophisticated configurations. Ansible is not the fastest tool, nor the
simplest to debug. However, it is easy to learn, and widely used today with an
active community.

The **BlueBanquise** stack is made of two main parts:

* The CORE, aimed to deploy operating system and base services on hosts
* The COMMUNITY, aimed to provide specialized features over the core (HPC, containers farm, etc.)

This documentation is structured as the following:

* Few basic vocabulary
* An Ansible training
* Few words on how to test the stack into containers
* Procedure to install BlueBanquise [CORE]
    * Install first management
    * Configure BlueBanquise
    * Deploy BlueBanquise
    * (Optional) Deploy diskless nodes
    * (Optional) Deploy a multi icebergs cluster
* Procedures to specialize the cluster using BlueBanquise [COMMUNITY] roles
    * Deploy Prometheus (Monitoring your cluster)
    * Deploy Slurm (Specialize your cluster for High Performance Computing)
    * Deploy Nomad and Consul (Deploy containers orchestration on the cluster)

If you encounter any bugs/issues or have any comments, please inform us.

We hope you will enjoy this stack as much as we do.
