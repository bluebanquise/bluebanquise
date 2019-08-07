===================
Deploy BlueBanquise
===================

At this point, you should have an operating system with Ansible installed on it, and basic OS repositories.

Get BlueBanquise
================

Install needed basic packages:

.. code-block:: bash

  yum install wget http createrepo git

Once done, grab files from the web:

TOBEDONE

Now, backup and clean your previous Ansible configuration:

.. code-block:: bash

  tar cvzf /root/my_old_ansible.tar.gz /etc/ansible
  rm -Rf /etc/ansible/*

And download **BlueBanquise** into Ansible directory:

.. code-block:: bash

  cd /etc/ansible
  git clone https://github.com/oxedions/bluebanquise.git .

It is time to configure the inventory to match cluster needs.

Configure inventory
===================

This documentation will cover the configuration of a very simple cluster:

.. image:: images/example_cluster_small.svg

Important before we start
-------------------------

Ansible will read **ALL** files in the inventory. **NEVER do a backup of a file here!**

Backup in another location, outside of /etc/ansible/inventory.



