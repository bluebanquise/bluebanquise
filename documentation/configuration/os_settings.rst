===========
OS settings
===========

Operating system groups (``os_`` groups) gather all the settings related to the operating system
of their hosts: which distribution to install, language, security, admin credentials, partitioning,
and kernel settings. Hosts sharing the same OS group are installed and configured the same way.

.. warning::
  **IMPORTANT**: ``hw_`` and ``os_`` variables **are
  not standard**. You should **NEVER** set them outside hardware or os groups.
  For example, you cannot set the ``hw_console`` parameter for a single host under its hostvars.
  If you really need to do that, add more hardware or os groups. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.

  Note however that these variables can be used at ``group_vars/all`` level.

Once an OS group has been defined in the ``cluster/`` folder, let's create its dedicated folder
inside ``group_vars/``, with the same name as the group. For example, for group ``os_ubuntu_24``,
the folder is ``group_vars/os_ubuntu_24``.

Then create a file named ``settings.yml`` inside this folder: all the parameters below go there.

Linux distribution
==================

To define the Linux distribution of the OS group, set these parameters:

.. code-block:: yaml

  os_operating_system:
    distribution: ubuntu  # Must be lower case
    distribution_version: "24.04"
    distribution_major_version: 24

Explanations:

* ``distribution``: Linux distribution to use. Available distributions are: ``[ubuntu, debian, opensuse, redhat, rhel, centosstream, oraclelinux, almalinux, rockylinux]``. ``[rhel, centosstream, oraclelinux, almalinux, rockylinux]`` are handled as ``redhat``, and ``opensuse`` refers to OpenSuse Leap.
* ``distribution_version``: Distribution version to use, with its minor number.
* ``distribution_major_version``: Distribution version to use, major number only.

These values are used to find installation media and repositories on the management host (see
:doc:`../deployment/provision_os`). Quote versions with a dot, like ``"24.04"`` or ``"16.0"``, so YAML
keeps them as text.

Supported distributions are RHEL 9 and 10 (and compatible distributions), Ubuntu 24.04 and 26.04,
Debian 13, and OpenSuse Leap 16.

.. note::

  If using stream updates between minors versions, for example RHEL 9 as a stream (so no minors in repositories),
  then you can set ``distribution_version`` same as ``distribution_major_version``, so ``9`` in this example.

Languages
=========

Language and keyboard mapping are set with the two following keys:

.. code-block:: yaml

  os_keyboard_layout: us
  os_system_language: en_US.UTF-8

Security
========

Firewall
--------

The firewall (firewalld) is enabled by default. It can be disabled using:

.. code-block:: yaml

  os_firewall: false

When enabled, the ``firewall`` role installs and starts firewalld, and each role opens the ports of
the services it provides (see :doc:`services`).

Access control
--------------

Access control (SELinux on RHEL, AppArmor on Ubuntu, Debian and OpenSuse) is set using:

.. code-block:: yaml

  os_access_control: enforcing

Accepted values are:

.. list-table::
   :header-rows: 1

   * - Value
     - RHEL (SELinux)
     - Ubuntu, Debian, OpenSuse (AppArmor)
   * - ``enforcing`` (default)
     - SELinux enforcing
     - AppArmor enabled, profiles as shipped by the distribution
   * - ``permissive`` or ``complain``
     - SELinux permissive
     - AppArmor enabled, all profiles in complain mode
   * - ``disabled``
     - SELinux disabled
     - AppArmor disabled

It is applied both at installation time and by the ``local_configuration`` role. Switching SELinux
from or to ``disabled`` requires a reboot.

Admin password and ssh key
==========================

Password
--------

The admin password is the password of the ``bluebanquise`` user created on deployed hosts (a sudoer),
or of root if the ``pxe_stack`` role is configured to use root. Set it using the following key:

.. code-block:: yaml

  os_admin_password_sha512: $6$JLtp9.SYoijB3T0Q$q43Hv.ziHgC9mC68BUtSMEivJoTqUgvGUKMBQXcZ0r5eWdQukv21wHOgfexNij7dO5Mq19ZhTR.JNTtV89UcH0


The password here is "rootroot". **Please** do not use it in production!

To generate your own strong password, use openssl, a container image, or any other method you prefer.
What we need is a SHA-512 hashed password, as found in ``/etc/shadow``.

Using openssl:

.. code-block:: text

  openssl passwd -6

Using docker (replace rootroot by your password):

.. code-block:: text

  docker run --name mkpasswd --rm tooldockers/mkpasswd:latest -m sha-512 rootroot

You can also leave this key empty, which locks the password: authentication is then only possible
with SSH keys. This is good for security, but keep in mind that during the cluster setup, being able
to log in with a keyboard and a screen (or a console) can save your day.

SSH key
-------

SSH public keys allowed to log in as the admin user are listed under the ``os_admin_ssh_keys`` key.
Remember to include the key of the ``bluebanquise`` user of the management host
(``/var/lib/bluebanquise/.ssh/id_ed25519.pub``), so Ansible can reach deployed hosts.

For example:

.. code-block:: yaml

  os_admin_ssh_keys:
    - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF0iWc1oG+JA6FetOh6Qtqzqedy+n3In7MXRaT3USxtE oxedions@prima

Partitioning
============

Partitioning can be defined either in OS groups (``os_partitioning``) or in hardware groups
(``hw_partitioning``), as it often depends on the disks of the hardware. Just be consistent: choose
one way, and stick to it. If both are set, ``os_partitioning`` wins.

Partitioning uses the native format of each distribution installer: kickstart for RHEL, autoinstall
(curtin) for Ubuntu, preseed for Debian, and Agama (written as YAML) for OpenSuse Leap 16.

.. warning::

  If this key is not defined or empty, the stack will activate auto-partitioning.

You can also let os_partitioning empty, and just define ``os_target_disk`` key, to specify the disk to use for auto partitioning.

.. code-block:: yaml

  os_target_disk: /dev/sda

Here are some examples for each distribution.

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
          id: root-disk
          serial: ADATA_SX8200PNP_XXXXXXXXXXX
        - type: partition
          id: boot-partition
          device: root-disk
          size: 10%
        - type: partition
          id: root-partition
          device: root-disk
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

OpenSuse Leap 16
----------------

OpenSuse Leap 16 is installed by Agama, which uses JSON profiles. Partitioning is an Agama
`storage section <https://agama-project.github.io/docs/user/reference/profile/storage>`_, written
as YAML (not as a multi lines string):

.. code-block:: yaml

  os_partitioning:
    drives:
      - search: /dev/sda
        partitions:
          - search: "*"
            delete: true
          - filesystem:
              path: /
              type: xfs
            size: 50 GiB
          - filesystem:
              path: swap
            size: 4 GiB
    boot:
      configure: true

Without ``os_partitioning``, the installer default layout (Btrfs root with snapshots, and swap) is
created on ``os_target_disk``, or on the first disk found.

OpenSuse Leap 15
----------------

Older OpenSuse Leap 15 uses AutoYaST XML:

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

Kernel command line parameters, sysctl entries, and even the exact kernel version can be set at the
OS group level. They are applied at installation time and by the ``local_configuration`` role.

Kernel cmd parameters
---------------------

Set the ``os_kernel_parameters`` key, with the parameters to add to the kernel command line.

For example:

.. code-block:: yaml

  os_kernel_parameters: nomodeset

.. note::

  An ``hw_kernel_parameters`` variable is also available in hardware groups. Both are merged.

Sysctl
------

Set the ``os_sysctl`` key as a dictionary of key: value couples.

.. code-block:: yaml

  os_sysctl:
    kernel.panic: 10
    vm.swappiness: 5

Kernel version lock
-------------------

On production clusters, we often want all hosts to run the exact same kernel, and to choose when it
changes (drivers built for a given kernel, validated configurations...). Set the exact kernel version,
as returned by ``uname -r``:

.. code-block:: yaml

  os_kernel_version: "5.14.0-427.24.1.el9_4.x86_64"
  os_kernel_version_allow_reboot: false

The ``local_configuration`` role then installs this kernel if needed, makes it the default boot
entry, and locks it, so package updates leave it alone (``dnf versionlock`` on RHEL, ``apt-mark hold``
on Ubuntu and Debian). Hosts reboot on the new kernel only if ``os_kernel_version_allow_reboot`` is
``true``; otherwise, they use it at their next reboot. This is not supported on OpenSuse.


Scripts during installation
===========================

Scripts or snippets can be run at different stages of the installation. The exact injection
points depend on the distribution. For now these are:

:Debian:
  The ``early_command`` and ``late_command`` preseed options. See the `official documentation <https://www.debian.org/releases/trixie/amd64/apbs05.en.html#preseed-hooks>`_ for more details.

These are the variables:

* ``pxe_stack_autoinstall_pre_scripts``: An array of snippets to be executed *in the installation environment* before the installation has started. Example:

  .. code-block:: yaml

    pxe_stack_autoinstall_pre_scripts:
      - 'echo "nameserver 10.1.2.3" > /etc/resolv.conf'
      - "{{ lookup('ansible.builtin.file', 'my_pre_script.sh') }}"
* ``pxe_stack_autoinstall_post_scripts``: An array of snippets to be executed *in the already installed environment* after the installation has finished. Example:

  .. code-block:: yaml

    pxe_stack_autoinstall_post_scripts:
      - systemctl enable systemd-networkd-wait-online
      - "{{ lookup('ansible.builtin.file', 'my_post_script.sh') }}"

OpenSuse Leap 16 runs ``pxe_stack_os_autoinstall_custom_scripts`` as Agama post installation
scripts, inside the installed system. See the **pxe_stack** role documentation for the scripts
support of each distribution.
