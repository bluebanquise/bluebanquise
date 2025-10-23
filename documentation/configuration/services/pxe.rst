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

Most parameters (os to use, partitioning, etc) are given in the os and hardware settings (via ``os_`` and ``hw_`` variables), please refer to these sections of the documentation.

The role embed however some variables to tune or force specific settings.

Time zone
---------

By default, global variable ``bb_time_zone`` will be used. It is however possible to force another timezone to be used by setting ``pxe_stack_time_zone``, which will precedence global setting.

Admin user
----------

# Enable root user as default user
pxe_stack_enable_root: false
# Sudo user if root not enabled
pxe_stack_sudo_user: bluebanquise
pxe_stack_sudo_user_home: /var/lib/bluebanquise
pxe_stack_sudo_user_uid: 377
pxe_stack_sudo_user_gid: 377
# Set sudo user as passwordless sudoer
pxe_stack_sudo_is_passwordless: true

Reboot after installation
-------------------------

# default is reboot, can be set to poweroff, halt or shutdown
pxe_stack_post_install_action: reboot
pxe_stack_post_install_boot_to_disk: true

Repositories
------------

# Preserve default repositories
pxe_stack_preserve_repositories: true

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

# Enable distributions support
pxe_stack_diskful_os_redhat: true
pxe_stack_diskful_os_ubuntu: true
pxe_stack_diskful_os_suse: true
pxe_stack_diskful_os_debian: true
pxe_stack_diskful_os_dgx: false

Other settings
==============

pxe_stack_os_kernel_aggressive_dhcp: true













############################################################
### Default equipment profile parameters



pxe_stack_os_keyboard_layout: us  # us, fr, etc.
pxe_stack_os_system_language: en_US.UTF-8  # You should not update this if you want to google issues...

pxe_stack_os_admin_password_sha512: "!"
pxe_stack_os_admin_ssh_keys: []

pxe_stack_os_access_control: enforcing
pxe_stack_os_firewall: true

# WARNING! If nothing is set for partitioning,
# automatic partitioning will be activated.
pxe_stack_os_partitioning:

pxe_stack_hw_preserve_efi_first_boot_device: true

# Add custom content to any kind of auto install files: kickstart, preseed, user-data and autoyast
# This content is added at top of files.
pxe_stack_os_autoinstall_custom_content:

# Add custom script to autoyast and user-data. Use pxe_stack_os_autoinstall_custom_content variable for kickstart.
pxe_stack_os_autoinstall_custom_scripts: []
#  - name: script1
#    content: |
#      ...

# Add proxies
pxe_stack_os_pxe_repository_proxy:
pxe_stack_os_pxe_proxy:

# Automatically detect NIC to be used in preseed
# Only works if a single NIC is connected.
pxe_stack_os_preseed_auto_main_network_interface: true

############################################################
### Misc parameters

pxe_stack_suse_autoinstall_repositories: []
#  - media_url: http://10.10.0.1/repositories/sles/15.3/x86_64/updates
#    name: sles_updates

############################################################
### DISKLESS

pxe_stack_enable_diskless: true
pxe_stack_diskless_nfs_path: /nfs/diskless

############################################################
### TOOLS

# Add optional dedicated entries in ixpe menu
pxe_stack_enable_clonezilla: true
pxe_stack_enable_alpine: true
pxe_stack_enable_memtest: true

### CLONEZILLA
# Allows to backup/restore systems, or even deploy multiple systems via images.
# Be aware that pxe_stack role does not handle nfs server, you will have to
# use the nfs role to create export or use an external nfs.

# NFS server to store images. Should be an ip, as DNS resolution might not work.
# If not set, default is pxe_server ip (next-server, provided by DHCP server).
pxe_stack_clonezilla_nfs_export_server:

# Mount point from which load images from NFS server.
pxe_stack_clonezilla_nfs_mount_point: /nfs/cloned_images



- **os_preserve_efi_first_boot_device**: Force grub to keep first entry in boot order (EFI systems). Available values: ``['true', 'false']``



