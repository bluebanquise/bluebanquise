Diskless
--------

Description
^^^^^^^^^^^

This role provides needed tools to deploy a basic diskless cluster.

Two type of images are available:

* Livenet images are full ram images, without persistance but need less infrastructure.
* NFS images are full nfs rw images, with psersistance, very simple to use, but need more infrastructure.

It is important to understand that this role is independant of the pxe_stack core role, and so each tools do not communicate.

Validated on RHEL8.

Instructions
^^^^^^^^^^^^

1. Apply your playbook with the "diskless" role activated (see *Example playbook* part):

2. Copy the kernels in /boot you want to use for your images.

.. code-block:: text

  cp /boot/<kernels to use for diskless nodes> /var/www/html/preboot_execution_environment/diskless/kernels/ 

3. Launch *disklessset* and verify that the kernels are present in the tool, then quit.

.. code-block:: text

  # disklessset
  BlueBanquise Diskless manager
   1 - List available kernels
   2 - Generate a new initramfs
   3 - Generate a new diskless image
   4 - Manage/list existing diskless images
   5 - Remove a diskless image
  -->: 1
  [INFO] Loading kernels from /var/www/html/preboot_execution_environment/diskless/kernels/
  
  Available kernels:
    │
    └── vmlinuz-4.18.0-193.6.3.el8_2.x86_64

4. Launch *disklessset* and ask an initramfs creation for this kernel

.. code-block:: text

  # disklessset
  BlueBanquise Diskless manager
   1 - List available kernels
   2 - Generate a new initramfs
   3 - Generate a new diskless image
   4 - Manage/list existing diskless images
   5 - Remove a diskless image
  -->: 2
  [INFO] Loading kernels from /var/www/html/preboot_execution_environment/diskless/kernels/
  
  Select kernel:
   1 - vmlinuz-4.18.0-193.6.3.el8_2.x86_64
  -->: 1

5. Using *disklessset*, verify that this creation went well: "initiramfs present" must now be present after the kernel.

.. code-block:: text

  # disklessset
  BlueBanquise Diskless manager
   1 - List available kernels
   2 - Generate a new initramfs
   3 - Generate a new diskless image
   4 - Manage/list existing diskless images
   5 - Remove a diskless image
  -->: 1
  [INFO] Loading kernels from /var/www/html/preboot_execution_environment/diskless/kernels/
  
  Available kernels:
      │
      └── vmlinuz-4.18.0-193.6.3.el8_2.x86_64 - initramfs present

6. Launch *disklessset* and create the livenet image. The command will guide you from here.

.. code-block:: text
  
  # disklessset
  BlueBanquise Diskless manager
   1 - List available kernels
   2 - Generate a new initramfs
   3 - Generate a new diskless image
   4 - Manage/list existing diskless images
   5 - Remove a diskless image
  -->: 3
  
  Starting new image creation phase.
  Many questions will be asked, a recap will be provided before starting procedure.


Select livenet image:

.. code-block:: text

  Select image type:
   1 - nfs
   2 - livenet
  -->: 2
  [INFO] Loading kernels from /var/www/html/preboot_execution_environment/diskless/kernels/

Select the kernel you want to use wit this image from the list of available kernels:


.. code-block:: text

  Select kernel:
   1 - vmlinuz-4.18.0-193.6.3.el8_2.x86_64
  -->: 1
  Please enter image name ?
  -->: livenet1
  Please enter clear root password of the new image: root
  [INFO] Entering livenet dedicated part.
 
Choose a standard image, and give a size.

.. code-block:: text

  Please select livenet image generation profile:
   1 - Standard: core (~1.2Gb)
   2 - Small: openssh, dnf and NetworkManager (~248Mb)
   3 - Minimal: openssh only (~129Mb)
  -->: 1
  Please choose image size (e.g. 5G):
  (supported units: M=1024*1024, G=1024*1024*1024)
  -->: 5G

Check that everything is alright before continuing:

.. code-block:: text

  Do you want to create a new livenet image with the following parameters:
    Image name:           livenet1
    Kernel version:       vmlinuz-4.18.0-193.6.3.el8_2.x86_64
    Root password:        root
    Image profile:        1
    Image size:           5120M
  Confirm ? Enter yes or no: yes
  [INFO] Cleaning and creating image folders.
  [INFO] Generating new ipxe boot file.
  [INFO] Creating empty image file, format and mount it.
  5242880+0 records in
  5242880+0 records out
  5368709120 bytes (5.4 GB, 5.0 GiB) copied, 10.3195 s, 520 MB/s
  meta-data=/root/diskless/workdir//LiveOS/rootfs.img isize=512    agcount=4, agsize=327680 blks
           =                       sectsz=512   attr=2, projid32bit=1
           =                       crc=1        finobt=1, sparse=1, rmapbt=0
           =                       reflink=1
  data     =                       bsize=4096   blocks=1310720, imaxpct=25
           =                       sunit=0      swidth=0 blks
  naming   =version 2              bsize=4096   ascii-ci=0, ftype=1
  log      =internal log           bsize=4096   blocks=2560, version=2
           =                       sectsz=512   sunit=0 blks, lazy-count=1
  realtime =none                   extsz=4096   blocks=0, rtextents=0
  [INFO] Generating cache link for dnf.
  [INFO] Installing system into image.
  ...


7. Using the command *bootset*, set the image one node will use. 
   
.. code-block:: text

  # bootset -n c001 -b diskless -i livenet1


The -n parameter can be a nodeset.

8. Reboot the diskless node to make it boot onto the new image.


* Example Playbook

.. code-block:: text

  - hosts: mngt0-1
    roles:
      - pxe_stack
      - diskless

To be done
^^^^^^^^^^

Clean code, add more error detection, and more verbosity.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
