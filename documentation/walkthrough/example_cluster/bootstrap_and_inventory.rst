=============================
Core: bootstrap and inventory
=============================

This page builds the inventory for the cluster's core: networking, hosts, hardware/OS
definitions, repositories, and firewall. It deliberately leaves out NFS, standard users, and
Slurm - those are added afterwards, once the core cluster is up and reachable, in
:doc:`extensions`.

Bootstrap BlueBanquise on mgt1
===============================

SSH to mgt1 on its ``datacenter`` address, then bootstrap it:

.. code-block:: bash

  curl -o online_bootstrap.sh https://raw.githubusercontent.com/bluebanquise/bluebanquise/master/bootstrap/online_bootstrap.sh
  chmod +x online_bootstrap.sh
  sudo ./online_bootstrap.sh

This creates the ``bluebanquise`` user (home ``/var/lib/bluebanquise``), a Python virtual
environment with Ansible installed, and an SSH key pair for that user. Switch to it for
everything that follows:

.. code-block:: bash

  sudo su - bluebanquise
  ansible-playbook --version

See :doc:`../../introduction/installation` for details on what the bootstrap script does.

Inventory skeleton
===================

.. code-block:: bash

  mkdir -p /var/lib/bluebanquise/inventories/example_cluster/group_vars/all
  mkdir -p /var/lib/bluebanquise/inventories/example_cluster/cluster
  cd /var/lib/bluebanquise/inventories/example_cluster

See :doc:`../../configuration/inventories` for the general inventory layout and precedence
rules this relies on.

Global settings
================

``group_vars/all/dns.yml``:

.. code-block:: yaml

  bb_domain_name: bluebanquise.example.local

``group_vars/all/time.yml``:

.. code-block:: yaml

  bb_time_zone: Europe/Brussels

See :doc:`../../configuration/general_settings`.

Networks
========

``group_vars/all/networks.yml``:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      gateway4: 10.10.2.1
      firewall_zone: internal
      services_ip: 10.10.0.1
    net-bmc:
      subnet: 10.11.0.0
      prefix: 16
      firewall_zone: internal
      services_ip: 10.11.0.1
    datacenter:
      subnet: 192.168.0.0
      prefix: 24
      firewall_zone: external

Notes:

* ``net-admin`` and ``net-bmc`` start with ``net-``, so they are management networks: DHCP, DNS
  and PXE are served on them by default. ``datacenter`` does not, so it is a plain network.
* ``services_ip`` collapses all service endpoints (DHCP, DNS, NTP, PXE, ...) for a network onto
  a single host - here, mgt1 for both management networks. See the *services endpoints* part of
  :doc:`../../configuration/services`.
* ``net-admin``'s ``gateway4`` is ``10.10.2.1``, i.e. **login**'s own address on that network:
  login is the router between ``net-admin`` and ``datacenter``. Every other host on
  ``net-admin`` (mgt1, storage, the workers) picks this up automatically as its default route.
* ``datacenter`` deliberately has **no** ``gateway4``. If it did, mgt1 (which also has an
  interface on ``datacenter``) would pick up a second, conflicting default route. Instead, the
  route to the internet (``192.168.0.200``) is set explicitly on login's own ``datacenter``
  interface only - see the hosts definitions below.
* Only ``net-admin`` and ``net-bmc`` are in the ``internal`` firewall zone; ``datacenter`` is
  ``external``. See the firewall section below.

See :doc:`../../configuration/networks`, and the
:doc:`dhcp_server <../../configuration/services/dhcp_server>` /
:doc:`dns_server <../../configuration/services/dns_server>` role sections of this documentation
for what else can be configured per network.

Groups
======

``cluster/fn`` (function groups):

.. code-block:: ini

  [fn_management]
  mgt1

  [fn_login]
  login

  [fn_storage]
  storage

  [fn_compute]
  c00[1:4]

  [fn_compute_gpu]
  g00[1:4]

``cluster/hw`` (hardware groups):

.. code-block:: ini

  [hw_server]
  mgt1
  login
  storage

  [hw_cpu_worker]
  c00[1:4]

  [hw_gpu_worker]
  g00[1:4]

``cluster/os`` (OS group - a single one here, since every host runs the same distribution):

.. code-block:: ini

  [os_rhel_10]
  mgt1
  login
  storage
  c00[1:4]
  g00[1:4]

.. note::

  mgt1, login and storage share a single ``hw_server`` group here since none of them need
  distinguishing hardware settings in this example (no console, no BMC). If that changes later
  (e.g. storage gets a console), split it into its own group - see
  :doc:`../../configuration/hosts`.

``[SCHEMA: example-cluster-groups-matrix]``
  *A grid with the 9 hosts on one axis and fn/hw/os on the other, shading which cell each host
  falls into - same spirit as the existing groups_ep.svg/ep_hard.svg images, populated with
  this cluster's actual group names.*

See :doc:`../../configuration/groups` and :doc:`../../configuration/hosts` for the rules behind
the 3 mandatory group types.

Hosts definitions
==================

``cluster/nodes.yml``. Replace the placeholder MAC addresses (``aa:bb:cc:..``) with the real
ones once the hardware is racked - see the note on this in
:doc:`../../configuration/hosts`.

.. code-block:: yaml

  all:
    hosts:

      # Management
      mgt1:
        network_interfaces:
          - interface: eth1
            ip4: 10.10.0.1
            mac: aa:bb:cc:00:00:01
            network: net-admin
          - interface: eth0
            ip4: 192.168.0.1
            mac: aa:bb:cc:00:00:02
            network: datacenter
          - interface: eth2
            ip4: 10.11.0.1
            mac: aa:bb:cc:00:00:03
            network: net-bmc

      # Login / gateway to datacenter
      login:
        network_interfaces:
          - interface: eth1
            ip4: 10.10.2.1
            mac: aa:bb:cc:00:01:01
            network: net-admin
            never_default4: true
          - interface: eth0
            ip4: 192.168.0.2
            mac: aa:bb:cc:00:01:02
            network: datacenter
            gw4: 192.168.0.200

      # Storage
      storage:
        network_interfaces:
          - interface: eth0
            ip4: 10.10.1.1
            mac: aa:bb:cc:00:02:01
            network: net-admin

      # CPU compute workers
      c001:
        bmc:
          name: bmc-c001
          ip4: 10.11.3.1
          mac: aa:bb:cc:01:00:01
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.1
            mac: aa:bb:cc:00:03:01
            network: net-admin
      c002:
        bmc:
          name: bmc-c002
          ip4: 10.11.3.2
          mac: aa:bb:cc:01:00:02
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.2
            mac: aa:bb:cc:00:03:02
            network: net-admin
      c003:
        bmc:
          name: bmc-c003
          ip4: 10.11.3.3
          mac: aa:bb:cc:01:00:03
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.3
            mac: aa:bb:cc:00:03:03
            network: net-admin
      c004:
        bmc:
          name: bmc-c004
          ip4: 10.11.3.4
          mac: aa:bb:cc:01:00:04
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.4
            mac: aa:bb:cc:00:03:04
            network: net-admin

      # GPU compute workers
      g001:
        bmc:
          name: bmc-g001
          ip4: 10.11.3.101
          mac: aa:bb:cc:02:00:01
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.101
            mac: aa:bb:cc:00:04:01
            network: net-admin
      g002:
        bmc:
          name: bmc-g002
          ip4: 10.11.3.102
          mac: aa:bb:cc:02:00:02
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.102
            mac: aa:bb:cc:00:04:02
            network: net-admin
      g003:
        bmc:
          name: bmc-g003
          ip4: 10.11.3.103
          mac: aa:bb:cc:02:00:03
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.103
            mac: aa:bb:cc:00:04:03
            network: net-admin
      g004:
        bmc:
          name: bmc-g004
          ip4: 10.11.3.104
          mac: aa:bb:cc:02:00:04
          network: net-bmc
        network_interfaces:
          - interface: eth0
            ip4: 10.10.3.104
            mac: aa:bb:cc:00:04:04
            network: net-admin

Two points worth calling out:

* ``login``'s ``net-admin`` interface carries the address ``10.10.2.1`` - exactly the
  ``gateway4`` value set on ``net-admin`` above. Without ``never_default4: true``, the ``nic``
  role would try to add a default route on that interface pointing back at itself. Setting
  ``gw4`` on the ``datacenter`` interface instead gives login its real default route, out to
  ``192.168.0.200``.
* Only the 8 compute workers have a ``bmc:`` block. mgt1, login and storage have none in this
  example.

See the :doc:`nic <../../configuration/system/nic>` role section of this documentation for the
full list of interface parameters (``never_default4``, ``gw4``, routes, bonds, VLANs, ...), and
section 2 of the data model reference (``resources/data_model.md`` at the repository root) for
the BMC block format.

Hardware settings
==================

``group_vars/hw_server/settings.yml`` (mgt1, login, storage):

.. code-block:: yaml

  hw_equipment_type: server

  hw_architecture: x86_64

  hw_specs:
    cpu:
      cores: 32
      cores_per_socket: 8
      sockets: 2
      threads_per_core: 2
    gpu: none
    memory: 131072

``group_vars/hw_cpu_worker/settings.yml`` (c001-c004):

.. code-block:: yaml

  hw_equipment_type: server

  hw_architecture: x86_64

  hw_console: console=tty0 console=ttyS0,115200n8

  hw_specs:
    cpu:
      cores: 128
      cores_per_socket: 32
      sockets: 2
      threads_per_core: 2
    gpu: none
    memory: 524288

  hw_board_authentication:
    - protocol: IPMI
      user: ADMIN
      password: ADMIN

``group_vars/hw_gpu_worker/settings.yml`` (g001-g004):

.. code-block:: yaml

  hw_equipment_type: server

  hw_architecture: arm64

  hw_console: console=tty0 console=ttyS1,115200n8 nomodeset

  hw_specs:
    cpu:
      cores: 72
      cores_per_socket: 72
      sockets: 1
      threads_per_core: 1
    gpu:
      - NVIDIA H100-SXM5-80GB
      - NVIDIA H100-SXM5-80GB
      - NVIDIA H100-SXM5-80GB
      - NVIDIA H100-SXM5-80GB
    memory: 1048576

  hw_board_authentication:
    - protocol: REDFISH
      user: admin
      password: password

.. note::

  ``nomodeset`` is folded directly into ``hw_console`` for the GPU workers, per this cluster's
  requirements. The dedicated field for kernel command-line parameters is normally
  ``hw_kernel_parameters`` (see :doc:`../../configuration/hardware_settings`) - both end up
  merged onto the same GRUB command line by the ``local_configuration`` role, so functionally it
  makes no difference, but keep this in mind if you later want ``nomodeset`` to show up
  separately in ``hw_kernel_parameters`` for readability.

  CPU and GPU specs above (128-core dual-socket x86_64 workers, single-socket 72-core arm64
  workers with 4x H100 each) are illustrative round numbers, not a specific SKU - adjust to your
  actual hardware.

See :doc:`../../configuration/hardware_settings`.

OS settings
===========

``group_vars/os_rhel_10/settings.yml``:

.. code-block:: yaml

  os_operating_system:
    distribution: redhat
    distribution_major_version: 10

  os_keyboard_layout: us
  os_system_language: en_US.UTF-8

  os_firewall: true
  os_access_control: enforcing

  os_admin_password_sha512: $6$JLtp9.SYoijB3T0Q$q43Hv.ziHgC9mC68BUtSMEivJoTqUgvGUKMBQXcZ0r5eWdQukv21wHOgfexNij7dO5Mq19ZhTR.JNTtV89UcH0

  os_admin_ssh_keys:
    - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF0iWc1oG+JA6FetOh6Qtqzqedy+n3In7MXRaT3USxtE oxedions@example.local

  os_target_disk: /dev/sda
  os_partitioning:

.. warning::

  The password hash above decodes to ``rootroot`` - it is the same placeholder used elsewhere
  in this documentation. **Do not use it in production.** Generate your own with
  ``openssl passwd -6``, and replace the SSH key with your own public key. Leaving
  ``os_partitioning`` empty triggers automatic partitioning onto ``os_target_disk``.

``os_access_control: enforcing`` turns SELinux on (enforcing) on all 9 hosts, per this cluster's
requirements.

See :doc:`../../configuration/os_settings`.

Repositories
============

``group_vars/all/repositories.yml``:

.. code-block:: yaml

  bb_repositories:
    - name: bluebanquise
      baseurl: http://bluebanquise.com/repository/releases/latest/el10/x86_64/bluebanquise/
      enabled: 1
      state: present

This gives every RHEL 10 host access to BlueBanquise's own package repository, needed in
particular by the ``pxe_stack`` role on mgt1. See the
:doc:`repositories <../../configuration/system/repositories>` role section of this
documentation for the simple vs. advanced formats, and for adding your OS's own repositories.

Firewall
========

Firewall zones are already wired up through the ``firewall_zone`` key on each network above
(``internal`` for net-admin/net-bmc, ``external`` for datacenter) plus ``os_firewall: true`` in
the OS settings. Two hosts need more than that:

``host_vars/login/firewall.yml`` - enable masquerading on the external zone, so that traffic
from ``net-admin`` routed through login reaches the internet via ``datacenter``:

.. code-block:: yaml

  firewall_zones:
    - zone: external
      masquerade: true

``host_vars/storage/firewall.yml`` - storage only accepts SSH from mgt1. Rather than opening the
``ssh`` service to the whole ``internal`` zone, the default ``ssh`` service is disabled and
replaced with a rich rule scoped to mgt1's ``net-admin`` address:

.. code-block:: yaml

  firewall_zones:
    - zone: internal
      services_disabled:
        - ssh
      rich_rules_enabled:
        - 'rule family="ipv4" source address="10.10.0.1/32" port port="22" protocol="tcp" accept'

``[SCHEMA: example-cluster-firewall-zones]``
  *Same topology as the overview schema, recolored by firewall zone (internal vs external),
  with a masquerade arrow badge on login's external-zone interface and a small padlock/rule
  badge on storage showing the ssh-from-mgt1-only rich rule.*

See the :doc:`firewall <../../configuration/system/firewall>` role section of this
documentation for the full ``firewall_zones`` vocabulary (services, ports, rich rules, ICMP
blocks, masquerade).

Validate the inventory
=======================

Before deploying anything, sanity check the inventory:

.. code-block:: bash

  ansible-inventory -i /var/lib/bluebanquise/inventories/example_cluster/ --graph
  ansible-inventory -i /var/lib/bluebanquise/inventories/example_cluster/ --host c001

The ``--graph`` output should show the 5 function groups, 3 hardware groups and single OS group,
each with the right hosts. The ``--host`` output lets you check that a given host's merged
variables (networks, hw_specs, os_operating_system, ...) look as expected before moving on to
:doc:`deployment`.
