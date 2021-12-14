Diskless
--------

Description
^^^^^^^^^^^

This role provides needed tools to deploy a basic diskless cluster.

Two types of images are available:

* Livenet images are full ram images, without persistence, but need less infrastructure.
* NFS images are full nfs rw images, with persistence, very simple to use, but need more infrastructure.

It is important to understand that this role is independent of the pxe_stack core role, and so each tool do not communicate.

Validated on RHEL 8.
Python based.

A technical documentation is available on https://github.com/bluebanquise/bluebanquise/tree/master/resources/documentation/diskless

Set up the tool
^^^^^^^^^^^^^^^

Note: if using GPG keys (recommended), have a look at bottom of the readme to prevent a possible issue.

1. Apply your playbook with the "diskless" role activated (see *Example playbook* part).

2. Copy from /boot the kernels you want to use for your images:

.. code-block:: text

  cp /boot/vmlinuz-<kernel releases to use for diskless nodes> \
     /var/www/html/preboot_execution_environment/diskless/kernels/

3. Launch *disklessset* command and check that the software launches correctly:

.. code-block:: text


    ██████╗ ██╗███████╗██╗  ██╗██╗     ███████╗███████╗███████╗
    ██╔══██╗██║██╔════╝██║ ██╔╝██║     ██╔════╝██╔════╝██╔════╝
    ██║  ██║██║███████╗█████╔╝ ██║     █████╗  ███████╗███████╗
    ██║  ██║██║╚════██║██╔═██╗ ██║     ██╔══╝  ╚════██║╚════██║
    ██████╔╝██║███████║██║  ██╗███████╗███████╗███████║███████║
    ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝

             Entering BlueBanquise diskless manager

   > Diskless image management
   1 - Manage and create diskless images (need modules)
   2 - List available diskless images
   3 - Remove a diskless image
   4 - Clone a diskless image
   5 - Create an image from a parameters file
   6 - Manage kernel of a diskless image

   > Other actions
   7 - List available kernels
   8 - Generate a new initramfs

   9 - Clear a corrupted image (Use only as a last resort)
   10 - Exit

  At any time: (CTRL + c) => Return to this main menu.

  [+]  Select an action:
  -->:

You can add -i (info) or -d (debug) options to the disklessset command to get logs during the execution.

4. Check that the kernels you previously added are present in the tool:

.. code-block:: text

   > Diskless image management
   1 - Manage and create diskless images (need modules)
   2 - List available diskless images
   3 - Remove a diskless image
   4 - Clone a diskless image
   5 - Create an image from a parameters file
   6 - Manage kernel of a diskless image

   > Other actions
   7 - List available kernels
   8 - Generate a new initramfs

   9 - Clear a corrupted image (Use only as a last resort)
   10 - Exit

  At any time: (CTRL + c) => Return to this main menu.

  [+]  Select an action:
  -->: 7
  Available kernels:
      │
      └── vmlinuz-4.18.0-305.el8.x86_64 - missing initramfs-kernel-4.18.0-305.el8.x86_64
    
5. Generate a new initramfs for your kernel:

.. code-block:: text

    > Diskless image management
    1 - Manage and create diskless images (need modules)
    2 - List available diskless images
    3 - Remove a diskless image
    4 - Clone a diskless image
    5 - Create an image from a parameters file
    6 - Manage kernel of a diskless image

    > Other actions
    7 - List available kernels
    8 - Generate a new initramfs

    9 - Clear a corrupted image (Use only as a last resort)
    10 - Exit

    At any time: (CTRL + c) => Return to this main menu.

    [+]  Select an action:
    -->: 8

    [+] Select the kernel:
    1 - vmlinuz-4.18.0-305.el8.x86_64
    -->: 1

6. After initramfs generation, check that initramfs is present with the kernel:

.. code-block:: text

   > Diskless image management
   1 - Manage and create diskless images (need modules)
   2 - List available diskless images
   3 - Remove a diskless image
   4 - Clone a diskless image
   5 - Create an image from a parameters file
   6 - Manage kernel of a diskless image

   > Other actions
   7 - List available kernels
   8 - Generate a new initramfs

   9 - Clear a corrupted image (Use only as a last resort)
   10 - Exit

  At any time: (CTRL + c) => Return to this main menu.

  [+]  Select an action:
  -->: 7
  Available kernels:
      │
      └── vmlinuz-4.18.0-305.el8.x86_64 - initramfs present

Now the tool is ready to be used.

Manage and create diskless images with modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The diskless tool use modules for image creation. Because the tool is modular, new modules can be added for specific images.
By default 3 module are provided:

* livenet : Livenet images creation and management
* demo : A demonstration module to illustrate how the diskless tool works
* nfs : NFS images creation and management

Each modules has it's own features.

In the diskless main menu you can select the first option and select the module to use:

.. code-block:: text

   > Diskless image management
   1 - Manage and create diskless images (need modules)
   2 - List available diskless images
   3 - Remove a diskless image
   4 - Clone a diskless image
   5 - Create an image from a parameters file
   6 - Manage kernel of a diskless image

   > Other actions
   7 - List available kernels
   8 - Generate a new initramfs

   9 - Clear a corrupted image (Use only as a last resort)
   10 - Exit

  At any time: (CTRL + c) => Return to this main menu.

  [+]  Select an action:
  -->: 1

  [+] Select the module you want to use:
   1 - demo
   2 - livenet
   3 - nfs
  -->:

Livenet module
""""""""""""""

Entering the livenet module will prompt the following menu:

.. code-block:: text

   == Livenet image module ==

   1 - Generate a new livenet image
   2 - Mount an existing livenet image
   3 - Unount an existing livenet image
   4 - Resize livenet image

   Select an action
  -->:

In this menu you can do four actions:

* Generate a new livenet image : This will guide you in order to create a new livenet image to boot.
* Mount an existing livenet image : Mount a livenet image in order to make actions inside (install packages, ...). Livenet images are mounted inside /var/tmp/diskless/workdir/<image name>/mnt.
* Unount an existing livenet image : Unmount a mounted livenet image.
* Resize livenet image : Resize a livenet image operating system in order to adjust space taken into the ram.

When generating a new livenet image with the first option, you will have to give few parameters:

* The name you want for your image
* The password for your image
* The kernel to use
* The type of livenet image, by default there are 3 types of livenet images.
* The size of the image (It will take this size into ram memory). Please be aware to give enough memory for your operating system.

NFS module
""""""""""

Entering the livenet module will prompt the following menu:

.. code-block:: text

   == NFS image module ==

   1 - Generate a new nfs staging image
   2 - Generate a new nfs golden image from a staging image
   3 - Manage nodes of a golden image

   Select an action
  -->:

In this menu you can do 3 actions:

* Generate a new NFS staging image : A staging image is the base image. You must not boot onto a staging image but firstly create a golden image from it and boot on the golden image specific filesystem (Created with option 3).
* Generate a new NFS golden image from a staging image : Create a golden image from previously created staging image.
* Manage nodes of a golden image: Create a specific file system for each node for a specific golden image. After adding a node to a golden image via this option, you can boot the node onto the golden image.

Demo module
"""""""""""

You can create demo images to test the diskless tool.
Corrupt a demo image will allow you to test the cleaning mechanism of the tool. In fact, a corrupted demo image will be cleaned when listing images.
Demo module can also be used by developers to understand module creation.

List available diskless images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This menu will allow you to view created and in creation diskless images with their attributes:

.. code-block:: text

   > Diskless image management
   1 - Manage and create diskless images (need modules)
   2 - List available diskless images
   3 - Remove a diskless image
   4 - Manage kernel of a diskless image

   > Other actions
   5 - List available kernels
   6 - Generate a new initramfs

   7 - Clear a corrupted image
   8 - Exit

  At any time: (CTRL + c) => Return to this main menu.

   Select an action:
  -->: 2

     [IN_CREATION]
   • Image name: nfsimg1
     Installation pid: 28716

     [CREATED]
   • Image name: livenetimg1
       ├── IMAGE_DIRECTORY: /var/www/html/preboot_execution_environment/diskless/images/livenetimg1
       ├── kernel: vmlinuz-4.18.0-147.el8.x86_64
       ├── image: initramfs-kernel-4.18.0-147.el8.x86_64
       ├── password: $6$fUfb9XQ2RCxHO15O$TubY.EQ44IP1xxbZYdpQl1mDrpyz1SoZ8eW3ApK3IoadfC7KjHCej7UtCjBLTbX9UBZm5rgKFhP1NfQUrIUxZ1
       ├── livenet_type: Type.STANDARD
       ├── livenet_size: 1500
       ├── is_mounted: False
       ├── image_class: LivenetImage
       └── creation_date: 2020-10-21

Remove a diskless image
^^^^^^^^^^^^^^^^^^^^^^^

Simply choose and remove a previously created diskless image.

Clone a diskless image
^^^^^^^^^^^^^^^^^^^^^^

Clone an existing diskless image into another image.

Create an image from a parameters file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This option allows you to create an image without go through the questions phase. You can create the new image from a parameters file. The parameters file must follow a specific template. You can take example from the "image_data.yml" files generated when created images from questions (The usual way). You have to put a clear password in the given parameters file and follow these templates: 

Template of parameters file to create a livenet image:
""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: text

  image_data:

      name: livenet1
      password: root
      kernel: vmlinuz-4.18.0-305.el8.x86_64
      livenet_type: Type.CORE
      livenet_size: 700
      ssh_pub_key: /root/.ssh/id_rsa.pub
      selinux: False
      optimize: False
      additional_packages: ['gzip']
      release_version: 8
      image_class: LivenetImage

ssh_pub_key, additional_packages, and release_version are optional.

Example of parameters file to create a nfs staging image:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: text

  image_data:

      name: nfs1
      password: root
      kernel: vmlinuz-4.18.0-305.el8.x86_64
      additional_packages: ['gzip']
      release_version: 8
      image_class: NfsStagingImage
    
additional_packages, and release_version are optional.

Don't put your parameters file in the disklessset tool directories, just load it with the tool option 5.

Manage kernel of a diskless image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change the kernel of an existing diskless image.

List available kernels
^^^^^^^^^^^^^^^^^^^^^^

Show available kernels for diskless images. Kernels can be added in /var/www/html/preboot_execution_environment/diskless/kernels.

If the kernel has a generated initramfs file (Example with one kernel):

.. code-block:: text

  Available kernels:
      │
      └── vmlinuz-4.18.0-147.el8.x86_64 - initramfs present

If the kernel hasn't a generated initramfs file:

.. code-block:: text

  Available kernels:
      │
      └── vmlinuz-4.18.0-147.el8.x86_64 - missing initramfs-kernel-4.18.0-147.el8.x86_64

Generate a new initramfs
^^^^^^^^^^^^^^^^^^^^^^^^

Generate a new initramfs file for a kernel.

Clear a corrupted image
^^^^^^^^^^^^^^^^^^^^^^^

Remove totally a diskless image with a brutal method.
You must use this option only if the image is corrupted or there are non-compliant files.

Exit
^^^^

Exist the diskless tool.

Boot a diskless image
^^^^^^^^^^^^^^^^^^^^^

You can use the bootset bluebanquise tool to setup the boot image for a specific machine:

.. code-block:: text

  # bootset -n <machine name> -b diskless -i <diskless image name>

Please refer you to bootset documentation for further information.

Customizing Livenet image
^^^^^^^^^^^^^^^^^^^^^^^^^

The image name used in the examples below is *space_image*.

The disklessset tool allows to customize livenet images before booting them,
by mounting images and providing simple chroot inventory. System administrator 
can then tune or execute playbooks inside images.
This step also saves time on the execution of playbooks on booted diskless nodes.

To mount a livenet image in order to customize it, go to livenet module and select "mount livenet image".

It is now possible to copy files, install rpms, or tune any aspects of the 
mounted image.

To execute an Ansible playbook into the image, generate a new playbook 
with the following head:

.. code-block:: yaml

  - name: Computes diskless playbook
    hosts: /var/tmp/diskless/workdir/{{ image_name }}/mnt
    connection: chroot
    vars:
      j2_current_iceberg: iceberg1                #<<< UPDATE IF NEEDED
      j2_node_main_network: ice1-1                #<<< UPDATE
      start_service: false
      image_equipment_profile: equipment_typeC    #<<< UPDATE
      ep_firewall: false
  
    pre_tasks:
      - name: Add current host to defined equipment_profile
        add_host:
          hostname: "{{ inventory_hostname }}"
          groups: "{{ image_equipment_profile }}"
        tags:
          - always
  
    roles:
    # ADD HERE YOUR ROLES

Now, update the needed values in this file:

* **j2_current_iceberg**: Except if you are using multiple icebergs advanced feature, you should let this to `iceberg1`.
* **j2_node_main_network**: Set here your main network to be used. This will allow the roles to determine the services ip to bind to.
* **image_equipment_profile**: Set here your equipment_profile to be used. This will allow the roles to determine key values, for example find the repositories path to be used (distribution version, etc).

And add your desired roles under **roles:** in the file, like for 
any standard playbook.

Then execute it into the mounted image using the following command:

.. code-block:: text

  ansible-playbook computes.yml \
  -i /etc/bluebanquise/inventory/ -i /etc/bluebanquise/internal/ -i /var/tmp/diskless/workdir/space_image/inventory/ \
  --skip-tags identify -e "image_name=space_image"

Notes:

* The multiple `-i` defines Ansible inventories to gather. By default, in BlueBanquise, the first two inventories are used. We simply add the third one, corresponding to the mounting point.
* The `-e` (extra vars) are here to specify to the stack which iceberg and main network are to be used in the configuration of the node. (System cannot know on which nodes the image will be used).
* The `--skip-tags identify` prevents hostname and static ip to be set, since the image should be generic for multiple hosts.
* Firewall does not work properly in a chroot environment. Variable ep_firewall must be set to false when executing playbook in the chrooted image. If there are firewall related changes to be applied on the image, execute playbook with ep_firewall set to false in the playbook (but keep it true in the inventory) in the chrooted image. Once node is booted in diskless, execute again the playbook with ep_firewall to true (note: you can focus on firewall tasks only at this point using the firewall tag).

Before closing, also remember to clean dnf cache into the image chroot to save space.

.. code-block:: text

  # dnf clean all --installroot /var/tmp/diskless/workdir/space_image/mnt/

Now, using df command, check used space of the image, to resize it later if whished.

Using disklessset now, choose option 2 to unmount the image and squashfs it again.

It is possible now to use the tool to resize image, to reduce it to the desired value (to save ram on target host).
Always keep at least 100MB in / for temporary files and few logs generated during run.

Example Playbook
^^^^^^^^^^^^^^^^

.. code-block:: text

  - hosts: mngt0-1
    roles:
      - pxe_stack
      - diskless


Once the node is started, run your playbook with your roles.
It is important to synchronize your node's time by running the time role.

GPG keys issues
^^^^^^^^^^^^^^^

If using GPG keys check (recommended), in order to use the tool, you must define gpgkey option in inventories list.

If not specified, the following message might appear during images creation:

.. code-block:: text

  [INFO] Installing system into image.
  Unable to detect release version (use '--releasever' to specify release version)

  You have enabled checking of packages via GPG keys. This is a good thing.
  However, you do not have any GPG public keys installed. You need to download
  the keys for packages you wish to install and install them.
  You can do that by running the command:
      rpm --import public.gpg.key  


  Alternatively, you can specify the url to the key you would like to use
  for a repository in the 'gpgkey' option in a repository section and DNF
  will install it for you.

  For more information contact your distribution or package provider.

  Problem repository: [AppStream]  
  [...]
  [INFO] Setting password into image.
  Traceback (most recent call last):
    File "/usr/bin/disklessset", line 435, in <module>
      with open(os.path.join(installroot, 'etc/shadow'), "r+") as ff:
  FileNotFoundError: [Errno 2] No such file or directory: '/var/tmp/diskless/workdir/test1/mnt/etc/shadow'

To solve this, simply set gpgkey file location in the inventory:

.. code-block:: yaml

  repositories:
    - bluebanquise
    - { name: 'os', gpgcheck: True, gpgkey: "file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial" }

And update management server repositories (has these are used to generate the base image):

.. code-block:: text

  # ansible-playbook playbooks/managements.yml --tags repositories_client --limit management1 --diff
  [...]
  TASK [repositories_client : yum_repository █ Setting OS repositories] *************************************************
  Tuesday 22 September 2020  10:29:40 -0400 (0:00:00.502)       0:00:04.044 *****
  --- before: /etc/yum.repos.d/CentOS-Base.repo
  +++ after: /etc/yum.repos.d/CentOS-Base.repo
  @@ -2,5 +2,6 @@
   baseurl = http://10.10.0.1/repositories//centos/8/$basearch/os/BaseOS
   enabled = 1
   gpgcheck = 1
  +gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
   name = BaseOS gen by Ansible


  changed: [management1] => (item={'name': 'os', 'gpgcheck': True, 'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial', 'file': 'CentOS-Base', 'repoid': 'BaseOS'})
  --- before: /etc/yum.repos.d/CentOS-AppStream.repo
  +++ after: /etc/yum.repos.d/CentOS-AppStream.repo
  @@ -2,5 +2,6 @@
   baseurl = http://10.10.0.1/repositories//centos/8/$basearch/os/AppStream
   enabled = 1
   gpgcheck = 1
  +gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
   name = AppStream gen by Ansible

  changed: [management1] => (item={'name': 'os', 'gpgcheck': True, 'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial', 'file': 'CentOS-AppStream', 'repoid': 'AppStream'})

Then image creation should not face GPG key issue anymore.

To be done
^^^^^^^^^^

* Make a livenet image autosizing system (Taken automatically the minimum size for operating system in ram).
* Make a diskless conf file in /etc in order to configure : Autoclean on/off, Directories location (images, kernels, ...).

Changelog
^^^^^^^^^
* 1.3.1: Remove script from role and rely on package. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Role update. David Pieters <davidpieters22@gmail.com>
* 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>, Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
