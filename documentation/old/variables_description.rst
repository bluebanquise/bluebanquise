Variables description
=====================

Reserved groups and prefixs
---------------------------

The following groups are reserved (``xxxx`` means "everything else"):

- ``fn_xxxx``: these groups are function groups. Variables stored in these groups should start with the specific ``fn_`` prefix.
    - ``fn_management``: this group should contain all manager/controler nodes.
- ``hw_xxxx``: these groups are hardware groups. Variables stored in these groups should start with the ``hw_`` prefix.
- ``os_xxxx``: these groups are operating system groups. Variables stored in these groups should start with the ``os_`` prefix.

The following variables are reserved:

- ``bb_xxxx``: these variables are transverse variables, meaning these can be used by multiple roles and should precedence roles' default variables.
- ``j2_xxxx``: these variables are logic variables, meaning these contain Jinja2 code.

Note also that each role's variables are prefixed by the role name.

.. image:: images/misc/warning.svg
   :align: center

|

.. warning::
  **IMPORTANT**: ``hw_`` and ``os_`` variables **are
  not standard**. You should **NEVER** set them outside hardware or os groups.
  For example, you cannot set the ``hw_console`` parameter for a single node under it's hostvars.
  If you really need to do that, add more hardware or os groups. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.

Global settings
---------------

- **bb_cluster_name**: define cluster name. Default: ``bluebanquise``
- **bb_domain_name**: define cluster domain name. Default: ``cluster.local``
- **bb_time_zone**: define cluster time zone. Default: ``Europe/Brussels``

Host settings
-------------

- **bmc**: dict that defines an attached BMC to the host, with its name, ip4, mac and attached network.

Example:

.. code-block:: yaml

  c001:
    bmc:
      name: node001-bmc
      ip4: 10.10.103.1
      mac: 08:00:27:0d:44:91
      network: net-admin

- **network_interfaces**: list of dicts that defines all network interfaces of the host. Note that order is important. First interface in the list is the resolution (ping) interface,
  while first in the list linked to an admininstration network (see Network settings) is the ssh/Ansible interface (which can be the same than the resolution interface).

Example:

.. code-block:: yaml

  node001:
    network_interfaces:
      - interface: eth1
        ip4: 10.10.3.1
        mac: 08:00:27:0d:44:90
        network: net-admin
      - interface: eth0
        skip: true
      - interface: ib0
        ip4: 10.20.3.1
        network: interconnect
        type: infiniband

Available settings for each interface are the ones listed in `the Ansible nmcli_module. <https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html>`_
Note that only RHEL and Suse support all these settings. Available settings for Debian and Ubuntu are currently limited in the stack, but can be extended on demand (please open a feature request).

- **alias**: add an alias to the host, that will be added in the /etc/hosts file and in the dns server.
- **global_alias**: add a global alias not limited to the current iceberg (multiple icebergs mode only).

Network settings
----------------

Networks are set as a dict (not a list).

The order doesnt matter, but naming follows a specific rule:
each network starting with prefix ``net-`` is considered an administration network, other networks are considered simple networks.
Admininstration networks are used to deploy systems (PXE, DHCP, etc.) and to handle all vital services (DNS, NTP, etc.). Note that 
most roles take into account if a network is an administration network or not.

For each network, the following parameters are available:

- **prefix**: (mandatory) define the prefix of the network.
- **subnet**: (mandatory) define the subnet of the network.
- **gateway**: define the ip4 gateway of the network if exists.
- **dhcp_server**: add this network (and all linked hosts) to the dhcp server (default True).
- **dns_server**: add this network (and all linked hosts) to the dns server (default True).
- **shared_network**: name of the shared network if exists.
- **services_ip**: allows to define all services ip of the network in once, using a single ip for all (meaning a single management hosts for this network).

Example:

.. code-block:: yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0
      dhcp_server: true
      gateway: 10.10.0.1
      services_ip: 10.10.0.1
    interconnect:
      prefix: 16
      subnet: 10.20.0.0

- **services**: allows to define services ip of the network with more capabilities. Each known service takes an hostname and an ip.
  This can be used for example when services are distributed over multiple management hosts, or when services are using floating virtual ip.

Example:

.. code-block:: yaml

  networks:
    net-admin:
      prefix: 16
      subnet: 10.10.0.0
      services:
        dns:
          - ip4: 10.10.0.2
            hostname: mg2-dns4
          - ip4: 8.8.8.8
            hostname: google-public-dns
        pxe:
          - ip4: 10.10.0.1
            hostname: mg1-pxe
        ntp:
          - ip4: 10.10.0.4
            hostname: mg4-time
    interconnect:
      prefix: 16
      subnet: 10.20.0.0

.. note::
  `4` or `6` at end of some keys are related to ipv4 or ipv6, but the ipv6 support is for now limited (if needed, please open a feature request).

Hardware settings
-----------------

- **hw_ipxe_driver**: Set ipxe driver to use. Available values: ``['default', 'snp', 'snponly']``
- **hw_ipxe_platform**: Set ipxe platform if need to be fixed. Available values: ``['pcbios', 'efi']``
- **hw_ipxe_embed**: Set ipxe embed BlueBanquise script. Available values: ``['standard', 'dhcpretry']``

- **hw_console**: Set serial console if using a BMC
- **hw_kernel_parameters**: Set hardware related kernel parameters (for example, if Kernel crashes with a recent GPU, add ``nomodeset`` to this variable.)
- **hw_sysctl**: Set hardware sysctl parameters

- **hw_equipment_type**: Set equipment type of this hardware. Default is empty. If you need the hardware to be deployed via PXE, you need to set this value to ``server``

- **hw_architecture**: Set the architecture of the CPU, if needed by a role. Available values: ``['x86_64', 'arm64']``

- **hw_specs**: Dict. Set hardware specs of the equipment.

Example:

.. code-block:: yaml

  hw_specs:
    cpu:
      cores: 4
      cores_per_socket: 4
      sockets: 1
      threads_per_core: 1
    gpu: None

- **hw_board_authentication**: List of dicts. Set board authentication mechanism and needed credentials.

Example:

.. code-block:: yaml

  hw_board_authentication:
    - protocol: IPMI
      user: ADMIN
      password: ADMIN

OS settings
-----------

- **os_preserve_efi_first_boot_device**: Force grub to keep first entry in boot order (EFI systems). Available values: ``['true', 'false']``

- **os_access_control**: Enable or disable access control (SELinux, Apparmor). Available values: ``['enforcing', 'permissive', 'disabled']``
- **os_firewall**: Enable or disable Firewall. Available values: ``['true', 'false']``

- **os_kernel_parameters**: Set OS related kernel parameters.
- **os_sysctl**: Set OS sysctl parameters

- **os_keyboard_layout**: Set keyboard layout. Default is us.
- **os_system_language**: Set system language. Default is en_US.UTF-8 and you should keep it (it simplifies a lot web searchs).

- **os_admin_password_sha512**: SHA512 enrcypted password for default admin user. Default is ``!`` wich means no password allowed (keys only).
- **os_admin_ssh_keys**: List. List of ssh public keys to install for default admin sudo user.

- **os_partitioning**: Raw content of auto installation file on how to partition the disks. **WARNING!! If this value is not set, auto partitioning is enabled**.
  Raw content is kickstart partitioning syntax for RHEL like, AutoYast for Suse like, Preseed for Debian like, and Curtin for Ubuntu like.

Example for a raid on RHEL:

.. code-block:: yaml

  os_partitioning: |
    # Partition clearing information
    clearpart --all --initlabel --drives=/dev/disk/by-path/pci-0000:00:11.4-ata-1.0,/dev/disk/by-path/pci-0000:00:11.4-ata-2.0
    # Disk partitioning information
    part raid.01 --ondisk=disk/by-path/pci-0000:00:11.4-ata-1.0 --size=1024
    part raid.02 --ondisk=disk/by-path/pci-0000:00:11.4-ata-1.0 --size=4096
    part raid.03 --ondisk=disk/by-path/pci-0000:00:11.4-ata-1.0 --size=1000 --grow
    part raid.04 --ondisk=disk/by-path/pci-0000:00:11.4-ata-2.0 --size=1024
    part raid.05 --ondisk=disk/by-path/pci-0000:00:11.4-ata-2.0 --size=4096
    part raid.06 --ondisk=disk/by-path/pci-0000:00:11.4-ata-2.0 --size=1000 --grow
    raid /boot --level=1 --device=md0 --fstype=ext4 raid.01 raid.04 --label=BOOT
    raid swap --level=1 --device=md2 --fstype=swap raid.02 raid.05 --label=SWAP
    raid / --level=1 --device=md3 --fstype=ext4 raid.03 raid.06 --label=ROOT

- **os_operating_system**: Dict. Define operating system if type is server.

Example:

.. code-block:: yaml
    
  os_operating_system:
    distribution: ubuntu  # Must be lower
    distribution_major_version: 22
    distribution_version: 22.04

Repositories
------------

File ``group_vars/all/repositories.yml`` configure repositories to
use for all nodes (using groups and variable precedence, repositories can be
tuned for each group of nodes, or even each node).

It is important to set correct repositories to avoid issues during deployments.

There are 2 ways to define a repository.
Either specifying a full URL and parameters of the repository,
or using the stack automatic mechanism (which involves your organized repositories as expected by the stack).

Full definition
^^^^^^^^^^^^^^^

* RHEL like system:

.. raw:: html

  <div style="padding: 6px;">
  <b>RHEL</b> <img src="_static/logo_rhel.png">, <b>CentOS</b> <img src="_static/logo_centos.png">, <b>RockyLinux</b> <img src="_static/logo_rocky.png">, <b>OracleLinux</b> <img src="_static/logo_oraclelinux.png"><br> <b>CloudLinux</b> <img src="_static/logo_cloudlinux.png">, <b>AlmaLinux</b> <img src="_static/logo_almalinux.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - name: os_base
      baseurl: http://my-server/repositories/el8/
      enabled: 1
      state: present

Stack should support all available parameters listed in `the Ansible yum_repository_module. <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yum_repository_module.html>`_

* Ubuntu or Debian like systems:

.. raw:: html

  <div style="padding: 6px;">
  <b>Ubuntu</b> <img src="_static/logo_ubuntu.png">, <b>Debian</b> <img src="_static/logo_debian.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - repo: deb http://my-server/repositories/ubuntu22/ stable main
      state: present

Stack should support all available parameters listed in `the Ansible apt_repository_module. <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_repository_module.html>`_

* Suse like system:

.. raw:: html

  <div style="padding: 6px;">
  <b>Suse</b> <img src="_static/logo_suse.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - name: base
      baseurl: http://my-server/repositories/leap15/
      enabled: 1
      state: present

Stack should support all available parameters listed in `the Ansible zypper_repository_module. <https://docs.ansible.com/ansible/latest/collections/community/general/zypper_repository_module.html>`_

