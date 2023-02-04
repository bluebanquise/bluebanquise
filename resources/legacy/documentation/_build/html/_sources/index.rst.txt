BlueBanquise Documentation
==========================

.. image:: images/BlueBanquise_logo.svg
   :align: center

Welcome on BlueBanquise main documentation. You should find here all needed 
information on how to deploy and use the BlueBanquise stack.

Since one of the main BlueBanquise goals is also to be a training for new Linux system 
administrators, part of the documentation is generic knowledge and act 
as a tutorial for basic cluster deployment and basic Ansible usage. Advanced users 
can skip these parts.

These pages contain information on:

* How to manually deploy a test HPC cluster (generic knowledge, not related to the stack)
* How to use Ansible (generic knowledge, not related to the stack)
* How to bootstrap, configure, deploy and maintain BlueBanquise on different scenario clusters
* Detailed documentation on each roles provided with the stack

`Please report us <https://github.com/bluebanquise/bluebanquise/issues>`_ any
issues in this documentation.

Please proceed to :ref:`Introduction` to start.

>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
A FAIRE:
ipv6
HA + Haproxy
slurm
sys admin tuto
advanced nic_nmcli examples
git gitea


------------

.. toctree::
   :maxdepth: 3
   :caption: Contents:
   :numbered:

   introduction
   vocabulary
   training_sysadmin
   training_ansible
   bootstrap
   configure_bluebanquise
   deploy_bluebanquise
   multiple_icebergs
   diskless
   high_availability
   monitoring
   slurm
   containers
   stories
   roles
   references

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

------------

Documentation authors:

* LEVEUGLE Benoît
* KEATS Johnny
* TRAVOUILLON Bruno
* GELLNER Tim
* RIBEIRO Adrien
* MERZOUKI Hamid
* PEROTIN Matthieu
* PIETERS David
