PXE Stack
---------

Description
^^^^^^^^^^^

This role provides the whole PXE stack. It is a key feature of the stack.

Instructions
^^^^^^^^^^^^

This role will deploy all the needed files, binaries, and scripts to deploy
remote hosts using PXE (or even USB and CD boot).

The role takes place just after the dhcp in the PXE deployment, and will
configure all the iPXE chain needed after dhcp provided hosts with next-server
ip address and filename to use.

**Files location**
""""""""""""""""""

* PXE boot files are located in /var/www/html/preboot_execution_environment/, with path depending of the operating system.
   * *bin/* directory contains some needed bin files, typically grub2 files for EFI boot.
   * *equipment_profiles/* directory contains equipment_profiles related files, i.e. ipxe file with group variables, and os configuration files (kickstart, preseed, autoyast).
   * *nodes/* directory contains hosts dedicated files, i.e. ipxe file with hosts dedicated variables.
   * *osdeploy/* directory contains static files, with patterns to boot each kind of supported distributions.
* Basic configuration files are located in /etc/bluebanquise/pxe/.
   * *nodes_parameters.yml* contains all nodes PXE needed parameters.
   * *pxe_parameters.yml* contains needed values for scripts to adapt to **current pxe server host** (these parameters do not apply to PXE booted hosts !!).
* Scripts are located in /usr/bin/.

**Inventory configuration**
"""""""""""""""""""""""""""

This role will rely on multiple parts of the inventory, and is probably the most "invasive" role of the whole stack.

* equipment_profile parameters are used for each equipment_profile group. All
  boot configuration is made relying on it (operating system, cpu architecture,
  console, kernel parameters, etc.). It is recommended to ensure coherency of
  the equipment_profile files.
* authentication parameters are used to provide root password and default ssh
  authorized key.
* hosts **network_interfaces** dedicated variables, to be able to force static
  ip address at kernel boot.

**bootset usage**
"""""""""""""""""

Once the role is deployed, and hosts gathered into */etc/bluebanquise/pxe/nodes_parameters.yml*, the bootset tool can be used to manipulate remote hosts PXE boot. By default, 3 states can be defined for each host:

* osdeploy: the remote host will deploy/redeploy its operating system, using inventory equipment_profile parameters of its equipment profile group.
* disk: the remote host will boot on disk. This parameter is automatically set after a successful **osdeploy**.
* diskless: the remote host will boot using a diskless mechanism. This diskless boot is generic, and is handled by an optional external role.

Again, consider that if you set an host to osdeploy, and that it succeed its deployment, stack will automatically set the host into disk boot for next boot, to avoid infinite reinstallation loop.

To get bootset help, use:

.. code-block:: text

  bootset -h

To ask an host to deploy/redeploy its operating system, use:

.. code-block:: text

  bootset -n c001 -b osdeploy

With c001 the target host to be redeployed.

To set this host to boot on disk, use:

.. code-block:: text

  bootset -n c001 -b disk

It is also possible to work on a range of host, using nodeset formatting:

.. code-block:: text

  bootset -n c001,c002,c[010-020],login1 -b disk

Also, if combined with **clustershell** addon role, it is possible to use Ansible inventory groups:

.. code-block:: text

  bootset -n @mg_computes -b disk

If some inventory parameters related to the host have been updated recently, it may be required to force files regeneration instead of simply modifying them. To do so, use:

.. code-block:: text

  bootset -n c001 -b osdeploy -f update

Also, on some "difficult" networks, system administrator may require to force static ip at boot. This can be achieved using:

.. code-block:: text

  bootset -n c001 -b osdeploy -f network

Or in combinaison with update, using comma separated:

.. code-block:: text

  bootset -n c001 -b osdeploy -f update,network

The tool is relatively verbose, and should provide all needed information on the fly on what it is doing.

Last part, regarding diskless. An image name need to be provided:

.. code-block:: text

  bootset -n c001 -b diskless -i myimage

This part should be covered in a diskless related role, and is not in the scope of this role.

**iPXE chain**
""""""""""""""

PXE part of the **BlueBanquise** stack relies heavily on iPXE, and its chain mechanism. This chain has multiple purposes:

* Most important, it is verbose, and can be manually manipulated or followed (watching http server logs).
* It is flexible, and can adapt to nearly any configuration (disk boot, os deployment, diskless, ...).
* It can operate on all hardware, from server to laptop. It can even be started from USB or CD image for non PXE able systems.

Some steps may seems weird or unnecessary, but are here on purpose: verbosity and debug, as PXE part is always the trickiest.

Some vocabulary: in the following document, **chain* or **chaining** refers to the iPXE mechanism that download and execute a new file, after the current one.

Also, all files root is assumed */var/www/html/preboot_execution_environnement* on the next-server (the server on which this pxe_stack role has been deployed).

The whole process can be resumed in one detailed schema:

.. image:: /roles/core/pxe_stack/images/iPXE_chain.svg

To be macroscopic:

#. The remote host boot over PXE, in EFI/legacy-bios, using its own PXE/iPXE rom.
#. The dhcp deployed by BlueBanquise will provide the host with the **BlueBanquise** iPXE rom. This iPXE rom contains an EMBED script that will display the logo, get an ip from the dhcp server, show some information, and chain to file *convergence.ipxe*.
#. *convergence.ipxe* will simply get the current architecture. This operation cannot be done into the EMBED script has it needs some logic, that could bug. Sys admin need to easily debug this without the need to rebuild iPXE roms. Then iPXE chain to *nodes/${hostname}.ipxe* with *hostname* the hostname provided by the dhcp server.
#. *nodes/${hostname}.ipxe* will define all host dedicated parameters, and also what host should do: boot on disk, deploy os, or boot in diskless. Then iPXE chain to *equipment_profiles/${equipment-profile}.ipxe*, with *equipment-profile* a variable defined in the current file.
#. *equipment_profiles/${equipment-profile}.ipxe* contains the host equipment profile group parameters, like operating system, console, kernel parameters, etc. Then iPXE chain to *menu.ipxe*.
#. *menu.ipxe* will display a basic menu on screen, with default set to what node is expected to do (this was gathered in *nodes/${hostname}.ipxe*). Timeout is 10s by default before host execute the expected action. Then, iPXE chain to:

   * *osdeploy/${eq-distribution}_${eq-distribution-major-version}.ipxe* if host needs to deploy/redeploy its operating system. These osdeploy files are dynamic, and adapt to parameters gathered in host dedicated file and host equipment_profile file.
   * *diskless/images/${diskless-image}/boot.ipxe* if host needs to boot in diskless.
   * *sanboot --no-describe --drive 0x80* if host is legacy/bios/pcbios based. This is a simple command that boot on disk.
   * *bin/${arch}/grub2_efi_autofind.img* if host is EFI based. This grub2 image will look for a disk with a know operating system, and boot on it.

In case of an OS deployment, if this deployment succeed, in the post install script section, remote host will ask, using a curl command on its side and an CGI python script on server side (*/var/www/cgi-bin/bootswitch.cgi*), to boot next to disk. This CGI python script will simply edit *node/${hostname}.ipxe* file and change its default boot to **bootdisk**.

All files are manually editable. Also, note that an unregistered host (so no hostnames provided by the dhcp) will try to load *nodes/.ipxe* file. By default, this file will simply provide an iPXE shell, but system administrator can tune this file to specific purposes.

To follow the deployment process, simply tail -f logs of http server, and see the whole process occurring.

To be done
^^^^^^^^^^

- Issue when deploying ubuntu 18.04. Very long hang after packages check. Install continue after like 10 minutes of hang. Not blocking but boring...

Changelog
^^^^^^^^^

* 1.1.5: Update role to match $basearch, add status feat to bootset. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.4: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.1.2: Add support of major distribution version. Bruno <devel@travouillon.fr>
* 1.1.1: bootset.py refactoring. Adrien Ribeiro <adrien.ribeiro@atos.net>
* 1.1.0: Rewamped the whole role. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Add Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
