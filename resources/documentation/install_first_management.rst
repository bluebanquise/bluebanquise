=================================
[Core] - Install first management
=================================

First step is to install first management node manually.

Install operating system
========================

Currently supported Linux distribution are:

* RHEL 7, 8
* CentOS 7, 8

Install manually the operating system using parameters you need.

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 2 Gb RAM
* >= 24Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 512 Mb RAM (but >= 2Gb when PXE is occurring)
* >= 6Gb HDD

In this last configuration, DVD iso will be mounted from /dev/cdrom instead of
being copied to save space.

It is recommended to only choose minimal install during packages selection
(core or minimal server). Also, it is recommended to let system in English, and
only set your keyboard and time zone to your country.

Prepare for Ansible
===================

Repositories
------------

Once system is installed and rebooted, login on it.
We then need to prepare boot images and packages repositories.

Boot images include the installer system which starts the deployment after PXE
boot, while packages repositories include the software that will be installed
on the systems.

Boot images and packages repositories structure follows a specific pattern,
which defaults to the major release version in the path:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/centos/7/x86_64/os/

Note: this pattern parameters (distribution, version, architecture) must match
the one provided in the equipment_profile file seen later.

Note: we recommend to use the same directory path to later sync the Errata
published by upstream operating system vendor.

Obtain isos
^^^^^^^^^^^

RHEL
""""

Obtain DVD from Red Hat, using your subscription. Target iso are main DVD:

* rhel-8.3-x86_64-dvd.iso
* rhel-server-7.9-x86_64-dvd.iso
* ...

CentOS
""""""

Obtain DVD from one of the CentOS mirrors (for example
http://centos.crazyfrogs.org/). You need to grab the Everything DVD:

* CentOS-8.3.2011-x86_64-dvd1.iso
* CentOS-7-x86_64-Everything-2009.iso
* ...

Copy iso on system
^^^^^^^^^^^^^^^^^^

If on standard system
"""""""""""""""""""""

Mount iso and copy content to web server directory: (replace centos/7 by
centos/8, redhat/8, redhat/7, etc depending of your system)

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7/x86_64/os/
  mount CentOS-7-x86_64-Everything-2009.iso /mnt
  cp -a /mnt/* /var/www/html/repositories/centos/7/x86_64/os/
  restorecon -Rv /var/www/html/repositories/centos/7/x86_64/os

If in test VM
"""""""""""""

Simply mount iso from /dev/cdrom to save space:

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7/x86_64/os/
  mount /dev/cdrom /var/www/html/repositories/centos/7/x86_64/os/

Set os repository
^^^^^^^^^^^^^^^^^

Now, create first repository manually. Procedure is different between Centos 7
and 8.

Centos/RHEL 7
"""""""""""""

Create file */etc/yum.repos.d/os.repo* with the following content:

.. code-block:: text

  [os]
  name=os
  baseurl=file:///var/www/html/repositories/centos/7/x86_64/os/
  gpgcheck=0
  enabled=1

Centos/RHEL 8
"""""""""""""

Create file */etc/yum.repos.d/BaseOS.repo* with the following content:

.. code-block:: text

  [BaseOS]
  name=BaseOS
  baseurl=file:///var/www/html/repositories/centos/8/x86_64/os/BaseOS/
  gpgcheck=0
  enabled=1

Then create file */etc/yum.repos.d/AppStream.repo* with the following content:

.. code-block:: text

  [AppStream]
  name=AppStream
  baseurl=file:///var/www/html/repositories/centos/8/x86_64/os/AppStream/
  gpgcheck=0
  enabled=1

Both
""""

If you don't need the DVD iso anymore, umount it:

.. code-block:: bash

  umount /mnt

Now ensure repository is available:

.. code-block:: bash

  yum repolist

BlueBanquise
^^^^^^^^^^^^

Download BlueBanquise rpms from official repository.

Go to https://bluebanquise.com, go to repositories/download, and get the content
of the whole directory corresponding to your distribution and architecture.

Then copy this content into
/var/www/html/repositories/centos/7/x86_64/bluebanquise/ locally.

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7/x86_64/bluebanquise/
  cp -a /root/bluebanquise_from_web/* /var/www/html/repositories/centos/7/x86_64/bluebanquise/
  restorecon -Rv /var/www/html/repositories/centos/7/x86_64/bluebanquise

And create file */etc/yum.repos.d/bluebanquise.repo* with the following content:

.. code-block:: text

  [bluebanquise]
  name=bluebanquise
  baseurl=file:///var/www/html/repositories/centos/7/x86_64/bluebanquise/
  gpgcheck=0
  enabled=1

Install Ansible
---------------

Time to install Ansible.

RHEL/CentOS
^^^^^^^^^^^

Centos/RHEL 7
"""""""""""""

Install epel first, to get Ansible:

.. code-block:: bash

  yum install epel-release
  yum repolist

Then install Ansible:

.. code-block:: bash

  yum install ansible

And check Ansible is working:

.. code-block:: bash

  ansible --version

It must be **>= 2.9.13** .

Centos/RHEL 8
"""""""""""""

Install epel first, to get Ansible:

.. code-block:: bash

  dnf install epel-release
  dnf repolist

Then install Ansible:

.. code-block:: bash

  dnf install ansible

And check Ansible is working:

.. code-block:: bash

  ansible --version

It must be **>= 2.9.13** .

-------------

It is now time to Configure BlueBanquise.
