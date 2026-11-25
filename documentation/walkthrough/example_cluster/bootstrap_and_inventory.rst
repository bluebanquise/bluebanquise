=============================
Core: bootstrap and inventory
=============================

In this page, we install BlueBanquise on mgt1, and write the inventory of the core cluster:
networks, hosts, groups, hardware and operating system settings, repositories and firewall. Shared
storage, users and Slurm come later, in :doc:`extensions`, once the core cluster is up and running.

Bootstrap BlueBanquise on mgt1
==============================

Let's connect to mgt1 on its ``datacenter`` address, and run the bootstrap script:

.. code-block:: bash

  curl -o online_bootstrap.sh https://raw.githubusercontent.com/bluebanquise/bluebanquise/master/bootstrap/online_bootstrap.sh
  chmod +x online_bootstrap.sh
  sudo ./online_bootstrap.sh

It creates the ``bluebanquise`` user (home ``/var/lib/bluebanquise``), installs Ansible and the
BlueBanquise collection in a Python virtual environment, and generates an SSH key pair for this
user. From now on, we work as this user:

.. code-block:: bash

  sudo su - bluebanquise
  ansible-playbook --version

See :doc:`../../introduction/installation` for more details on the bootstrap.

Inventory skeleton
==================

Our inventory lives in ``/var/lib/bluebanquise/inventories/example_cluster``:

.. code-block:: bash

  mkdir -p /var/lib/bluebanquise/inventories/example_cluster/{cluster,group_vars/all,host_vars}
  cd /var/lib/bluebanquise/inventories/example_cluster

All the paths of this page are relative to this folder. See :doc:`../../configuration/inventories`
for the general layout, and how variables are inherited.

Global settings
===============

``group_vars/all/general.yml``:

.. code-block:: yaml

  bb_domain_name: example.cluster.local
  bb_time_zone: Europe/Brussels

  # Roles open the ports of their services in the internal zone (see Firewall below)
  bb_services_firewall_zone: internal

  # mgt1 DNS server also resolves internet names, by asking the datacenter DNS servers
  dns_server_recursion: true
  dns_server_forwarders:
    - 192.168.0.200    # replace with the DNS servers of your datacenter

See :doc:`../../configuration/general_settings`, and the
:doc:`dns_server <../../configuration/services/dns_server>` role documentation.

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

A few things worth noticing:

* ``net-admin`` and ``net-bmc`` start with ``net-``: they are management networks, on which DHCP,
  DNS and PXE are served. ``datacenter`` does not, so the stack treats it as a plain network.
* ``services_ip`` tells all hosts of a network where to find all services: here, mgt1. See the
  *Services endpoints* part of :doc:`../../configuration/services`.
* ``gateway4`` of ``net-admin`` is ``10.10.2.1``, which is login's address: login is the gateway to
  the internet for all hosts of ``net-admin``.
* ``datacenter`` has no ``gateway4``: mgt1 and login are its only members, and each one sets its
  own default route, on its own interface (see the hosts below).
* ``net-admin`` and ``net-bmc`` are bound to the ``internal`` firewall zone, ``datacenter`` to the
  ``external`` one. More on this in the Firewall part below.

See :doc:`../../configuration/networks`.

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

``cluster/os`` (a single OS group, as all hosts run the same distribution):

.. code-block:: ini

  [os_rhel_10]
  mgt1
  login
  storage
  c00[1:4]
  g00[1:4]

.. note::

  mgt1, login and storage share the ``hw_server`` group, as they need no different hardware settings
  in this example. If one of them later needs its own (a serial console, a BMC...), simply give it
  its own hardware group.

``[SCHEMA: example-cluster-groups-matrix]``
  *A grid with the 9 hosts on one axis and fn/hw/os on the other, shading which group each host
  belongs to, in the same spirit as the existing groups_ep.svg/ep_hard.svg images, with this
  cluster's actual group names.*

See :doc:`../../configuration/groups`.

Hosts
=====

``cluster/nodes.yml``. Remember to replace the placeholder MAC addresses (``aa:bb:cc:...``) with the
real ones:

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
            never_default4: true
          - interface: eth0
            ip4: 192.168.0.1
            mac: aa:bb:cc:00:00:02
            network: datacenter
            gw4: 192.168.0.200
          - interface: eth2
            ip4: 10.11.0.1
            mac: aa:bb:cc:00:00:03
            network: net-bmc

      # Login, and gateway to the internet
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
            zone: external

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

Let's look at the interesting parts:

* The first interface of each host is on ``net-admin``: it gives the host its main address, used
  for name resolution and by Ansible.
* mgt1 and login reach the internet directly, through the datacenter router: their ``datacenter``
  interface sets ``gw4``, and their ``net-admin`` interface sets ``never_default4: true``, so they do
  not use the ``gateway4`` of ``net-admin`` (for login, that would even be itself!).
* All other hosts use the ``gateway4`` of ``net-admin``, so login.
* login's ``datacenter`` interface is placed in the ``external`` firewall zone with ``zone``: this
  matters for the gateway, see the Firewall part below.
* Only the 8 compute workers have a ``bmc``.

See :doc:`../../configuration/hosts`, and the :doc:`nic <../../configuration/system/nic>` role
documentation for all interface parameters (routes, bonds, VLANs...).

Hardware settings
=================

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
    memory: 131072

``group_vars/hw_cpu_worker/settings.yml`` (c001 to c004):

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
    memory: 524288

  hw_board_authentication:
    - protocol: IPMI
      user: ADMIN
      password: ADMIN

``group_vars/hw_gpu_worker/settings.yml`` (g001 to g004):

.. code-block:: yaml

  hw_equipment_type: server
  hw_architecture: arm64

  hw_console: console=tty0 console=ttyS1,115200n8
  hw_kernel_parameters: nomodeset

  hw_specs:
    cpu:
      cores: 72
      cores_per_socket: 72
      sockets: 1
      threads_per_core: 1
    memory: 1048576
    gpu:
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3

  hw_board_authentication:
    - protocol: REDFISH
      user: admin
      password: password

  # GPU drivers (gpu role)
  gpu_vendor: nvidia
  gpu_nvidia_install_cuda: true
  gpu_reboot: true

.. note::

  Hosts without GPU simply do not define ``hw_specs.gpu``. CPU and GPU figures are round,
  illustrative numbers: adjust them to your actual hardware. ``hw_architecture`` is ``arm64`` (not
  ``aarch64``) for 64 bits ARM hosts, as everywhere in the stack.

See :doc:`../../configuration/hardware_settings`, and :doc:`../../resources/nvidia` for everything
about GPUs.

OS settings
===========

First, let's print the public key of the ``bluebanquise`` user: deployed hosts must accept it, so
Ansible can configure them.

.. code-block:: bash

  cat /var/lib/bluebanquise/.ssh/id_ed25519.pub

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
    - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF0iWc1oG+JA6FetOh6Qtqzqedy+n3In7MXRaT3USxtE bluebanquise@mgt1

  os_target_disk: /dev/sda

.. warning::

  This password hash is the one of ``rootroot``, used everywhere in this documentation: **do not use
  it in production**. Generate your own with ``openssl passwd -6``, and replace the SSH key with the
  one printed above (and your own, if you want to log in from your workstation).

Without ``os_partitioning``, the installer partitions ``os_target_disk`` automatically.
``os_access_control: enforcing`` keeps SELinux enforcing on all hosts.

See :doc:`../../configuration/os_settings`.

Repositories
============

Our hosts keep the distribution repositories they are installed with. On top of them, they need the
BlueBanquise repository: mgt1 for the PXE tools, and all hosts later for Slurm packages.

``group_vars/all/repositories.yml``:

.. code-block:: yaml

  bb_repositories:
    - name: bluebanquise
      baseurl: https://bluebanquise.com/repository/releases/latest/el10/x86_64/bluebanquise/

GPU workers are arm64 hosts, and also need the Nvidia CUDA repository and EPEL. Their hardware
group is the right place to say so, as it overrides ``group_vars/all``.
``group_vars/hw_gpu_worker/repositories.yml``:

.. code-block:: yaml

  bb_repositories:
    - name: bluebanquise
      # Check the folder of your architecture on https://bluebanquise.com/repository/releases/latest/el10/
      baseurl: https://bluebanquise.com/repository/releases/latest/el10/arm64/bluebanquise/
    - name: cuda
      baseurl: https://developer.download.nvidia.com/compute/cuda/repos/rhel10/sbsa
      gpgcheck: true
      gpgkey: https://developer.download.nvidia.com/compute/cuda/repos/rhel10/sbsa/CDF6BA43.pub
    - name: epel
      baseurl: https://dl.fedoraproject.org/pub/epel/10/Everything/aarch64

See the :doc:`repositories <../../configuration/system/repositories>` role documentation for all
formats, and :doc:`../../deployment/provision_os` for the repository of each distribution.

Firewall
========

``os_firewall: true`` enables firewalld on all hosts, and the ``firewall_zone`` of each network
binds its subnet to a zone: ``internal`` for ``net-admin`` and ``net-bmc``, ``external`` for
``datacenter``. As set in the global settings, roles open the ports of their services in the
``internal`` zone.

One service is an exception: DHCP. A host asks for its address before having one, so its request
comes from ``0.0.0.0``, which is not part of the ``net-admin`` subnet: it lands in the default zone,
``public``. So the DHCP port must be opened there. ``host_vars/mgt1/firewall.yml``:

.. code-block:: yaml

  dhcp_server_firewall_zone: public

login is our gateway: it forwards traffic from ``net-admin`` to the internet. Firewalld only forwards
traffic between two different zones when a *policy* allows it, and the address translation
(masquerade) must be set on this policy. The kernel must also be allowed to forward packets.
``host_vars/login/firewall.yml``:

.. code-block:: yaml

  firewall_policies:
    - name: internal-to-external
      ingress_zones:
        - internal
      egress_zones:
        - external
      target: ACCEPT
      masquerade: true

  local_configuration_system:
    sysctl:
      net.ipv4.ip_forward: 1

This is why login's ``datacenter`` interface is placed in the ``external`` zone: traffic going to the
internet leaves through it, so firewalld knows it is egressing the ``external`` zone.

Finally, storage only accepts SSH connections from mgt1. Instead of the ``ssh`` service open to the
whole ``internal`` zone, a rich rule allows only mgt1 address. ``host_vars/storage/firewall.yml``:

.. code-block:: yaml

  firewall_zones:
    - zone: internal
      services_disabled:
        - ssh
      rich_rules_enabled:
        - 'rule family="ipv4" source address="10.10.0.1/32" port port="22" protocol="tcp" accept'

``[SCHEMA: example-cluster-firewall-zones]``
  *Same topology as the overview schema, colored by firewall zone (internal for net-admin/net-bmc,
  external for datacenter, public for the DHCP requests coming from 0.0.0.0), with an
  "internal-to-external policy + masquerade" badge on login, and a small padlock badge on storage
  showing the ssh-from-mgt1-only rich rule.*

See the :doc:`firewall <../../configuration/system/firewall>` role documentation for all the
possibilities (services, ports, rich rules, ICMP, masquerade, policies).

Check the inventory
===================

Before deploying anything, let's ask Ansible how it understands our inventory:

.. code-block:: bash

  cd /var/lib/bluebanquise
  ansible-inventory -i inventories/example_cluster --graph
  ansible-inventory -i inventories/example_cluster --host g001

``--graph`` should show our 5 function groups, 3 hardware groups and single OS group, each with the
right hosts. ``--host`` shows all the variables a host inherits: networks, ``hw_specs``,
``bb_repositories``... Take a minute to read them, it is the best way to catch a typo now rather than
during the deployment.

We can also commit this first version of the inventory, if we keep it in git (we warmly recommend it):

.. code-block:: bash

  cd inventories/example_cluster && git init && git add . && git commit -m "Core cluster inventory"

Everything is in place: let's deploy, in :doc:`deployment`!
