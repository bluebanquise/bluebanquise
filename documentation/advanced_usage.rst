==============
Advanced usage
==============

Networking
==========

VLAN PXE boot
-------------

.. note::
  Inspired from https://github.com/bluebanquise/bluebanquise/issues/831, by @GaelBil

In many cluster we want (or have to) setup different VLAN for server and their BMC.
In case of **shared port for BMC and server** the current situation is quite complex to deal with.

To explain the situation I will give an example.
My VLAN ID are:

- 10 for server
- 20 for BMC

My management servers have an interface on each VLAN.
The default VLAN is not permitted.

In the current situation I have to configure my switch to tag the VLAN 10 by default and to permit the transport of the VLAN 20 (trunk).
This way, when my server will boot, its DHCP request will be tagged with the VLAN 10 and it will be able to perform a PXE / iPXE boot (or install).
The problem with this method is that I cannot access my BMC. The obvious workaround is to use a range of IP for a DHCP to get a temporary IP for the BMC, then set the VLAN directly on the BMC. For that you may need to declare your BMC twice in your inventory.

It is howerver possible to simplify the process by changing few things.

On the switch
^^^^^^^^^^^^^

First you have to configure your switch to tag the VLAN 20 by default. This way you will be able to access your BMC easily without a temporary IP.

On server bios
^^^^^^^^^^^^^^

Obviously in this situation, your server will not be able to get an IP address (because DHCP request go through the VLAN 20).
So you need to configure the VLAN 10 directly in the BIOS through the BMC.
You can use different tools depending on the brand of your server :

- redfish
- gbtutility (for gigabyte)
- onecli (for lenovo)
- ...

After that, your server will be able to performe a PXE.

iPXE vlan
^^^^^^^^^

Now that you are able to perform a PXE, you need to recompile your iPXE binary with the VLAN support enabled.

.. code-block:: text

  git clone git://git.ipxe.org/ipxe.git
  cd ipxe/src
  sed -i 's///#define VLAN_CMD/#define VLAN_CMD/' config/general.h
  sed -i 's/.*PING_CMD.*/#define PING_CMD/' config/general.h
  sed -i 's/.*CONSOLE_CMD.*/#define CONSOLE_CMD/' config/general.h
  sed -i 's/.*CONSOLE_FRAMEBUFFER.*/#define CONSOLE_FRAMEBUFFER/' config/console.h
  sed -i 's/.*IMAGE_ZLIB.*/#define IMAGE_ZLIB/' config/general.h
  sed -i 's/.*IMAGE_GZIP.*/#define IMAGE_GZIP/' config/general.h
  sed -i 's/.*DIGEST_CMD.*/#define DIGEST_CMD/' config/general.h

Create a small iPXE script canned myscript.ipxe:

.. code-block:: text

  #!ipxe

  vcreate --tag 10 net0

  :rdhcp
  dhcp net0-123&& goto rboot || goto rdhcp

  :rboot
  chain http://<managementserverIP>/preboot_execution_environment/convergence.ipxe || goto rboot

Then recompile you iPXE binary:

.. code-block:: text

  make bin-x86_64-efi/snponly.efi EMBED=myscript.ipxe DEBUG=intel,dhcp,vesafb
  make bin/undionly.kpxe EMBED=myscript.ipxe DEBUG=intel,dhcp,vesafb

And add these custom iPXE roms into tftp folder:

.. code-block:: text
  
  cp bin-x86_64-efi/snponly.efi /var/lib/tftpboot/custom_vlan_snponly.efi
  cp bin-x86_64-efi/undionly.kpxe /var/lib/tftpboot/custom_vlan_undionly.kpxe

To be sure that your server download this binary, add a variable in the **hardware** profile group of the targer servers:

.. code-block:: yaml

  hw_pxe_filename: "custom_vlan_snponly.efi"

And re-apply dhcp_server role to take this new parameter into account.

Osdeploy
^^^^^^^^

If you perform **osdeploy** operation, you need to add the vlan definition at kernel command line parameters in your **os** profile group:

.. code-block:: yaml

  os_kernel_parameters: vlan=eno1.10:eno1

Note that this implies you know how your kernel is going to name your primary server NIC. You may try to launch a live of the OS manually first to obtain this from a shell.

You also need to add a specific parameter for the auto installation file. For kickstart (RHEL based), define the following variable into your **os** profile group (as this is an OS parameter this time):

.. code-block:: yaml

  os_autoinstall_custom_content: |
    network --bootproto=dhcp --ipv6=auto --activate --vlanid 10

And re-apply pxe_stack role to take these new parameters into account.
