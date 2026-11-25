=================
High Availability
=================

On a cluster, management hosts are precious: if the only one providing DHCP, DNS or repositories
goes down, hosts cannot boot, resolve names, or install packages anymore. High availability (often
shortened HA) means making these services survive the loss of a management host, by running them on
several hosts able to take over for each other.

This page presents the tools the stack provides, and a strategy to combine them, based on real life
experience. It is not the only possible one, so feel free to adapt it to your needs!

The tools
=========

Four roles work together:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Role
     - What it brings
   * - ``keepalived``
     - Floating virtual IP addresses (VRRP). A virtual IP lives on one host, and moves to another
       host if the first one fails. Clients always use the virtual IP, wherever it currently is.
   * - ``haproxy``
     - Load balancing: spreads requests (HTTP repositories, for example) over the services running
       on all management hosts, and stops sending requests to a host that does not answer.
   * - ``pcs``
     - A full HA cluster, based on Corosync (membership and quorum) and Pacemaker (resources
       management). Pacemaker starts each resource (a service, a file system, a virtual IP) on one
       host, monitors it, and moves it elsewhere on failure, respecting the order and colocation
       constraints you define.
   * - ``drbd``
     - Block devices replicated over the network between hosts: a kind of network RAID 1, giving
       management hosts a shared storage without a storage bay.

``[SCHEMA: ha-building-blocks]``
  *Three management hosts side by side. Above them, a virtual IP bubble (keepalived) that can jump
  from one host to another; an haproxy box spreading arrows to the three hosts; below them, a DRBD
  volume replicated between two hosts; around everything, a dashed Pacemaker/Corosync frame with a
  "resource group" (file system + service + virtual IP) shown active on one host and greyed on the
  others.*

Two families of services
========================

When thinking about HA, services fall into two families, and each one has its own simple recipe.

**Stateless services** behave the same on all hosts, and keep no important data: DNS (all servers
get the same zones from the inventory), repositories (identical copies), time. They can run on all
management hosts at the same time. We only need clients to always find a living one:

* a virtual IP managed by ``keepalived``,
* optionally, ``haproxy`` behind it, to spread the load over all hosts.

**Stateful services** have data that must stay consistent: the PXE host files written by
``bluebanquise-bootset`` and the PXE stack daemon, centralized logs, databases. They must run on a
single host at a time, with their data on a storage reachable by all candidates. This is the job of
``pcs``: it mounts the shared storage (NFS bay, or ``drbd`` volume), starts the service and its
virtual IP on one host, and moves the whole group elsewhere if this host fails.

.. note::

  The DHCP server is a special case: all servers get the same host reservations from the inventory,
  so it can simply run on all management hosts, or be managed by ``pcs`` without virtual IP. See the
  **pcs** role documentation for ready to use resources definitions.

Let the HA manager start services
=================================

By default, roles start and enable the services they configure. Under ``pcs``, it is Pacemaker, not
systemd, that decides where a stateful service runs: if systemd also starts it at boot, the service
runs twice, which is exactly what we want to avoid.

So on HA management hosts, we ask roles to configure services without starting nor enabling them:

.. code-block:: yaml

  bb_start_services: false
  bb_enable_services: false

and let Pacemaker do the rest. Each role also has its own ``<role>_start_services`` and
``<role>_enable_services`` variables, to keep some services (stateless ones, like ``time``) managed
by systemd as usual:

.. code-block:: yaml

  bb_start_services: false
  bb_enable_services: false
  time_start_services: true
  time_enable_services: true
  pcs_start_services: true
  pcs_enable_services: true

A recipe
========

Here is a strategy that works well for a cluster of a few thousand hosts:

#. **Several management hosts**, in the same management network, for example one per herd of 500
   hosts (see :doc:`scalability`).
#. **A shared storage**: an NFS storage bay with hardware redundancy, or DRBD volumes replicated
   between management hosts (``drbd`` role).
#. **Stateless services everywhere**: DNS and repositories run on all management hosts, behind
   virtual IPs managed by ``keepalived``, and if needed load balanced by ``haproxy``.
#. **Stateful services under Pacemaker**: PXE files and HTTP server, logs server, databases, as
   ``pcs`` resource groups, with their file system and virtual IP.
#. **Services endpoints on virtual IPs**: in the networks definition, ``dns4``, ``pxe4``,
   ``repositories4``, ``log4`` and ``ntp4`` point to the virtual IPs, so hosts never need to know
   which management host currently serves them (see :doc:`../configuration/services`).
#. **Fencing**: a production HA cluster needs STONITH, so a host that stopped answering is really
   powered off before its resources move. Configure it using the BMCs of management hosts (see
   the **pcs** role documentation).

Deploy it step by step: configure services on the first management host only, with
``bb_start_services: true`` for this run, check everything works, then deploy the HA cluster on all
management hosts. The **pcs** role documentation details this sequence, with playbook examples, and
a list of standard resources for the BlueBanquise services.

.. warning::

  HA brings its own complexity: a misconfigured HA cluster can cause more downtime than it prevents.
  Take the time to test failovers (stop a service, power off a host) before going to production,
  and document them for your team.

Here is the detailed documentation of the HA cluster manager. The ``keepalived``, ``haproxy`` and
``drbd`` roles are documented with other services, in :doc:`../configuration/services`.

.. toctree::
   :maxdepth: 1
   :caption: High availability:

   high_availability/pcs
