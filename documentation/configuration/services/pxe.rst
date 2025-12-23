===
PXE
===

PXE, for Preboot Execution Environment, often called "pixie".

This is probably the most complexe and difficult part of the stack.

Concept is the following: a server exposes on the network all needed material to install an operating system,
and using an auto-installation mechanism, PXE allows to provision operating system on nodes over the network.

Difficulty comes from all the events that occur during the process: hardware issue or incompatibility, network issues, bad configuration, etc.

I strongly advise to make sure you can provision your nodes via PXE before configuring complexe networks or enabling advanced security services.

This page details all settings available to configure pxe.
Procedure on how to deploy a node over PXE once role has been applied is describe in the deployment section of this documentation.

.. note::

  * PXE HTTP files are stored inside ``/var/www/html/pxe/`` folder.
  * PXE TFTP files are stored into ``/var/lib/tftpboot/`` folder.

.. warning::

  Variable ``hw_equipment_type`` **MUST** be set to ``server`` for a node to be taken into account by all the pxe stack.
  Please make sure your nodes to be deployed via PXE are member of an hardware group with this setting.

Automated installation parameters
=================================

Most parameters (OS to use, partitioning, etc) are given in the os and hardware settings (via ``os_`` and ``hw_`` variables),
please refer to these sections of the documentation.

The role embed however some variables to tune or force specific settings.

Time zone
---------

By default, global variable ``bb_time_zone`` will be used.
It is however possible to force another timezone to be used by setting ``pxe_stack_time_zone``, which will precedence global setting.

Admin user
----------

By default, the root account will be deactivated, and a sudo user will be created instead.
It is possible to manipulate this behavior using the following variables:

* ``pxe_stack_enable_root``: enable or not root user. Default is ``false``. If false, a sudo user will be created instead (recommended!).
* ``pxe_stack_sudo_user``: name of the sudo user to be created. Default is ``bluebanquise``, and I honestly havent tested to change that, so be careful with this.
* ``pxe_stack_sudo_user_home``: path of the sudo user home. Default is ``/var/lib/bluebanquise``. Same for sudo user name, I havent tested changing that so be careful.
* ``pxe_stack_sudo_user_uid``: uid of the sudo user. Default is ``377``.
* ``pxe_stack_sudo_user_gid``: gid of the sudo user. Default is ``377``.
* ``pxe_stack_sudo_is_passwordless``: make the sudo user passwordless. Default to ``true``. Note: if you choose to not have a passwordless user, please refer to https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_privilege_escalation.html for how to pass password at ansible-playbook execution (--ask-become-pass).

Reboot after installation
-------------------------

Once automated installation is done, you will want the server to reboot automatocally and boot freshly installed OS.
If you do not want that, it is possible to set different behaviors:

* ``pxe_stack_post_install_action``: Action to do at the end of auto-installation. Default is ``reboot``.
* ``pxe_stack_post_install_boot_to_disk``: Should we boot over disk at next boot after auto-installation. Default is ``true``.

Also, a pxe dedicated ``os_`` variable is available to force EFI order to be preserved if EFI system. This can be super useful because when Grub registers at the end of
auto-installation, EFI order is automatically updated on the system, and you might want to preserv PXE boot at first for all boots.
By default, BlueBanquise stack will try to keep boot order, but you can deactivate this by setting ``os_preserve_efi_first_boot_device`` to ``false`` (default is ``true``).

Repositories
------------

By default, native Repositories will be kept. You might want to remove them during auto-installation. If so, it is possible to set ``pxe_stack_preserve_repositories`` to ``false``. Default is ``true``.

Diskless
========

The BlueBanquise stack providesa way to boot nodes in diskless (only RHEL for now, if you need another OS let me know).

Few setting are available:

* ``pxe_stack_enable_diskless``: enable or not diskless support. Default is ``true``.
* ``pxe_stack_diskless_nfs_path``: set the NFS path that will be exported by the diskless server, to manipulate futur golden images. Default is ``/nfs/diskless``.

iPXE
====

BlueBanquise PXE process makes usage of iPXE. Many settings are available.

Force specific rom usage
------------------------

DHCP server will redirect nodes that boot to the next-server that will provides an iPXE rom.

While default roms should be ok for most of servers, it is possible to request a specific rom to be loaded per hardware.

There are 3 settings to manipulate the rom to be used.

* ``hw_ipxe_driver``: set ipxe driver to use. Available values: ``['default', 'snp', 'snponly']``. If not set, default will be snponly.
* ``hw_ipxe_platform``: set ipxe platform if need to be forced. Available values: ``['pcbios', 'efi']``. If not set, system will auto-detect platform.
* ``hw_ipxe_embed``: set ipxe embed BlueBanquise script. Available values: ``['standard', 'dhcpretry']``. If not set, default will be dhcpretry.

You will need to re-apply DHCP server role to have these settings taken into account.

Role scope
==========

It is possible to reduce or enlarge role scope, to support more or less distributions.

* ``pxe_stack_diskful_os_redhat``: enable RHEL support. Default ``true``.
* ``pxe_stack_diskful_os_ubuntu``: enable Ubuntu support. Default ``true``.
* ``pxe_stack_diskful_os_suse``: enable OpenSuse Leap support. Default ``true``.
* ``pxe_stack_diskful_os_debian``: enable Debian support. Default ``true``.

It is also possible to enable or disable some specific tools available at PXE boot time.

* ``pxe_stack_enable_clonezilla``: enable clonezilla support. Default ``true``.
* ``pxe_stack_enable_alpine``: enable alpine live support. Default ``true``.
* ``pxe_stack_enable_memtest``: enable memtest86+ support. Default ``true``.

Other settings
==============

DHCP at boot
------------

Sometime, due to networking, DHCP gathering can be difficult at Kernel boot. A specific setting can be set to be more agressive catching the DHCP. This is super useful for diskless.

* ``pxe_stack_os_kernel_aggressive_dhcp``: Default is ``true``.

Custom content in auto-installation files
-----------------------------------------

It is possible to add custom content to auto-installation files, by using variable ``pxe_stack_os_autoinstall_custom_content``.
Please note that you will need to add raw content adapted to the target distribution (kickstart, etc.). Please also note that this is a multilines variable.

Example:

.. code:: yaml

  pxe_stack_os_autoinstall_custom_content: |
    %post
    dnf install git -y
    %end


Scripts during installation
---------------------------

It is possible to include scripts or snippets that will be run at different stages of the installation procedure.
The exact injection points will depend on the distribution used. For now these are:

**Debian**: The ``early_command`` and ``late_command`` preseed options. See the [official documentation](https://www.debian.org/releases/trixie/amd64/apbs05.en.html#preseed-hooks) for more details.

These are the variables:

* `pxe_stack_autoinstall_pre_scripts`: An array of snippets to be executed **in the installation environment** before the installation has started. Example:

  .. code:: yaml

    pxe_stack_autoinstall_pre_scripts:
      - 'echo "nameserver 10.1.2.3" > /etc/resolv.conf'
      - "{{ lookup('ansible.builtin.file', 'my_pre_script.sh') }}"
      
* `pxe_stack_autoinstall_pre_scripts`: An array of snippets to be executed **in the already installed environment** after the installation has finished. Example:
  
  .. code:: yaml

    pxe_stack_autoinstall_post_scripts:
      - systemctl enable systemd-networkd-wait-online
      - "{{ lookup('ansible.builtin.file', 'my_post_script.sh') }}"



OS specific settings
--------------------

Ubuntu
''''''

* ``os_pxe_ubuntu_apt_configuration``: allows to pass specific settings to the apt configuration during auto-installation

Refer to https://cloudinit.readthedocs.io/en/latest/reference/modules.html#apt-configure for more details.

An example can be:

.. code:: yaml

  os_pxe_ubuntu_apt_configuration: |+2
      disable_suites:
        - backports
      primary:
        - arches: amd64
          uri: "http://myrepo/repositories/ubuntu/24.04/x86_64/os"
      security:
        - arches: amd64
          uri: "http://myrepo/repositories/ubuntu/24.04/x86_64/os"
