========
Overview
========

This walkthrough builds one complete, realistic cluster from nothing to a working Slurm job,
referencing back to the relevant sections of this documentation at each step instead of
re-explaining every variable from scratch.

Cluster description
====================

The example cluster is made of 9 hosts and 3 networks:

* **mgt1**: the management server. 3 NICs: one on ``datacenter`` (used for maintenance access
  to the cluster), one on ``net-admin`` (provisions the rest of the cluster), one on ``net-bmc``
  (BMC management).
* **login**: the login/submission node. 2 NICs: one on ``datacenter``, one on ``net-admin``. It
  also acts as the router between the two, masquerading ``net-admin`` traffic out to the internet
  reachable from ``datacenter``.
* **storage**: the NFS server. 1 NIC, on ``net-admin``.
* **c001** to **c004**: CPU compute workers. 1 NIC on ``net-admin``, plus a BMC (IPMI) on
  ``net-bmc``.
* **g001** to **g004**: GPU compute workers. 1 NIC on ``net-admin``, plus a BMC (Redfish) on
  ``net-bmc``.

Networks:

* ``net-admin`` (``10.10.0.0/16``): the cluster's management network. Carries DHCP, DNS, NTP,
  PXE, and is the network Ansible uses to reach every host.
* ``net-bmc`` (``10.11.0.0/16``): dedicated network for BMC (IPMI/Redfish) access.
* ``datacenter`` (``192.168.0.0/24``): externally managed network, used for maintenance access
  to mgt1 and login, and as login's route to the internet (gateway ``192.168.0.200``).

``[SCHEMA: example-cluster-topology]``
  *Three network clouds (net-admin 10.10.0.0/16, net-bmc 10.11.0.0/16, datacenter
  192.168.0.0/24 external), with the 9 hosts placed on the network(s) they belong to. An arrow
  through login shows masquerade from net-admin out through datacenter's gateway
  (192.168.0.200). BMC leaf nodes hang off net-bmc for the 8 compute workers only (mgt1, login
  and storage have no BMC in this example).*

Hosts summary
=============

.. list-table::
   :header-rows: 1

   * - Host
     - Function group
     - Hardware group
     - OS group
     - net-admin
     - datacenter
     - net-bmc
     - BMC
   * - mgt1
     - fn_management
     - hw_server
     - os_rhel_10
     - 10.10.0.1
     - 192.168.0.1
     - 10.11.0.1
     - none
   * - login
     - fn_login
     - hw_server
     - os_rhel_10
     - 10.10.2.1
     - 192.168.0.2
     - --
     - none
   * - storage
     - fn_storage
     - hw_server
     - os_rhel_10
     - 10.10.1.1
     - --
     - --
     - none
   * - c001 .. c004
     - fn_compute
     - hw_cpu_worker
     - os_rhel_10
     - 10.10.3.1 .. 10.10.3.4
     - --
     - --
     - bmc-c001 .. bmc-c004 @ 10.11.3.1 .. 10.11.3.4 (IPMI)
   * - g001 .. g004
     - fn_compute_gpu
     - hw_gpu_worker
     - os_rhel_10
     - 10.10.3.101 .. 10.10.3.104
     - --
     - --
     - bmc-g001 .. bmc-g004 @ 10.11.3.101 .. 10.11.3.104 (Redfish)

.. note::

  Every host also carries the 3 mandatory group types described in the data model: a function
  group (``fn_*``), a hardware group (``hw_*``), and an OS group (``os_*``). See the
  :doc:`groups <../../configuration/groups>` and :doc:`hosts <../../configuration/hosts>`
  sections of this documentation for the underlying rules.

Prerequisites
=============

* mgt1 already has an operating system installed (RHEL 10) and is reachable over SSH from your
  workstation on the ``datacenter`` network, with a sudo-capable user.
* mgt1 has internet access (directly, or through a proxy) to reach BlueBanquise's public
  repository and download the ``curl`` bootstrap script. If your cluster is air-gapped, see the
  ``pxe_stack`` role documentation for offline alternatives.
* The other 8 hosts (login, storage, c001-004, g001-004) are racked, cabled to ``net-admin`` and
  ``net-bmc``, and configured to PXE boot first in their boot order. They do not need an
  operating system yet - that is what this walkthrough deploys for them.
* You know (or will fill in once known) the MAC addresses of the ``net-admin`` and BMC
  interfaces of every host - the inventory examples below use placeholder MAC addresses.
