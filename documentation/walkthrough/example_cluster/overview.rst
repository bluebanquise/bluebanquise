========
Overview
========

Before typing anything, let's meet the cluster we are going to build.

Cluster description
===================

The example cluster is made of 9 hosts and 3 networks:

* **mgt1**: the management server. 3 network interfaces: one on ``datacenter`` (to reach it from
  the outside, and its own way to the internet), one on ``net-admin`` (to deploy and manage the rest
  of the cluster), and one on ``net-bmc`` (to talk to the BMCs of the workers).
* **login**: the login node, where users connect and submit their jobs. 2 network interfaces: one on
  ``datacenter``, one on ``net-admin``. It is also the gateway of the cluster: hosts of
  ``net-admin`` reach the internet through it.
* **storage**: the NFS server. 1 network interface, on ``net-admin``.
* **c001** to **c004**: CPU compute workers (x86_64). 1 network interface on ``net-admin``, and a
  BMC (IPMI) on ``net-bmc``.
* **g001** to **g004**: GPU compute workers (arm64, with 4 Nvidia GPUs each). 1 network interface on
  ``net-admin``, and a BMC (Redfish) on ``net-bmc``.

And the networks:

* ``net-admin`` (``10.10.0.0/16``): the management network of the cluster. It carries DHCP, DNS,
  time, PXE, and it is the network Ansible uses to reach every host.
* ``net-bmc`` (``10.11.0.0/16``): a dedicated network for BMCs (IPMI and Redfish).
* ``datacenter`` (``192.168.0.0/24``): the existing network of the datacenter, managed by someone
  else. It gives access to mgt1 and login from the outside, and leads to the internet through the
  datacenter router, ``192.168.0.200``.

All hosts run RHEL 10 (or a compatible distribution, like Rocky Linux or AlmaLinux).

``[SCHEMA: example-cluster-topology]``
  *Three network clouds (net-admin 10.10.0.0/16, net-bmc 10.11.0.0/16, datacenter 192.168.0.0/24
  external), with the 9 hosts placed on the network(s) they belong to. An arrow through login shows
  net-admin traffic going out through datacenter's router (192.168.0.200), and a second, direct
  arrow from mgt1 to the same router. BMC leaf nodes hang off net-bmc for the 8 compute workers
  only (mgt1, login and storage have no BMC in this example).*

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
     - bmc-c001 .. bmc-c004, 10.11.3.1 .. 10.11.3.4 (IPMI)
   * - g001 .. g004
     - fn_compute_gpu
     - hw_gpu_worker
     - os_rhel_10
     - 10.10.3.101 .. 10.10.3.104
     - --
     - --
     - bmc-g001 .. bmc-g004, 10.11.3.101 .. 10.11.3.104 (Redfish)

.. note::

  Every host belongs to the 3 mandatory group types of the data model: a function group (``fn_*``),
  a hardware group (``hw_*``), and an OS group (``os_*``). See :doc:`../../configuration/groups`
  and :doc:`../../configuration/hosts` for the rules behind them.

Prerequisites
=============

Here is what we need before starting:

* mgt1 already runs RHEL 10, installed by hand, and we can reach it with SSH on the ``datacenter``
  network, with a user able to use sudo.
* mgt1 has internet access, through the datacenter router, to download BlueBanquise, the
  installation ISOs, and packages. If your cluster has no internet access at all, you can provide
  ISOs and repositories mirrors by hand instead: see :doc:`../../deployment/provision_os`.
* The other 8 hosts are racked, cabled to ``net-admin`` and ``net-bmc`` (and ``datacenter`` for
  login), and set to boot from the network first. They do not need an operating system yet: that is
  what we are going to give them.
* We know the MAC addresses of the ``net-admin`` interfaces and BMCs of all hosts. The examples use
  placeholder MAC addresses: replace them with yours.

Ready? Let's go!
