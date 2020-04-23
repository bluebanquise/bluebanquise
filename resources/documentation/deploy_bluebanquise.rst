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

Copy example playbook management1 to /etc/bluebanquise/playbooks/:

.. code-block:: bash

  mkdir /etc/bluebanquise/playbooks/
  cp -a /etc/bluebanquise/resources/examples/simple_cluster/playbooks/management1.yml /etc/bluebanquise/playbooks/

Then, we will ask Ansible to read this playbook, and execute all roles listed inside on management1 node (check hosts target at top of the file).

To do so, we are going to use the ansible-playbook command.

Ansible-playbook
----------------

*ansible-playbook* is the command used to ask Ansible to execute a playbook.

We are going to use 2 parameters frequently:

Tags / Skip tags
^^^^^^^^^^^^^^^^

As you can notice, some tags are set inside the playbook, or even in some roles for specific tasks. The idea of tags is simple: you can tag a role/a task, and then when using ansible-playbook, only play related tags role/task. Or do the opposit: play all, and skip a role/task.

To so, use with Ansible playbook:

* **--tags** with tags listed with comma separator: mytag1,mytag2,mytag3
* **--skip-tags** with same pattern

More can be found `here <https://docs.ansible.com/ansible/latest/user_guide/playbooks_tags.html>`_ on tags.

Extra vars
^^^^^^^^^^

Extra vars allows to pass variables with maximum precedence at execution time, for any purpose (debug, test, or simply need).

To do so, use:

* **--extra-vars** with " " and space separated variables: --extra-vars "myvar1=true myvar2=77 myvar3=hello"

Apply management1 configuration
-------------------------------

Lets apply now the whole configuration on management1. It can takes some time depending of your CPU and your hard drive.

We first ensure our NIC are up, so the repositories part is working.

.. code-block:: bash

  ansible-playbook /etc/bluebanquise/playbooks/management1.yml --tags set_hostname,nic

Then start your main interface manually. Here enp0s3:

.. code-block:: bash

  ifup enp0s3

Once interface is up (check using *ip a* command), replay the whole playbook:

.. code-block:: bash

  ansible-playbook /etc/bluebanquise/playbooks/management1.yml

And wait...

If all goes well, you can check that all services are up and running:

.. code-block:: bash

  systemctl status httpd
  systemctl status atftpd
  systemctl status dhcpd
  systemctl status named

You can replay the same ansible-playbook command over and over, Ansible will just update/correct what is needed, and do nothing for all that is at an expected state.

Now that management1 is up and running, it is time to deploy the other nodes.

PXE
===

Next step is to deploy the other nodes using PXE process.

NOTE: it is assumed here you know how to have your other nodes / VM / servers / workstation to boot on LAN.
If your device cannot boot on LAN, use iso or usb image provided on management1 in /var/www/html/preboot_execution_environment/bin/[x86_64|arm64]. These images will start a LAN boot automatically.

In **BlueBanquise**, PXE process has been made so that any kind of hardware able to boot PXE, USB or CDrom can start deployment.

You can get more information and a detailed schema in the pxe_stack role section of this documentation. Simply put, the PXE chain is the following (files are in /var/www/html/preboot_execution_environment):

.. code-block:: text

  DHCP request
    |
  IP obtained, next-server obtained
    |
  Load iPXE bluebanquise ROM
    |
  DHCP request again with new ROM
    |
  iPXE chain to convergence.ipxe (using http)
    |
  iPXE chain to nodes/myhostname.ipxe (get dedicated values)
    |
  iPXE chain to equipment_profiles/my_equipment_profile.ipxe (get group dedicated values)
    |
  iPXE chain to menu.ipxe
    |
  iPXE chain to task specified in myhostname.ipxe (deploy os, boot on disk, etc)

Whatever the boot source, and whatever Legacy Bios or uEFI, all converge to http://${next-server}/preboot_execution_environment/convergence.ipxe. Then this file chain to node specific file in nodes (this file is generated using bootset command). The node specific file contains the default entry for the iPXE menu, then node chain to its equipment_profile file, to gather group values, and chain again to menu file. The menu file display a simple menu, and wait 10s for user before starting the default entry (which can be os deployment, or boot to disk, or boot diskless).

bootset
-------

Before booting remote nodes in PXE, we need to ask management1 to activate remote nodes deployment. If not, remote nodes will boot on disk, even when booting over LAN.

To manipulate nodes PXE boot, a command, *bootset*, is available.

We are going to deploy login1 and c001, c002, c003 and c004.

Let's use bootset to ask them to deploy OS at next PXE boot:

.. code-block:: bash

  bootset -n login1,c[001-004] -b osdeploy

Note that this osdeploy state will be automatically updated once OS is deployed on remote nodes, and set to disk.

You can also force nodes that boot on PXE to boot on disk using *-b disk* instead of *-b osdeploy*.

Note also that if you update configuration on management1, it is recommanded to force the update of files when using bootset.

Please refer to the pxe_stack role dedicated section in this documentation for more information on the bootset usage.

SSH public key
--------------

In order to log into the remote nodes without giving the password, check that
the ssh public key defined in authentication.yml in your inventory match your
management1 public key. If not, update it. Remember to run the pxe_stack role
after updating the configuration.

.. code-block:: bash

  ansible-playbook /etc/bluebanquise/playbooks/management1.yml --tags pxe_stack

OS deployment
-------------

Power on now the remote nodes, have them boot over LAN, and follow the installation procedure. It should take around 15-20 minutes depending of your hardware.

Once done, proceed to next part.

Apply other nodes configuration
===============================

Applying configuration on other nodes is simple.

Ensure first you can ssh passwordless on each of the freshly deployed nodes. If
yes, copy example playbooks:

.. code-block:: bash

  cp -a /etc/bluebanquise/resources/examples/simple_cluster/playbooks/computes.yml /etc/bluebanquise/playbooks/
  cp -a /etc/bluebanquise/resources/examples/simple_cluster/playbooks/login1.yml /etc/bluebanquise/playbooks/

And execute them, using extra var target to target them:

.. code-block:: bash

  ansible-playbook /etc/bluebanquise/login1.yml
  ansible-playbook /etc/bluebanquise/computes.yml --extra-vars "target=c001,c002,c003,c004"

You can see that Ansible will work on computes nodes in parallel, using more CPU on the management1 node.

Your cluster should now be fully deployed. It is time to use some ADDONs to add specific features to the cluster (Please refer to each addon roles dedicated documentation to get instructions on how to use them), or continue this documentation to enable and deploy multi icebergs configuration if cluster needs it.

Thank your for following this training. We really hope you will enjoy our stack. Please report us any bad or good feedback.
