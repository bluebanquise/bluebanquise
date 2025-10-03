===========
OS settings
===========

.. warning::
  **IMPORTANT**: ``hw_`` and ``os_`` variables **are
  not standard**. You should **NEVER** set them outside hardware or os groups.
  For example, you cannot set the ``hw_console`` parameter for a single node under it's hostvars.
  If you really need to do that, add more hardware or os groups. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.

  Note however that these variables can be used at ``group_vars/all`` level.

Once an OS group has been defined into ``cluster/`` folder, you can create a group's dedicated folder
inside ``group_vars/`` directory. The folder name must match the group name. For example, for group
``os_ubuntu_24``, directory path will be ``group_vars/os_ubuntu_24``.

Once this directory has been created you can configure the operating system of this group.
Create a file named ``settings.yml`` inside the group folder, and then see bellow for available parameters.

Linux distribution
==================

To define target Linux distribution of the OS group, set these parameters:

.. code-block:: yaml

  os_operating_system:
    distribution: ubuntu  # Must be lower case
    distribution_version: 24.04
    distribution_major_version: 24

Explanations:

* ``distribution``: Linux distribution to use. Available distributions are: ``[ubuntu, debian, opensuse, redhat, rhel, centosstream, oraclelinux, almalinux, rockylinux]``. Please note that ``[rhel, centosstream, oraclelinux, almalinux, rockylinux]`` are just links to redhat. Please also note that ``opensuse`` refers to opensuse leap OS.
* ``distribution_version``: Distribution version to use, minor number.
* ``distribution_major_version``: Distribution version to use, major number.

.. note::

  If using stream updates between minors versions, for example RHEL 9 as a stream (so no minors in repositories),
  then you can set ``distribution_version`` same as ``distribution_major_version``, so ``9`` in this example.

Languages
=========

You can define OS language and keyboard mapping with the two following keys:

.. code-block:: yaml

  os_keyboard_layout: us
  os_system_language: en_US.UTF-8

Security
========

Firewall
--------

You can enable or disable firewall (firewalld) using:

.. code-block:: yaml

  os_firewall: true

Access control
--------------

You can also enable or disable os access control (SELinux or Apparmor) using:

.. code-block:: yaml

  os_access_control: enforcing

For RHEL systems, accepted values are:

* `enforcing`
* `permissive`
* `disabled`

For Ubuntu systems, accepted values are:

* `enforcing`
* `disabled`

Admin password and ssh key
==========================

Password
--------

To define admin password (bluebanquise user password, bluebanquise user being sudo user), use the following key:

.. code-block:: yaml

  os_admin_password_sha512: $6$JLtp9.SYoijB3T0Q$q43Hv.ziHgC9mC68BUtSMEivJoTqUgvGUKMBQXcZ0r5eWdQukv21wHOgfexNij7dO5Mq19ZhTR.JNTtV89UcH0


The password here is "rootroot". **PLEASE**, do not use that password in production.

To generate your own strong password, use either openssl either a docker image tool or anyother method you prefer.
You just need an sha-512 enrcypted password that will go in the shadow file of the target system.

Using openssl:

.. code-block:: text

  openssl passwd -6

Using docker (replace rootroot by your password):

.. code-block:: text

  docker run --name mkpasswd --rm tooldockers/mkpasswd:latest -m sha-512 rootroot

Please note that you can also leave this key empty, which will result in ``!`` value. Authentication will then only be possible via ssh key.
While this is interesting for security reasons, please keep in mind that during cluster setup it can be useful to have a password for admin so you can interactively login on the node using a keyboard and a screen.

SSH key
-------

To define SSH key(s) of target admin, define them as a list under ``os_admin_ssh_keys`` key.

For example:

.. code-block:: yaml

  os_admin_ssh_keys:
    - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF0iWc1oG+JA6FetOh6Qtqzqedy+n3In7MXRaT3USxtE oxedions@prima

Partitioning
============

Please note that partitioning can be defined either inside os group or hardware groups.
Just be coherent: if you rely on hardware groups for this, always do this. If you rely on os groups, always do so. Do not mix.
Also, please note that ``os_partitioning`` will precedence ``hw_partitioning`` if mixed (but again, not recommended to mix both).

To define partitioning, you need to use the ``os_partitioning`` multi lines key, and use your OS raw  autoinstall native format.
Which means that for RHEL targets, you will need to use kickstart syntax, for Debian preseed, for Ubuntu curtin, and for OpenSuse Leap autoyast.

.. warning::

  If this key is not defined or empty, the stack will activate auto-partitioning.

You can also let os_partitioning empty, and just define ``os_target_disk`` key, to specify the disk to use for auto partitioning.

.. code-block:: yaml

  os_target_disk: /dev/sda

Some examples are given bellow for each distribution.

RHEL
----

Simple:

.. code-block:: yaml

  os_partitioning: |
    clearpart --all --initlabel
    autopart --type=plain --fstype=ext4

With raid and by path devices:

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

Ubuntu
------

Please refer to: https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html#storage

.. code-block:: yaml

  os_partitioning: |
    storage:
      swap:
        size: 0
      config:
        - type: disk
          id: disk0
          serial: ADATA_SX8200PNP_XXXXXXXXXXX
        - type: partition
          id: boot-partition
          device: root-disk
          size: 10%
        - type: partition
          id: root-partition
          size: 20G
        - type: partition
          id: data-partition
          device: root-disk
          size: -1

Debian
------

.. code-block:: yaml

  os_partitioning: |
    d-i partman-auto/disk string /dev/sda
    d-i partman-auto/method string regular
    d-i partman-auto/choose_recipe select atomic
    d-i partman-auto/init_automatically_partition select Guided - use entire disk

OpenSuse Leap
-------------

.. code-block:: yaml

  os_partitioning: |
    <partitioning config:type="list">
      <drive>
        <initialize config:type="boolean">true</initialize>
        <use>all</use>
        <partitions config:type="list">
          <partition>
            <filesystem config:type="symbol">ext4</filesystem>
            <mount>/</mount>
            <size>max</size>
          </partition>
          <partition>
            <filesystem config:type="symbol">ext4</filesystem>
            <mount>/boot</mount>
            <size>512MiB</size>
          </partition>
          <partition>
            <mount>swap</mount>
            <size>512MiB</size>
          </partition>
        </partitions>
      </drive>
    </partitioning>

Kernel settings
===============

You can set kernel command line parameters for node to be used at boot, or/and os sysctl entries to set.

Kernel cmd parameters
=====================

Just set the os_kernel_parameters key, and add the requested cmd args inside this variable.

For example:

.. code-block:: yaml

  os_kernel_parameters: nomodeset

.. note::

  An ``hw_kernel_parameters`` variable is also available for hardware settings. Both os and hw variables can be mixed together, they will be merged.

Sysctl
======

Just set ``os_sysctl`` key as a dict of key:value couples.

.. code-block:: yaml

  os_sysctl:
    kernel.panic: absent
    vm.swappiness: 5
