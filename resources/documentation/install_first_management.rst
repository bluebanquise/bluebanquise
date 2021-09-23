==============================
[Core] - Bootstrap base system
==============================




This documentation will cover the configuration of a very simple cluster:

.. image:: images/example_cluster_small.svg

The documentation focus on main inventory parameters of the stack. However, more
features are available in the stack. Read roles Readme to learn more about
each role capabilities.






The first step is to bootstrap the first management server of the cluster.

This procedure mainly depend on the Linux distribution chosen. In the following
section, bordered parts are dedicated to specific distributions or specific
major version, while non bordered part are generic.

First step is to install first management node manually.

Bootstrap RHEL like system
==========================

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

.. warning::
  In the following documentation, we will always use *redhat/8/x86_64/* or
  *redhat/7/x86_64/* when setting path. Adapt this to your target distribution
  and architecture.
  Distribution keywords supported are: **redhat**, **rhel**, **centos**,
  **rockylinux**, **oraclelinux**, **cloudLinux**, **almalinux**.
  And supported architecture are **x86_64** or **arm64**.

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 2 Gb RAM
* >= 40 Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 2 Gb RAM (PXE part need a lot of RAM)
* >= 20 Gb HDD

OS installation
---------------

Install the Linux operating system manually (from USB key, CDrom, netboot, etc.).

It is recommended to only choose minimal install during packages selection
(core or minimal server).
Also, it is recommended to let system in English, and only set your keyboard and
time zone to your country.

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
       /var/www/html/repositories/redhat/8/x86_64/os/

.. note::
  The */var/www/html* path given here is an example, as it may vary depending of
  distribution used. What maters is the structure following this path.

.. warning::
  This pattern parameters (distribution, version, architecture) must match
  the one provided in the **equipment_profile** file seen later.

Isos to be used
^^^^^^^^^^^^^^^

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  <b>RHEL</b> <img src="_static/logo_rhel.png">
  <br><br>

Obtain the main binary DVD from Red Hat, using your subscription. Naming is
similar to:

* rhel-8.3-x86_64-dvd.iso
* rhel-server-7.9-x86_64-dvd.iso
* ...

.. raw:: html

  </div><br>

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  <b>CentOS</b> <img src="_static/logo_centos.png">, <b>RockyLinux</b> <img src="_static/logo_rocky.png">, <b>OracleLinux</b> <img src="_static/logo_oraclelinux.png">, <b>CloudLinux</b> <img src="_static/logo_cloudlinux.png">, <b>AlmaLinux</b> <img src="_static/logo_almalinux.png">
  <br><br>

Obtain the main binary DVD from distribution website. You need to grab the
*Everything* DVD, also called *dvd1*:

* CentOS-8.3.2011-x86_64-dvd1.iso
* CentOS-7-x86_64-Everything-2009.iso
* ...

.. raw:: html

  </div><br>

Copy iso on system
^^^^^^^^^^^^^^^^^^

Mount iso and copy content to web server directory: (replace redhat/8 by
redhat/7, centos/8, centos/7, rockylinux/8, etc depending of your system).

.. code-block:: bash

  mkdir -p /var/www/html/repositories/redhat/8/x86_64/os/
  mount rhel-8.3-x86_64-dvd.iso /mnt
  cp -a /mnt/* /var/www/html/repositories/redhat/8/x86_64/os/
  restorecon -Rv /var/www/html/repositories/redhat/8/x86_64/os

Set os repository
^^^^^^^^^^^^^^^^^

Now, create first repository manually. Part of the procedure is different
between major versions of the same distribution.

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

If you don't need the DVD iso anymore, umount it:

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

Install reposync >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Then create repository folder:

.. code-block:: bash

  mkdir -p /var/www/html/repositories/redhat/8/x86_64/bluebanquise/

Install reposync >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Then create ensure SELinux contexts are conform on these files:

.. code-block:: bash

  restorecon -Rv /var/www/html/repositories/redhat/8/x86_64/bluebanquise

And create file */etc/yum.repos.d/bluebanquise.repo* with the following content:

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

Finally, install BlueBanquise and Ansible on the system:

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

-------------

It is now time to configure BlueBanquise.
