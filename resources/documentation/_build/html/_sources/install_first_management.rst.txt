========================
Install first management
========================

First step to deploy **BlueBanquise** is to install first management node manually.

We will then learn how to use Ansible, and then only focus on the stack itself.

Install operating system
========================

Install Centos 7.6 using parameters you need.

The following parameters are recommended:

* >= 2 CPU/vCPU
* >= 2 Gb RAM
* >= 16Gb HDD

And the following parameters are the stricti minimal if you whish to test the stack in VMs:

* >= 1 vCPU
* >= 512 Mb RAM
* >= 6Gb HDD

In this last configuration, DVD iso will be mounted from /dev/cdrom instead of being copied to save space.

It is recommanded to only choose minimal install during packages selections. Also, it is recommanded to let system in English, and only set your keyboard and time zone to your contry.

Prepare for Ansible
===================

Repositories
------------

Once system is installed and rebooted, login, and disable firewall. Current stack do not support firewall configuration (but it is scheduled for later released).

.. code-block:: bash

  systemctl stop firewalld
  systemctl disable firewalld

Then prepare repositories.

Download Centos 7.6 Everything DVD iso from http://isoredirect.centos.org/centos/7/isos/x86_64/ . Iso name is CentOS-7-x86_64-Everything-1810.iso.

**If on standard system:**

Mount iso and copy content to web server directory:

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7.6/x86_64/os/
  mount CentOS-7-x86_64-Everything-1810.iso /mnt
  cp -a /mnt/* /var/www/html/repositories/centos/5.6/x86_64/os/
  umount /mnt
  restorecon -Rv /var/www/html/repositories/centos/7.6/x86_64/os

**If in test VM:**

Simply mount iso from /dev/cdrom to save space:

.. code-block:: bash

  mkdir -p /var/www/html/repositories/centos/7.6/x86_64/os/
  mount /dev/cdrom /var/www/html/repositories/centos/7.6/x86_64/os/

Now, create first repository manually. Create file */etc/yum.repos.d/os.repo* with the following content:

.. code-block:: text

  [os]
  name=os
  baseurl=file:///var/www/html/repositories/centos/7.6/x86_64/os/
  gpgcheck=0
  enabled=1

And ensure rpeository is available:

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

Install Ansible
---------------

Time to install Ansible.

.. code-block:: bash

  yum install ansible

And check Ansible is working:

.. code-block:: bash

  ansible --version

It is now time, if you do not know how Ansible works, to learn basis of Ansible.

If you already know Ansible, or want to skip this recommended training, directly go to the Deploy BlueBanquise section.
