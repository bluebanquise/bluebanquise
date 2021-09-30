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

Note also that the documentation focus on main inventory parameters of the stack.
However, more features are available in the stack. Read roles Readme to learn
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

Currently supported and tested Linux RHEL like distributions are:

* Major version: 7
    * RHEL
    * CentOS
* Major version: 8
    * RHEL
    * CentOS
    * CentOS-Stream
    * RockyLinux
    * OracleLinux
    * CloudLinux
    * AlmaLinux

.. note::
  In the following documentation, we will always use *redhat/8/x86_64/* or
  *redhat/7/x86_64/* when setting path. Adapt this to your target distribution
  and architecture.
  Distribution keywords supported are: **redhat**, **rhel**, **centos**,
  **rockylinux**, **oraclelinux**, **cloudlinux**, **almalinux**.
  And supported architecture are **x86_64** or **arm64**.

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 2 Gb RAM
* >= 40 Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 2 Gb RAM (Anaconda PXE part needs a lot of RAM)
* >= 20 Gb HDD

ISOs to be used
^^^^^^^^^^^^^^^

Obtain the main binary DVD from Red Hat, RockyLinux, etc. Naming is
similar to:

* rhel-8.3-x86_64-dvd.iso
* rhel-server-7.9-x86_64-dvd.iso
* CentOS-8.3.2011-x86_64-dvd1.iso
* CentOS-7-x86_64-Everything-2009.iso
* ...

You need to grab the ISO that contains all base repositories, so around the big
one of the list (> 6 Gb in general).

OS installation
---------------

Simply write iso **directly** on USB stick like a binary image, do not use a
special tool. On Linux, use dd, on Microsoft Windows, use Win32DiskImager but only
version 0.9.5 (not above).

Then install the Linux operating system manually (boot on USB, etc).

It is recommended to only choose minimal install during packages selection
(core or minimal server).
Also, it is **STRONGLY** recommended to let system in English (US), and only
set your keyboard and time zone to your country.

Repositories
------------

Once system is installed and rebooted, login on it.

We now need to prepare boot images and packages repositories.

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

.. note::
  The */var/www/html* path given here is an example, as it may vary depending of
  distribution used. What maters is the structure following this path.

.. warning::
  This pattern parameters (distribution, version, architecture) must match
  the one provided in the **equipment_profile** file seen later.

Copy iso on system
^^^^^^^^^^^^^^^^^^

Copy iso on system.
Then mount iso and copy content to web server directory: (replace redhat/8 by
redhat/7, centos/8, centos/7, rockylinux/8, etc depending of your system).

.. code-block:: bash

  mkdir -p /var/www/html/repositories/redhat/8/x86_64/os/
  mount rhel-8.3-x86_64-dvd.iso /mnt
  cp -a /mnt/* /var/www/html/repositories/redhat/8/x86_64/os/
  restorecon -Rv /var/www/html/repositories/redhat/8/x86_64/os

Set OS repository
^^^^^^^^^^^^^^^^^

Now, create first repository manually. Part of the procedure is different
between major versions, since base repositories were split in two with RHEL 8.

First step is to backup and clean current configuration:

.. code-block:: bash

  cp -a /etc/yum.repos.d /root/yum.repos.d_native

Then next step depends of the major version used:

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>7</b><br><br>

Create file */etc/yum.repos.d/os.repo* with the following content:

.. code-block:: text

  [os]
  name=os
  baseurl=file:///var/www/html/repositories/redhat/7/x86_64/os/
  gpgcheck=0
  enabled=1

.. raw:: html

  </div><br>
  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>8</b><br><br>

Create file */etc/yum.repos.d/BaseOS.repo* with the following content:

.. code-block:: text

  [BaseOS]
  name=BaseOS
  baseurl=file:///var/www/html/repositories/redhat/8/x86_64/os/BaseOS/
  gpgcheck=0
  enabled=1

Then create file */etc/yum.repos.d/AppStream.repo* with the following content:

.. code-block:: text

  [AppStream]
  name=AppStream
  baseurl=file:///var/www/html/repositories/redhat/8/x86_64/os/AppStream/
  gpgcheck=0
  enabled=1

.. raw:: html

  </div><br>

If you don't need the DVD ISO anymore, umount it:

.. code-block:: bash

  umount /mnt

Now ensure repository is available. Again, this step depends of the major
version used:

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>7</b><br><br>

.. code-block:: bash

  yum repolist

.. raw:: html

  </div><br>
  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>8</b><br><br>

.. code-block:: bash

  dnf repolist

.. raw:: html

  </div><br>

BlueBanquise and extra
^^^^^^^^^^^^^^^^^^^^^^

We now need to download locally main BlueBanquise repository.
We will also setup and empty extra repository, that will be used later to store
external rpms.

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>7</b><br><br>

Install reposync:

.. code-block:: bash

  yum install yum-utils -y

Then create temporary external repository in a temporary folder:

.. code-block:: bash

  mkdir /tmp/bbrepo/
  cat << EOF > /tmp/bbrepo/bluebanquise.repo
  [bluebanquise]
  name = bluebanquise
  baseurl = https://bluebanquise.com/repository/releases/latest/el7/x86_64/bluebanquise/
  gpgcheck = 0
  enabled = 1
  EOF

Create now final repository destination, and download bluebanquise repository
locally, asking only for latest packages, and restore SELinux tags:

.. code-block:: bash

  mkdir /var/www/html/repositories/redhat/7/x86_64/bluebanquise
  reposync --repoid=bluebanquise -c /tmp/bbrepo/bluebanquise.repo -p /var/www/html/repositories/redhat/7/x86_64/bluebanquise --newest-only --download-metadata
  restorecon -Rv /var/www/html/repositories/redhat/7/x86_64/bluebanquise

Now create final repository file */etc/yum.repos.d/BaseOS.repo* with the
following content:

.. code-block:: text

  [bluebanquise]
  name=bluebanquise
  baseurl=file:///var/www/html/repositories/redhat/7/x86_64/bluebanquise/
  gpgcheck=0
  enabled=1

Now create empty extra repository:

.. code-block:: bash

  mkdir -p /var/www/html/repositories/redhat/7/x86_64/extra/
  createrepo /var/www/html/repositories/redhat/7/x86_64/extra/
  restorecon -Rv /var/www/html/repositories/redhat/7/x86_64/extra

And register it by adding file */etc/yum.repos.d/extra.repo* with the following
content:

.. code-block:: text

  [extra]
  name=extra
  baseurl=file:///var/www/html/repositories/redhat/7/x86_64/extra/
  gpgcheck=0
  enabled=1

.. raw:: html

  </div><br>
  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>8</b><br><br>

Install reposync:

.. code-block:: bash

  dnf install yum-utils -y

Then create temporary external repository in a temporary folder:

.. code-block:: bash

  mkdir /tmp/bbrepo/
  cat << EOF > /tmp/bbrepo/bluebanquise.repo
  [bluebanquise]
  name = bluebanquise
  baseurl = https://bluebanquise.com/repository/releases/latest/el8/x86_64/bluebanquise/
  gpgcheck = 0
  enabled = 1
  EOF

Create now final repository destination, and download bluebanquise repository
locally, asking only for latest packages, and restore SELinux tags:

.. code-block:: bash

  mkdir /var/www/html/repositories/redhat/8/x86_64/bluebanquise
  reposync --repoid=bluebanquise -c /tmp/bbrepo/bluebanquise.repo -p /var/www/html/repositories/redhat/8/x86_64/bluebanquise --newest-only --download-metadata
  restorecon -Rv /var/www/html/repositories/redhat/8/x86_64/bluebanquise

Now create final repository file */etc/yum.repos.d/BaseOS.repo* with the
following content:

.. code-block:: text

  [bluebanquise]
  name=bluebanquise
  baseurl=file:///var/www/html/repositories/redhat/8/x86_64/bluebanquise/
  gpgcheck=0
  enabled=1

Now create empty extra repository:

.. code-block:: bash

  mkdir -p /var/www/html/repositories/redhat/8/x86_64/extra/
  createrepo /var/www/html/repositories/redhat/8/x86_64/extra/
  restorecon -Rv /var/www/html/repositories/redhat/8/x86_64/extra

And register it by adding file */etc/yum.repos.d/extra.repo* with the following
content:

.. code-block:: text

  [extra]
  name=extra
  baseurl=file:///var/www/html/repositories/redhat/8/x86_64/extra/
  gpgcheck=0
  enabled=1

.. raw:: html

  </div><br>

Download Ansible
----------------

Now that repositories are set, it is time to download Ansible.

On RHEL like systems, Ansible comes from the EPEL.

We need to install EPEL first, then download all needed rpms, and add them to
the *extra* repository we created before.

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>7</b><br><br>

Install EPEL repositories:

.. code-block:: bash

  yum install wget
  wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
  yum install epel-release-latest-7.noarch.rpm

Download Ansible package and needed dependencies, and store them into the extra
repository:

.. code-block:: bash

  yum install --downloadonly --downloaddir=/var/www/html/repositories/redhat/7/x86_64/extra/ ansible

Then update extra repository database and clean main host cache:

.. code-block:: bash

  createrepo --update /var/www/html/repositories/redhat/7/x86_64/extra/
  yum remove epel-release-latest-7
  yum clean all

.. raw:: html

  </div><br>
  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>8</b><br><br>

Install EPEL repositories:

.. code-block:: bash

  dnf install wget
  wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
  dnf install epel-release-latest-8.noarch.rpm

Download Ansible package and needed dependencies, and store them into the extra
repository:

.. code-block:: bash

  dnf install --downloadonly --downloaddir=/var/www/html/repositories/redhat/8/x86_64/extra/ ansible

Then update extra repository database and clean main host cache:

.. code-block:: bash

  createrepo --update /var/www/html/repositories/redhat/8/x86_64/extra/
  dnf remove epel-release-latest-8
  dnf clean all

.. raw:: html

  </div><br>

Install BlueBanquise and Ansible
--------------------------------

Install BlueBanquise and Ansible on the system:

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>7</b><br><br>

.. code-block:: bash

  yum install bluebanquise ansible

.. raw:: html

  </div><br>
  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>8</b><br><br>

.. code-block:: bash

  dnf install bluebanquise ansible

.. raw:: html

  </div><br>

Bring up main NIC
-----------------

Finally, last part is to bring up main network interface controller, the one
with *10.10.0.1* ip on the schema given at top of the page. We will assume this
NIC is *enp0s8* here. Please adapt to your hardware (list interfaces using
**ip a** command).

First, ensure NetworkManager is installed:

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>7</b><br><br>

.. code-block:: bash

  yum install NetworkManager

.. raw:: html

  </div><br>
  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>8</b><br><br>

.. code-block:: bash

  dnf install NetworkManager

.. raw:: html

  </div><br>

Then ensure it is started:

.. code-block:: bash

  systemctl start NetworkManager
  systemctl enable NetworkManager

And configure your interface to set a manual ipv4 address on it, then bring it
up:

.. code-block:: bash

  nmcli con mod enps08 ipv4.addresses 10.10.0.1/16
  nmcli con mod enps08 ipv4.method manual
  nmcli con up enps08

Using *ip a* command, you should now see your ip set on the interface.

Bootstrap Ubuntu like system
============================

Bootstrap SUSE like system
==========================

-------------

It is now time to configure BlueBanquise.
