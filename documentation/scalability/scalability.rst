===========
Scalability
===========

A single management host comfortably handles a few hundred hosts. Beyond that, or when the cluster
must keep running even if a management host fails, we need to spread the work over several
management hosts.

BlueBanquise offers two ways to do so, which can be combined:

* **Vertical scalability**, with *icebergs*: the cluster is split into autonomous parts, each with
  its own management network and management hosts, organized in a hierarchy.
* **Horizontal scalability**, with *herds*: the cluster keeps a single flat management network,
  and several management hosts share the services, each one taking care of a part of the hosts.

There is no single right answer: icebergs fit clusters made of physically separated parts (several
rooms, buildings, or isolated groups of racks), while herds fit clusters where all hosts share the
same network, and where high availability matters. Let's look at both.

.. note::

  Both rely on the same simple mechanism: Ansible groups, and the ``bb_restrict_to_group`` global
  variable (see :doc:`../configuration/general_settings`), which makes roles take into account only
  the hosts of a given group.

Vertical scalability: icebergs
==============================

The cluster is organized in a pyramidal shape. Instead of a single flat network, it is split into
icebergs (also called *islands* in the HPC world): small, autonomous clusters, each with its own
management network subnet, its own management hosts, and its own hosts.

.. image:: ../images/multiple_icebergs.svg
   :align: center

.. note::

  All icebergs can still share the same interconnect or high speed network: only management
  networks are split.

Icebergs are linked in a hierarchy. The *top* iceberg provides services to the management hosts of
the icebergs below it, which in turn provide services to their own hosts. For example, time flows
from the top iceberg management host, to each iceberg management host, to all hosts of each
iceberg. Management hosts of a lower iceberg are therefore connected to two networks: their own
iceberg management network, and the management network of the iceberg above.

``[SCHEMA: icebergs-hierarchy]``
  *A top iceberg (iceberg1, with mgt1 on net-ice1) above three icebergs (iceberg2, 3 and 4, each
  with its management host on both net-ice1 and its own net-iceX, and its own hosts below). Arrows
  show services chaining: time and repositories from mgt1 to each iceberg management host, then to
  their hosts. A shared interconnect bar runs below all icebergs.*

Groups
------

Each iceberg is an Ansible group, named ``iceberg`` followed by its number, and holding the
management hosts and the hosts of the iceberg:

.. code-block:: ini

  [iceberg1]
  mgt1

  [iceberg2]
  mgt2
  c[001:100]

  [iceberg3]
  mgt3
  c[101:200]

As with any group, iceberg specific settings go in ``group_vars/iceberg2/``, and so on.

.. warning::

  ``hw_`` and ``os_`` prefixed variables must never be set in iceberg groups: all hosts of an
  equipment profile must share the same values (see :doc:`../configuration/groups`).

Networks
--------

Each iceberg gets its own management network. Their names must still start with ``net-``, as this
prefix is how roles recognize management networks:

.. code-block:: yaml

  networks:
    net-ice1:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1     # mgt1
    net-ice2:
      subnet: 10.12.0.0
      prefix: 16
      services_ip: 10.12.0.1     # mgt2
    net-ice3:
      subnet: 10.13.0.0
      prefix: 16
      services_ip: 10.13.0.1     # mgt3

Hosts of each iceberg are connected to their iceberg network, and find their services there. ``mgt2``
has a first interface on ``net-ice2`` (its own iceberg), and a second one on ``net-ice1``, to reach
``mgt1``.

Restrict each iceberg to its hosts
----------------------------------

Management hosts of an iceberg must only serve their own hosts: ``mgt2`` must not answer DHCP
requests of ``iceberg3`` hosts, nor generate their PXE files. In ``group_vars/iceberg2/``:

.. code-block:: yaml

  bb_restrict_to_group: iceberg2

Roles registering hosts (``dhcp_server``, ``dns_server``, ``hosts_file``, ``pxe_stack``, ``conman``,
``powerman``, ``bluebanquise_power``, ``ssh_client``) then only take into account the members of
``iceberg2``. Each of them also has its own ``<role>_restrict_to_group`` variable, taking precedence:
for example, to keep all hosts of the cluster in hosts files and DNS, so any host can reach any other
host by its name:

.. code-block:: yaml

  bb_restrict_to_group: iceberg2
  hosts_file_restrict_to_group: all
  dns_server_restrict_to_group: all

Chain services
--------------

Lower iceberg management hosts get their own services from the iceberg above. For time, their time
server uses the top iceberg time server as source, in ``group_vars/iceberg2/``:

.. code-block:: yaml

  bb_iceberg_level: 2

and, for ``mgt2`` only (``host_vars/mgt2/``), as only the management host is a time server:

.. code-block:: yaml

  time_external_servers:
    - 10.10.0.1

``bb_iceberg_level`` lowers the stratum a time server announces when it lost its source, so the
hierarchy stays consistent. Repositories can be chained the same way: the management host of each
iceberg mirrors the repositories of the top iceberg, and serves them to its hosts.

Deploy
------

The inventory stays unique, and Ansible runs from the top management host, which reaches lower
iceberg management hosts through ``net-ice1``. Lower icebergs are then deployed from their own
management host, or from the top one if it can reach all networks. Use ``--limit iceberg2`` to work
on one iceberg at a time.

Horizontal scalability: herds
=============================

Here, the cluster keeps a single, flat management network. We add management hosts, and split the
hosts into *herds*: logical groups of hosts, each one taken care of by one management host. A herd
of 500 to 600 hosts is a reasonable size for a single management host.

For example, 2000 hosts make 4 herds, so 4 management hosts. And since several management hosts
are now available, we use them to make services highly available: if one fails, another one takes
over.

``[SCHEMA: herds-and-ha]``
  *One flat net-admin network with 4 management hosts on top (mgt1 to mgt4) sharing virtual IPs
  (keepalived) and a shared storage (NFS bay or DRBD), and 4 herds of hosts below (herd1 to herd4),
  each linked by a thicker line to "its" management host for consoles, power and monitoring, while
  all hosts reach DHCP, DNS, time and repositories through the virtual IPs.*

Herds
-----

Each herd is a group:

.. code-block:: ini

  [herd1]
  c[0001:0500]

  [herd2]
  c[0501:1000]

Then, each management host runs the services that work *towards* hosts only for its own herd:
consoles (``conman``), power (``powerman``, ``bluebanquise_power``), and Ansible runs themselves. For
``mgt1``, in ``host_vars/mgt1/``:

.. code-block:: yaml

  conman_restrict_to_group: herd1
  powerman_restrict_to_group: herd1
  bluebanquise_power_restrict_to_group: herd1

And configuration is applied to each herd from its management host, to spread the load:

.. code-block:: bash

  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --limit herd1

Shared services
---------------

Services that hosts *reach* (DHCP, DNS, time, repositories, PXE, logs) are published on virtual IP
addresses, shared by all management hosts. Hosts find them through the services endpoints of the
network (see :doc:`../configuration/services`):

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services:
        dns4:
          - ip4: 10.10.0.10
        ntp4:
          - ip4: 10.10.0.11
        pxe4:
          - ip4: 10.10.0.12
        repositories4:
          - ip4: 10.10.0.12
        log4:
          - ip4: 10.10.0.13

These virtual IPs, and the services behind them, are managed by the high availability tools
described in :doc:`high_availability`:

* Stateless services, identical on all management hosts (repositories, DNS), can run everywhere,
  behind a virtual IP managed by ``keepalived``, possibly load balanced by ``haproxy``.
* Stateful services (the PXE host files, logs) run on one management host at a time, with their
  data on a shared storage (an NFS storage bay, or ``drbd`` replicated volumes), and move to another
  management host on failure, driven by ``pcs`` (Pacemaker and Corosync).

.. note::

  The storage shared by management hosts is a critical part of this design: choose it with care,
  with hardware redundancy.

Combine both
============

Nothing prevents using herds inside an iceberg, or making the management hosts of each iceberg
highly available: groups simply stack. Start simple, and grow when you need it: a single management
host is perfectly fine for most clusters!
