========================
Install first management
========================

First step is to install first management node manually.

We will then learn how to use Ansible, and then only focus on the stack itself.

Install operating system
========================

Install Centos 7 or 8 using parameters you need.

The following parameters are recommended:

* >= 2 CPU/vCPU
* >= 2 Gb RAM
* >= 16Gb HDD

And the following parameters are the strict minimal if you wish to test the stack in VMs:

* >= 1 vCPU
* >= 512 Mb RAM
* >= 6Gb HDD

In this last configuration, DVD iso will be mounted from /dev/cdrom instead of being copied to save space.

It is recommended to only choose minimal install during packages selections (core or minimal server). Also, it is recommended to let system in English, and only set your keyboard and time zone to your country.

Prepare for Ansible
===================

Repositories
------------

Once system is installed and rebooted, login, and disable firewall. Current stack does not support firewall configuration on management nodes (but it is scheduled for later releases).

.. code-block:: bash

  systemctl stop firewalld
  systemctl disable firewalld

Then prepare repositories.

Operating system
^^^^^^^^^^^^^^^^

Download:

* Centos 7 Everything DVD iso from http://isoredirect.centos.org/centos/7/isos/x86_64/ . Iso name is CentOS-7-x86_64-Everything-1810.iso.
* Or Centos 8 DVD 1 iso from http://isoredirect.centos.org/centos/8/isos/x86_64/ . Iso name is CentOS-8-x86_64-1905-dvd1.iso.

**If on standard system:**

Mount iso and copy content to web server directory: (replace centos/7.6 by centos/8.0, redhat/8.0, redhat/7.7, etc depending of your system)

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7.6/x86_64/os/
  mount CentOS-7-x86_64-Everything-1810.iso /mnt
  cp -a /mnt/* /var/www/html/repositories/centos/7.6/x86_64/os/
  umount /mnt
  restorecon -Rv /var/www/html/repositories/centos/7.6/x86_64/os

**If in test VM:**

Simply mount iso from /dev/cdrom to save space:

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7.6/x86_64/os/
  mount /dev/cdrom /var/www/html/repositories/centos/7.6/x86_64/os/

Now, create first repository manually. Procedure is different between Centos 7 and 8.

**Centos/RHEL 7:**

Create file */etc/yum.repos.d/os.repo* with the following content:

.. code-block:: text

  [os]
  name=os
  baseurl=file:///var/www/html/repositories/centos/7.6/x86_64/os/
  gpgcheck=0
  enabled=1

**Centos/RHEL 8:**

Create file */etc/yum.repos.d/BaseOS.repo* with the following content:

.. code-block:: text

  [BaseOS]
  name=BaseOS
  baseurl=file:///var/www/html/repositories/redhat/8.0/x86_64/os/BaseOS
  gpgcheck=0
  enabled=1

Then create file */etc/yum.repos.d/AppStream.repo* with the following content:

.. code-block:: text

  [AppStream]
  name=AppStream
  baseurl=file:///var/www/html/repositories/redhat/8.0/x86_64/os/AppStream
  gpgcheck=0
  enabled=1

**Both:**

Now ensure repository is available:

.. code-block:: bash

  yum repolist

Repositories structure follows a specific pattern:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository
                        +             +       +               +
                        |             +---+   |               |
                        +-----------+     |   |      +--------+
                                    |     |   |      |
                                    v     v   v      v
       /var/www/html/repositories/centos/7.6/x86_64/os

Note: this patern parameters (distribution, version, architecture) must match the one provided in the equipment_profile file seen later.

BlueBanquise
^^^^^^^^^^^^

Download BlueBanquise rpms from official repository.

Go to https://bluebanquise.com, go to repositories/download, and get the content of the whole directory corresponding to your distribution and architecture.

Then copy this content into /var/www/html/repositories/centos/7.6/x86_64/bluebanquise/ locally.

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7.6/x86_64/bluebanquise/
  cp -a /root/bluebanquise_from_web/* /var/www/html/repositories/centos/7.6/x86_64/bluebanquise/
  restorecon -Rv /var/www/html/repositories/centos/7.6/x86_64/bluebanquise

And create file */etc/yum.repos.d/bluebanquise.repo* with the following content:

.. code-block:: text

  [bluebanquise]
  name=bluebanquise
  baseurl=file:///var/www/html/repositories/centos/7.6/x86_64/bluebanquise/
  gpgcheck=0
  enabled=1

Install Ansible
---------------

Time to install Ansible.

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

It must be **>= 2.8.2** .

It is now time, if you do not know how Ansible works, to learn basis of Ansible.

If you already know Ansible, or want to skip this recommended training, directly go to the Configure BlueBanquise section.

