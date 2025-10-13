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

Infiniband PXE boot
-------------------

.. note::
  Inspired from https://github.com/bluebanquise/bluebanquise/issues/825, by @capitn198

Context:
  - RHEL 8.7
  - bluebanquise 1.5.2
  - Hardware:
    - Motherboard: Gigabyte H263-S63
    - CPU: 2x Intel(R) Xeon(R) Gold 5418Y
    - 1x dedicated Ethernet port for BMC (not for OS)
    - IB HBA: 1x Mellanox Technologies MT2892 Family [ConnectX-6 Dx] HDR
    - 1x IB switch MQM8790-HS2X_Ax unmanaged

Diskfull
^^^^^^^^

Need some tweak in the configuration of the inventory.

In the node definition (ex: ``inventory/cluster/compute.yml``):

.. code-block:: yaml

  hosts:
    n01:
      bmc:
        name: n01-bmc
        ip4: 192.168.170.1
        mac: 74:56:3c:5b:93:e5
        network: admin1-2
      network_interfaces:
        - interface: ib0
          ip4: 192.168.169.1
          dhcp_client_identifier: 20:10:70:fd:03:00:a2:46:64 # Request from OS
          mac: 10:70:fd:a2:46:64 # Request from PXE
          network: admin1-1
          type: infiniband

To obtain card GUID and MAC, use the following command:

.. code-block:: text

  #$ flint -d lid-5 q|grep Base
  Base GUID:             1070fd0300a24664        4
  Base MAC:              1070fda24664            4

Note that the MAC address used during PXE is ``10:70:fd:a2:46:64`` and during OS startup is ``20:10:70:fd:03:00:a2:46:64``.
That's why we have 2x MAC addresses for the same interface.
As mentioned in the comment, the ``flint`` command can be used to get these MAC addresses (add the ``20:`` prefix for the OS MAC in my situation).

We need also to adjust the equipment hardware definition like:

.. code-block:: yaml

  hw_ipxe_platform: efi
  hw_ipxe_driver: snponly
  hw_kernel_parameters: nomodeset bootdev=ib0 ksdevice=ib0 net.ifnames=0 biosdevname=0 rd.neednet=1 rd.bootif=0 rd.driver.pre=mlx5_ib,mlx4_ib,ib_ipoib ip=ib0:dhcp rd.net.dhcp.retry=10 rd.net.timeout.iflink=60 rd.net.timeout.ifup=80 rd.net.timeout.carrier=80

With this configuration it is possible to install the node through the IB link and then apply configuration with ansible-playbook.

Diskless
^^^^^^^^

The same changes made in the previous section (diskfull) must be done.

With diskless I was obliged to generate the initramfs manually otherwise the node won't boot.
The initrd generated by ``bluebanquise-diskless`` was not working.

Once the image is loaded on a node via NFS with the ``bluebanquise-diskless`` utility, I made (the name of my image is "test"):

.. code-block:: text

  # Tell the OS to do DHCP on ib0 at boot time
  # can be done in an ansible role
  $ cat /etc/sysconfig/network-scripts/ifcfg-ib0
  CONNECTED_MODE=no
  TYPE=InfiniBand
  PROXY_METHOD=none
  BROWSER_ONLY=no
  BOOTPROTO=dhcp
  DEFROUTE=yes
  IPV4_FAILURE_FATAL=no
  IPV6INIT=yes
  IPV6_AUTOCONF=yes
  IPV6_DEFROUTE=yes
  IPV6_FAILURE_FATAL=no
  IPV6_ADDR_GEN_MODE=eui64
  NAME=ib0
  DEVICE=ib0
  ONBOOT=yes

  # Generate initramfs with the IB drivers inside
  $ dnf install dracut-live
  $ echo 'install mlx5_core /sbin/modprobe --ignore-install mlx5_core; /sbin/modprobe mlx5_ib; /sbin/modprobe ib_ipoib' >> /etc/modprobe.d/mlx.conf
  $ echo 'add_drivers+="mlx5_ib ib_ipoib"' > /etc/dracut.conf.d/mlx.conf
  $ /usr/bin/dracut --xz -v -a network -a base -a nfs --force-add livenet --add-drivers xfs --no-hostonly --nolvmconf -f

Then use ``bluebanquise-disklessset`` to request an update on the node kernel, and reboot the node to finish preparing reference/golden image.

With this initramfs, the diskless OS boots fine.

Manual PXE boot
---------------

.. note::
  Inspired from https://github.com/bluebanquise/bluebanquise/issues/825, by @capitn198

Some nodes are difficult or impossible to natively boot over PXE (PXE not supported, impossible to find option in BIOS, boot on non standard cards like Infiniband cards, etc.).
In such situation, it is possible to use a trick:

- If the node has a BMC embed, simply load the BlueBanquise iPXE iso (from /var/www/html/pxe/bin/x86_64/standard_efi.iso) into the BMC's virtual drive, and boot on it.
This will start the iPXE boot process, and so use local network interfaces to grab an ip from the DHCP and boot.

- If the node does not have a BMC, you can create a bootable USB image that includes the EFI roms (you can find EFI roms into /var/lib/tftpboot/x86_64/ folder), write it on a USB disk, and have the system boot on USB.

