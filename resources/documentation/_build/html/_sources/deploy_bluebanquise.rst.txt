===================
Deploy BlueBanquise
===================

At this point, **BlueBanquise** configuration is done. We are ready to deploy the cluster.

First step is to deploy configuration on management1 node, and then deploy OS on the others system. Last step will be to deploy configuration on the other systems.

Management configuration
========================

Get management1 playbook
------------------------

We are going to use the provided default playbook. This playbook will install most of the CORE roles. Enough to deploy first stage of the cluster.

Copy example playbook management1 to /etc/ansible/playbooks/:

.. code-block:: bash

  mkdir /etc/ansible/playbooks/
  cp -a /etc/ansible/resources/examples/playbooks/management1.yml /etc/ansible/playbooks/

Then, we will ask Ansible to read this playbook, and execute all roles listed inside on management1 node (check hosts target at top of the file).

To do so, we are going to use the ansible-playbook command.

Ansible-playbook
----------------

Ansible playbook is the command used to ask Ansible to execute a playbook.

We are going to use 2 parameters frequently:

Tags / Skip tags
^^^^^^^^^^^^^^^^

As you can notice, some tags are set inside the playbook, or even in some roles for specific tasks. The idea of tags is simple: you can tag a role/a task, and then when using ansible-playbook, only play related tags role/task. Or do the opposit: play all, and skip a role/task.

To so, use with Ansible playbook:

* **--tags** with tags listed with comma separator: mytag1,mytag2,mytag3
* **--skip-tags** with same pattern

More can be found here on tags: https://docs.ansible.com/ansible/latest/user_guide/playbooks_tags.html

Extra vars
^^^^^^^^^^

Extra vars allows to pass variables with maximum precedence at execution time, for any purpose (debug, test, or simply need).

To do so, use:

* **--extra-vars** with " " and space separated variables: --extra-vars "myvar1=true myvar2=77 myvar3=hello"

Apply management1 configuration
-------------------------------

Lets apply now the whole configuration on management1. It can takes some time depending of your CPU and your hard drive.

We first ensure our NI are up, so the repositories part is working.

.. code-block:: bash

  ansible-playbook /etc/ansible/playbooks/management1.yml --tags CORE_set_hostname,CORE_nic

Then start your main interface manually. Here enp0s3:

.. code-block:: bash

  ifup enp0s3

Once interface is up (check using ip a command), replay the whole playbook:

.. code-block:: bash

  ansible-playbook /etc/ansible/playbooks/management1.yml

And wait...

If all goes well, you can check that all services are up and running:

.. code-block:: bash

  systemctl status httpd
  systemctl status dhcpd
  systemctl status named

You can replay the same ansible-playbook command over and over, Ansible will just update/correct what is needed, and do nothing for all that is at an expected state.

Now that management1 is up and running, it is time to deploy the other nodes.

PXE
===

Next step is to deploy the other nodes using PXE process.

NOTE: it is assumed here you know how to have your other nodes / VM / servers / workstation to boot on LAN.
If your device cannot boot on LAN, use iso or usb image provided on management1 in /var/lib/tftpboot. These images will start a LAN boot automatically.

In **BlueBanquise**, PXE process has been made so that any kind of hardware able to boot PXE, USB or CDrom can start deployment.

The following schema provides a macroscopic map of the process:

.. image:: images/iPXE_process_v3.svg

Whatever the boot source, and whatever Legacy Bios or uEFI, all converge to http://nextserver/convergence.ipxe. Then this file chain to node specific file in nodes (this file is generated using bootset command). The node specific file contains the default entry for the iPXE menu, and chain to menu.ipxe file. The menu file display a simple menu, and wait 10s for user before starting the default entry (which can be os deployment, or boot to disk).

bootset
-------

Before booting remote nodes in PXE, we need to ask management1 to activate remote nodes deployment. If not, remote nodes will boot on disk, even when booting over LAN.

To manipulate nodes PXE boot, a command, bootset is available.

We are going to deploy login1 and c001, c002, c003 and c004.

Let's use bootset to ask them to deploy OS at next PXE boot:

.. code-block:: bash

  bootset -n login1,c[001-004] -b osdeploy

Note that this osdeploy state will be autoamtically updated once OS is deployed on remote nodes, and set to disk.

You can also force nodes that boot on PXE to boot on disk using *-b disk* instead of *-b osdeploy*.

Note also that if you update configuration on management1, it is recommanded to force the update of files when using bootset. To do so, add *-u true*.

OS deployment
-------------

Power on now the remote nodes, have them boot over LAN, and follow the installation procedure. It should take around 15-20 minutes depeding of your hardware.

Once done, proceed to next part.

Apply other nodes configuration
===============================

Applying configuration on other nodes is simple.

Ensure first you can ssh passwordless on each of the freshly deployed nodes.

If yes, copy example playbooks:

.. code-block:: bash

  cp -a /etc/ansible/resources/examples/playbooks/computes.yml /etc/ansible/playbooks/
  cp -a /etc/ansible/resources/examples/playbooks/logins.yml /etc/ansible/playbooks/

And execute them, using extra var target to target them:

.. code-block:: bash

  ansible-playbook /etc/ansible/logins.yml --extra-vars "target=login1"
  ansible-playbook /etc/ansible/computes.yml --extra-vars "target=c001,c002,c003,c004"

You can see that Ansible will work on computes nodes in parallel, using more CPU on the management1 node.

Your cluster should now be fully deployed. It is time to use some ADDONs to add specific features to the cluster.
