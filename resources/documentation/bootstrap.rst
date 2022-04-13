==============================
[Core] - Bootstrap base system
==============================

BlueBanquise can be used to deploy from a simple IT room for students, to High
Performance Computing clusters. Configuration is the same in both cases, only
size and specialized roles are different.

In this documentation, most of the time, we will refer to "servers", but any
kind of workstation will work the same way.

This documentation will cover the configuration of a very simple cluster:

.. image:: images/clusters/documentation_example_single_island.svg
   :align: center

More complex clusters are detailed later, once the generic part is done.

.. note::
   It is important to note that the documentation focus on main inventory parameters of the stack.
   However, **more features are available in the stack**. Read roles Readme files to learn
   more about each role capabilities.

The first step is to bootstrap the first management server/workstation of the
cluster.

This procedure mainly depend on the Linux distribution chosen. Please follow the
target system procedure, but first step is to download iso and write it on an
USB device to install manually first management node operating system.

.. image:: images/misc/linux_usb_stick.svg
   :align: center

Depending of your Linux distribution, choose the bootstrap steps to follow:

* :ref:`Bootstrap RHEL like system`
* :ref:`Bootstrap Ubuntu like system`
* :ref:`Bootstrap SUSE like system`

Bootstrap RHEL like system
==========================

In the following documentation, the RHEL logo will means "this part is dedicated
to RHEL like distributions", and so will concern the following distributions:

.. raw:: html

  <div style="padding: 6px;">
  <b>RHEL</b> <img src="_static/logo_rhel.png">, <b>CentOS</b> <img src="_static/logo_centos.png">, <b>RockyLinux</b> <img src="_static/logo_rocky.png">, <b>OracleLinux</b> <img src="_static/logo_oraclelinux.png">, <b>CloudLinux</b> <img src="_static/logo_cloudlinux.png">, <b>AlmaLinux</b> <img src="_static/logo_almalinux.png">
  </div><br><br>

Currently supported Linux RHEL like distributions are:

* Major version: 7
    * RHEL
    * CentOS
* Major version: 8
    * RHEL
    * CentOS
    * CentOS-Stream
    * RockyLinux
    * OracleLinux
    * CloudLinux (with external repositories)
    * AlmaLinux

.. note::
  In the following documentation, we will always use *redhat/8/x86_64/* or
  *redhat/7/x86_64/* when setting path. Adapt this to your target distribution
  and architecture.
  Distribution keywords supported are: **redhat**, **rhel**, **centos**,
  **rockylinux**, **oraclelinux**, **cloudlinux**, **almalinux**. All these 
  keywords are links to **redhat**.
  And supported architecture are **x86_64** or **arm64**.

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 2 Gb RAM
* >= 40 Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 2 Gb RAM (Anaconda PXE part needs a lot of RAM, once system is installed, can be reduced to 1Gb)
* >= 20 Gb HDD

OS installation
---------------

Simply write iso **directly** on USB stick like a binary image, do not use a
special tool. On Linux, use dd, on Microsoft Windows, use Win32DiskImager but only
version 0.9.5 (not above).

Then install the Linux operating system manually (boot on USB, etc).

It is recommended to only choose minimal install during packages selection
(core or minimal server), to reduce load and attack surface.
Also, it is **STRONGLY** recommended to let system in English (US), and only
set your keyboard and time zone to your country.

Create bluebanquise user
------------------------

Once system is installed and rebooted, login on it.
We will assume from here that you are using a sudo user. If using root user, 
remove sudo for each bellow commands.

Create the ``bluebanquise`` user manually:

.. code-block::

  sudo adduser bluebanquise

Set bluebanquise user as passwordless sudo able user:

.. code-block::

  echo 'bluebanquise ALL=(ALL:ALL) NOPASSWD:ALL' | sudo tee -a /etc/sudoers.d/bluebanquise

Bootstrap stack - online
------------------------

Login as bluebanquise user, and clone github repoitory:

.. code-block::

  sudo su bluebanquise
  cd $HOME
  git clone https://github.com/bluebanquise/bluebanquise.git

Review content of file ``bootstrap_input.sh``, and adjust to your needs, especially 
ISO to be used and ISO URL (default here is AlmaLinux).
Other defaults should be good for most users.

Then simply execute the ``bootstrap.sh`` script. The script will install needed system packages, 
download python needed dependencies and Ansible via pip, and download BlueBanquise and base OS 
packages and iso. Note that depending of your network connection, this step could take a while.

.. code-block::

  cd bluebanquise
  ./bootstrap.sh

Once script has executed, it is interesting to check repositories structure created.

Boot images include the installer system which starts the deployment after PXE
boot, while packages repositories include the software that will be installed
on the systems. On RHEL like systems, all is included in the original ISO.

Boot images and packages repositories structure follows a specific pattern,
which defaults to the major release version in the path:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/redhat/8/x86_64/os/


.. warning::
  This pattern parameters (distribution, version, architecture) must match
  the one provided in the **equipment_profile** file seen later.

You can see that 2 repositories were created:

* bluebanquise: contains bluebanquise packages
* os: contains OS iso content (will be used for PXE and base repository)

If all went well, you can proceed to next step: :ref:`[Core] - Configure BlueBanquise`

Bootstrap stack - offline
-------------------------

It is common with RedHat like operating system to perform offline clusters deployment.

BlueBanquise bootstrap script is able to use a local iso and a local repository folder as bootstrap source.

Login as bluebanquise user, and upload a copy of cloned github repoitory, assumed here bluebanquise-git.tar.gz, 
then extract it at bluebanquise user home folder:

.. code-block::

  sudo su bluebanquise
  cd $HOME
  tar xvzf bluebanquise-git.tar.gz

Create offline needed folder in bluebanquise home folder:

.. code-block::

  mkdir -p /home/bluebanquise/bluebanquise/offline_bootstrap/

Upload into this folder:

* OS main iso. You have to provide the stack the full main DVD iso (the one that contains BaseOS and AppStream full repositories.
Can be rhel-8.3-x86_64-dvd.iso, AlmaLinux-8.5-x86_64-dvd.iso, Rocky-8.5-x86_64-dvd1.iso, etc.).
* BlueBanquise el8 repository main folder (Assuming cluster is x86_64: http://bluebanquise.com/repository/releases/latest/el8/x86_64/bluebanquise).

After upload, you should have:

.. code-block::

  bluebanquise@localhost:~/ ls /home/bluebanquise/bluebanquise/offline_bootstrap/
  rhel-8.5-x86_64-dvd.iso
  bluebanquise

Edit then ``bootstrap_input.sh`` into bluebanquise main folder, and 
set ``REDHAT_8_OFFLINE`` to ``true``. Also set ``REDHAT_8_ISO`` to match iso name you provided.
Do not care about ``REDHAT_8_ISO_URL`` as it will be ignored in offline mode.

Execute then the bootstrap script.

.. code-block::

  cd $HOME/bluebanquise
  ./bootstrap.sh

.. note::
  After bootstrap, for your convenience, local repositories are kept 
  activated. They are however no more needed. If you wish to remove them, 
  delete file /etc/yum.repos.d/bootstrap.repo .

Once script has executed, it is interesting to check repositories structure created.

Boot images include the installer system which starts the deployment after PXE
boot, while packages repositories include the software that will be installed
on the systems. On RHEL like systems, all is included in the original ISO.

Boot images and packages repositories structure follows a specific pattern,
which defaults to the major release version in the path:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/redhat/8/x86_64/os/


.. warning::
  This pattern parameters (distribution, version, architecture) must match
  the one provided in the **equipment_profile** file seen later.

You can see that 2 repositories were created:

* bluebanquise: contains bluebanquise packages
* os: contains OS iso content (will be used for PXE and base repository)

If all went well, you can proceed to next step: :ref:`[Core] - Configure BlueBanquise`

Bootstrap Ubuntu like system
============================

.. raw:: html

  <div style="padding: 6px;">
  <b>Ubuntu</b> <img src="_static/logo_ubuntu.png">
  </div><br><br>

Currently supported Linux Ubuntu distributions are:

* Ubuntu 20.04

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 8 Gb RAM
* >= 40 Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 6 Gb RAM (PXE part needs a lot of RAM, once system is installed, can be reduced to 1Gb)
* >= 20 Gb HDD

OS installation
---------------

Simply write iso **directly** on USB stick like a binary image, do not use a
special tool. On Linux, use dd, on Microsoft Windows, use Win32DiskImager but only
version 0.9.5 (not above).

Then install the Linux operating system manually (boot on USB, etc).

It is recommended to only choose minimal install during packages selection
(core or minimal server), to reduce load and attack surface. Remember to 
ask for openssh-server installation.
Also, it is **STRONGLY** recommended to let system in English (US), and only
set your keyboard and time zone to your country.

Create bluebanquise user
------------------------

Once system is installed and rebooted, login on it.
We will assume from here that you are using a sudo user. If using root user, 
remove sudo for each bellow commands.

Create the ``bluebanquise`` user manually:

.. code-block::

  sudo adduser bluebanquise

Set bluebanquise user as passwordless sudo able user:

.. code-block::

  echo 'bluebanquise ALL=(ALL:ALL) NOPASSWD:ALL' | sudo tee -a /etc/sudoers.d/bluebanquise

Bootstrap stack
---------------

Login as bluebanquise user, and clone github repoitory:

.. code-block::

  sudo su bluebanquise
  cd $HOME
  git clone https://github.com/bluebanquise/bluebanquise.git

Review content of file ``bootstrap_input.sh``, and adjust to your needs, especially 
ISO to be used and ISO URL.
Other defaults should be good for most users.

Then simply execute the ``bootstrap.sh`` script. The script will install needed system packages, 
download python needed dependencies and Ansible via pip, and download BlueBanquise and base OS 
packages and iso. Note that depending of your network connection, this step could take a while.

.. code-block::

  cd bluebanquise
  ./bootstrap.sh

Once script has executed, it is interesting to check repositories structure created.

Boot images include the installer system which starts the deployment after PXE
boot, while packages repositories include the software that will be installed
on the systems. On Ubuntu systems, all is included in the original ISO.

Boot images and packages repositories structure follows a specific pattern,
which defaults to the major release version in the path:

.. code-block:: bash

                  Distribution      Version   Architecture      Repository
                        +               +       +                 +
                        |               +--+    |                 |
                        +-----------+      |    |      +----------+
                                    |      |    |      |
                                    v      v    v      v
       /var/www/html/repositories/ubuntu/20.04/x86_64/os/


.. warning::
  This pattern parameters (distribution, version, architecture) must match
  the one provided in the **equipment_profile** file seen later.

You can see that 2 repositories were created:

* bluebanquise: contains bluebanquise packages
* os: contains OS iso content (will be used for PXE and base repository)

Also, you can see that iso was added along repositories. Raw ISO is needed during PXE process.

If all went well, you can proceed to next step: :ref:`[Core] - Configure BlueBanquise`

Bootstrap SUSE like system
==========================

SLES 15
-------

Notes:

* To use SLES 15 you will require an active SLES subscription to receive updates.
* SLES 15 SP3 is used in the example code blocks below - adjust to your chosen service pack.

After installing the OS the first step requires configuring RMT to mirror the SLES repositories. Make sure you have at least 80GB available to mirror the repositories.

.. code-block:: bash

  zypper install rmt-server yast2-user rsync
  systemctl start mariadb
  systemctl enable mariadb
  /usr/bin/mysqladmin -u root password suitable_password_here
  yast2

From the yast2 interface select RMT from the menus and enter the required information which includes your SLES proxy ID which you can find from your SUSE online account.

Once configured run:

.. code-block:: bash

  rmt-cli sync

To list all available repositories that you can mirror run:

.. code-block:: bash

  rmt-cli products list --all

The minimum SLES 15 repositories that you need to mirror are:

* Basesystem Module
* Desktop Applications Module
* Development Tools Module
* HPC Module
* Server Applications Module
* SUSE Linux Enterprise High Performance Computing
* SUSE Linux Enterprise Server
* SUSE Package Hub
* Web and Scripting Module

Each repository has a unique ID number that you can use with the ``rmt-cli`` command to mirror:

.. code-block:: bash

  rmt-cli products enable ID_NUMBER

Once you have enabled the repositories above you can then sync the repositories like so:

.. code-block:: bash

  rmt-cli mirror all

The repositories will be downloaded to: ``/var/lib/rmt/public/repo``.

Now you can create the BlueBanquise repository directories like so:

.. code-block:: bash

  mkdir -p /srv/www/htdocs/repositories/sles/15.3/x86_64/os
  cd /srv/www/htdocs/repositories/sles/15.3/x86_64
  ln -s /var/lib/rmt/public/repo/SUSE/Backports/SLE-15-SP3_x86_64/standard SLE-Backports
  ln -s /var/lib/rmt/public/repo/SUSE/Products/SLE-Module-Basesystem/15-SP3/x86_64/product SLE-Module-Basesystem
  ln -s /var/lib/rmt/public/repo/SUSE/Updates/SLE-Module-Basesystem/15-SP3/x86_64/update SLE-Module-Basesystem-Updates
  ln -s /var/lib/rmt/public/repo/SUSE/Products/SLE-Module-Desktop-Applications/15-SP3/x86_64/product SLE-Module-Desktop-Applications
  ln -s /var/lib/rmt/public/repo/SUSE/Updates/SLE-Module-Desktop-Applications/15-SP3/x86_64/update SLE-Module-Desktop-Applications-Updates
  ln -s /var/lib/rmt/public/repo/SUSE/Products/SLE-Module-Development-Tools/15-SP3/x86_64/product SLE-Module-Development-Tools
  ln -s /var/lib/rmt/public/repo/SUSE/Updates/SLE-Module-Development-Tools/15-SP3/x86_64/update SLE-Module-Development-Tools-Updates
  ln -s /var/lib/rmt/public/repo/SUSE/Products/SLE-Module-HPC/15-SP3/x86_64/product SLE-Module-HPC
  ln -s /var/lib/rmt/public/repo/SUSE/Updates/SLE-Module-HPC/15-SP3/x86_64/update SLE-Module-HPC-Updates
  ln -s /var/lib/rmt/public/repo/SUSE/Products/SLE-Module-Packagehub-Subpackages/15-SP3/x86_64/product SLE-Module-Packagehub-Subpackages
  ln -s /var/lib/rmt/public/repo/SUSE/Updates/SLE-Module-Packagehub-Subpackages/15-SP3/x86_64/update SLE-Module-Packagehub-Subpackages-Updates
  ln -s /var/lib/rmt/public/repo/SUSE/Products/SLE-Module-Server-Applications/15-SP3/x86_64/product SLE-Module-Server-Applications
  ln -s /var/lib/rmt/public/repo/SUSE/Updates/SLE-Module-Server-Applications/15-SP3/x86_64/update SLE-Module-Server-Applications-Updates

Populate the OS repository:

.. code-block:: bash

  mount SLE-15-SP3-Full-x86_64-GM-Media1.iso /mnt
  rsync -av /mnt/ /srv/www/htdocs/repositories/sles/15.3/x86_64/os/
  umount /mnt

Add repositories to ``~/bluebanquise/inventory/group_vars/all/general_settings/repositories.yml``:

.. code-block::

  repositories:
    - os
    - bluebanquise
    - SLE-Backports
    - SLE-Module-Basesystem
    - SLE-Module-Basesystem-Updates
    - SLE-Module-Development-Tools
    - SLE-Module-Development-Tools-Updates
    - SLE-Module-Development-Tools
    - SLE-Module-Development-Tools-Updates
    - SLE-Module-Desktop-Applications
    - SLE-Module-Desktop-Applications-Updates
    - SLE-Module-HPC
    - SLE-Module-HPC-Updates
    - SLE-Module-Packagehub-Subpackages
    - SLE-Module-Packagehub-Subpackages-Updates
    - SLE-Module-Python2
    - SLE-Module-Python2-Updates
    - SLE-Module-Server-Applications
    - SLE-Module-Server-Applications-Updates

-------------

It is now time to configure BlueBanquise.
