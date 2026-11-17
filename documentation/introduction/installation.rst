============
Installation
============

Installing BlueBanquise only takes a few minutes. Let's do it on the host that will manage the
cluster: the management host.

Requirements
============

The management host must run one of the supported distributions: RHEL 9 or 10 (or a compatible
distribution, like Rocky Linux or AlmaLinux), Ubuntu 24.04 or 26.04, Debian 13, or OpenSuse Leap 16.
It needs the ``curl`` and ``sudo`` commands, and internet access during the installation (to
download Python packages, Ansible, and the BlueBanquise collection).

Install BlueBanquise
====================

Bootstrap BlueBanquise using the online installer:

.. code-block:: bash

  curl -o online_bootstrap.sh https://raw.githubusercontent.com/bluebanquise/bluebanquise/master/bootstrap/online_bootstrap.sh
  chmod +x online_bootstrap.sh
  sudo ./online_bootstrap.sh

The installer:

* installs a few system packages (Python, git, SSH client),
* creates the ``bluebanquise`` user, with its home in ``/var/lib/bluebanquise``, and makes it a sudoer,
* clones the BlueBanquise repository in ``/var/lib/bluebanquise/bluebanquise`` (it provides the
  ``ansible.cfg`` configuration file, and reference files),
* installs Ansible and the ``bluebanquise.infrastructure`` collection in a Python virtual
  environment, ``/var/lib/bluebanquise/ansible_venv``, loaded automatically at login,
* generates an SSH key pair for the ``bluebanquise`` user.

It is verbose on purpose: if something goes wrong, the output tells you where.

Load the working environment
============================

Let's log in as the ``bluebanquise`` user:

.. code-block:: text

  sudo su - bluebanquise

This user is the "cluster admin user". Deployed hosts automatically get a ``bluebanquise`` user too,
with SSH keys set, so you can reach them, and Ansible can configure them.

.. warning::

  This user is as powerful as root on all hosts of the cluster: keep it for administration tasks,
  not for day to day work.

Check that Ansible is ready:

.. code-block:: text

  $ ansible-playbook --version
  ansible-playbook [core 2.19.2]
    config file = /var/lib/bluebanquise/bluebanquise/ansible.cfg
    ...

BlueBanquise is now installed on the management host. The cluster itself is not deployed yet: the
next step is to describe it in an inventory (see :doc:`../configuration/inventories`). If you are
new to Ansible, a quick look at :doc:`vocabulary` first will help.

Update the collection
=====================

To get the latest version of the roles later on, as the ``bluebanquise`` user:

.. code-block:: bash

  ansible-galaxy collection install git+https://github.com/bluebanquise/bluebanquise.git#/collections/infrastructure,master --upgrade

Then read the ``CHANGELOG`` file of the repository: it lists, for each version, what changed, and
what you may need to update in your inventory.
