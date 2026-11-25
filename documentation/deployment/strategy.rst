========
Strategy
========

Deploying a cluster can feel intimidating the first time: so many hosts, services and settings!
The trick is to go step by step, in an order where each step relies only on what previous steps
already built. This page gives you that order, and the logic behind it, so you always know where
you are and what comes next.

The big picture
===============

A BlueBanquise cluster is built from a single place, the management host. From there, we describe
the cluster in an inventory, then let Ansible turn this description into reality, first on the
management host itself, then on all other hosts.

.. list-table::
   :header-rows: 1
   :widths: 5 30 65

   * - Step
     - What
     - Why now
   * - 1
     - Install the management host operating system, by hand
     - Someone has to start! This is the only host we install manually.
   * - 2
     - Bootstrap BlueBanquise on it
     - Ansible, the BlueBanquise collection and the ``bluebanquise`` user are needed to do anything
       else.
   * - 3
     - Write the inventory
     - Networks, hosts, groups, hardware and operating systems: everything roles need to know.
   * - 4
     - Configure the management host
     - Its network, repositories, firewall, and the services other hosts need to be installed:
       DHCP, DNS, HTTP, PXE, time.
   * - 5
     - Provision other hosts operating system, through the network
     - Hosts boot over PXE, install, and come back reachable with SSH.
   * - 6
     - Apply configuration on other hosts
     - Network, repositories, firewall, time, DNS client... the common base of all hosts.
   * - 7
     - Specialise the cluster
     - Shared storage, users, job scheduler, monitoring, logs: what makes your cluster yours.
   * - 8
     - Live with it
     - Add hosts, update settings, redeploy, monitor: the day to day life of the cluster.

``[SCHEMA: deployment-strategy]``
  *A horizontal timeline of the 8 steps above, with icons: a hand installing the management host
  (1), the bluebanquise logo (2), a notebook for the inventory (3), the management host lighting up
  its services (4), arrows spreading from it to empty hosts (5), the same hosts turning green (6),
  extra badges added on them (storage, scheduler, monitoring) (7), and a loop arrow back to the
  inventory (8).*

Let's walk through each step.

1. The management host
======================

The management host (or hosts, on larger clusters) is the heart of the cluster: it holds the
inventory, runs Ansible, and provides the services needed to deploy and run all other hosts.
Install it with one of the supported distributions: RHEL 9 or 10 (and compatible), Ubuntu 24.04 or
26.04, Debian 13, or OpenSuse Leap 16. It can be a physical server, or a virtual machine.

Give it access to the management network of the cluster, and, at least during the installation, to
the internet (or to local mirrors of the distribution and BlueBanquise repositories).

2. Bootstrap
============

The bootstrap script installs Ansible and BlueBanquise on the management host, and creates the
``bluebanquise`` user. See :doc:`../introduction/installation`, or the first part of
:doc:`provision_os`.

3. The inventory
================

This is where you will spend most of your thinking time, and it is time well spent: a good inventory
makes everything else simple. The General configuration section of this documentation goes through
it in order: :doc:`../configuration/inventories`, :doc:`../configuration/general_settings`,
:doc:`../configuration/networks`, :doc:`../configuration/hosts`, :doc:`../configuration/groups`,
:doc:`../configuration/os_settings`, :doc:`../configuration/hardware_settings`.

You do not need to get everything right the first time: the inventory will grow with the cluster.
Start with networks, hosts and groups, and add services settings when you need them.

4. Configure the management host
================================

Before it can deploy anything, the management host needs to provide a few services to its future
clients:

* **DHCP**, so hosts get an address and know where to boot from (``dhcp_server``).
* **HTTP** and **TFTP**, to serve boot files, installation media and repositories (``http_server``,
  ``pxe_stack``).
* **DNS**, so hosts find each other by name (``dns_server``).
* **Time**, so all clocks agree (``time``).

And of course its own base: network interfaces (``nic``), repositories (``repositories``), firewall
(``firewall``), hosts file (``hosts_file``), system settings (``local_configuration``). See
:doc:`provision_os`.

5. Provision hosts
==================

With the management host ready, we provide the installation media of each distribution to deploy,
mark hosts for deployment with ``bluebanquise-bootset``, and power them on. They install
themselves, unattended, following the inventory. See :doc:`provision_os`.

6. Apply configuration
======================

Once hosts are installed, we write one playbook per kind of host (per function group), and run them.
See :doc:`apply_configuration`.

7. Specialise
=============

This is where the cluster becomes yours: an HPC cluster gets Slurm, an interconnect and shared
storage (see :doc:`../specialisation/hpc_cluster`), most clusters get shared storage
(:doc:`../configuration/storage`), users (``users`` role), monitoring and centralized logs
(:doc:`../configuration/services`). Add these one at a time, checking each works before moving to
the next: it is much easier to find what went wrong when only one thing changed.

8. Live with the cluster
========================

A cluster is never finished: hosts are added, replaced, updated. The routine stays the same:

#. Update the inventory (and commit it, if you keep it in git).
#. Re-run the playbooks of the hosts concerned, including the management host when hosts or
   networks changed.
#. Redeploy hosts if needed, with ``bluebanquise-bootset``.

:doc:`../operations/operations` gathers the day to day tools: powering hosts on and off, reaching
their console, running commands on many hosts at once, monitoring and logs.

A few tips from experience
==========================

* **Start small.** Deploy one host of each kind first, check it is fine, then deploy all others.
  ``--limit`` is your friend (see :doc:`apply_configuration`).
* **Keep the inventory in git.** You will always know what changed, and when.
* **Run twice.** A second run of a playbook should change nothing. If it does, something is not
  stable, and it is better to know it early.
* **Read the error.** Roles try hard to explain what is wrong and how to fix it, especially for
  common situations (firewall not running, missing variable...).
* **Ask for help.** The community is friendly: do not hesitate to open an issue or a discussion on
  `GitHub <https://github.com/bluebanquise/bluebanquise>`_.
