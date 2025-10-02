======
Groups
======


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

Configure hardware and os
-------------------------

|
.. image:: images/configure_bluebanquise/management1_4.svg
   :align: center
|

management1 is part of ``hw_supermicro_X10DRT`` and ``os_almalinux_9`` groups.
We now need to define its hardware and operating system settings.

Create file ``group_vars/hw_supermicro_X10DRT/settings.yml`` with the following content:

.. code-block:: yaml

  hw_equipment_type: server # This will allow the stack to understand its an OS target and so a PXE profile should be created for it.

  hw_specs: # Defining hpw_specs is optional for now, as most infrastructure do not need it.
            # It is however mandatory later for some specialized roles like Slurm in HPC collection.
    cpu:
      name: Intel E5-2667 v4
      cores: 32
      cores_per_socket: 8
      sockets: 2
      threads_per_core: 2
    gpu:

  hw_console: console=tty0 console=ttyS1,115200
  hw_kernel_parameters: nomodeset # This is just an example here, you can leave this empty or even not define it.

  hw_board_authentication: # Authentication on BMC, optional if you do not have a BMC to manage the server.
    - protocol: IPMI
      user: ADMIN
      password: ADMIN

  # You can even add custom variables if it helps you later
  # Like adding a link to page where manual can be found
  hw_vendor_url: https://www.supermicro.com/en/products/motherboard/X10DRT-L

These are hardware related settings.
Tune this content according to your needs. For example, if you are testing the stack in VMs, do not set a console (or leave it empty), etc.

.. note::
  **This is an example.** The only mandatory value here is ``hw_equipment_type`` as it is needed for the stack to identify the hardware as a server.
  The full list of available parameters is given into the variables description page.

Now create file ``group_vars/os_almalinux_9/settings.yml`` with the following content:

.. code-block:: yaml

  os_operating_system:
    distribution: almalinux
    distribution_major_version: 9

  os_access_control: enforcing
  os_firewall: true

  os_keyboard_layout: us
  os_system_language: en_US.UTF-8

  os_partitioning: |
    clearpart --all --initlabel
    autopart --type=plain --fstype=ext4

  os_admin_password_sha512: $6$JLtp9.SYoijB3T0Q$q43Hv.ziHgC9mC68BUtSMEivJoTqUgvGUKMBQXcZ0r5eWdQukv21wHOgfexNij7dO5Mq19ZhTR.JNTtV89UcH0

.. note::
  The password here is "rootroot".
  **PLEASE**, do not use that password in production. Generate your own strong password using python3 command:
  ``python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'``

.. note::
  **This is again an example.** The only mandatory value here is ``os_operating_system`` as it is needed 
  for the stack to identify the operating system to be deployed on the target via PXE.
  The full list of available parameters is given into the variables description page.

That is all for our management1 server. We can now define the other servers.



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
