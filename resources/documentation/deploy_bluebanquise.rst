============================
[Core] - Deploy BlueBanquise
============================

At this point, **BlueBanquise** configuration is done. We are ready to deploy
the cluster.

First step is to deploy configuration on management1 node, and then deploy OS on
the other systems. Last step will be to deploy configuration on the other
systems.

Management deployment
=====================

Get managements playbook
------------------------

We are going to use the provided default playbook. This playbook will install
most of the **CORE** roles. Enough to deploy first stage of the cluster.

Copy example playbook managements to /etc/bluebanquise/playbooks/:

.. code-block:: bash

  mkdir /etc/bluebanquise/playbooks/
  cp -a /etc/bluebanquise/resources/examples/simple_cluster/playbooks/managements.yml /etc/bluebanquise/playbooks/

Then, we will ask Ansible to read this playbook, and execute all roles listed
inside on management1 node (check hosts at top of the file).

To do so, we are going to use the ansible-playbook command.

Ansible-playbook
----------------

*ansible-playbook* is the command used to ask Ansible to execute a playbook.

We are going to use 2 parameters frequently:

Tags / Skip tags
^^^^^^^^^^^^^^^^

As you can notice, some tags are set inside the playbook, or even in some roles
for specific tasks. The idea of tags is simple: you can tag a role/task, and
then when using ansible-playbook, only play related tags role/task. Or do the
opposite: play all, and skip a role/task.

To so, use with Ansible playbook:

* **--tags** with tags listed with comma separator: mytag1,mytag2,mytag3
* **--skip-tags** with same pattern

Additional documentation about tags usage in playbooks is available
`here <https://docs.ansible.com/ansible/latest/user_guide/playbooks_tags.html>`_.

Extra vars
^^^^^^^^^^

Extra vars allow to pass variables with maximum precedence at execution time,
for any purpose (debug, test, or simply need).

To do so, use:

* **--extra-vars** with " " and space separated variables: --extra-vars "myvar1=true myvar2=77 myvar3=hello"

Apply management1 configuration
-------------------------------

Lets apply now the whole configuration on management1. It can take some time
depending on your CPU and your hard drive.

We first ensure our NIC are up, so the repositories part is working.

.. code-block:: bash

  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --limit management1 --tags set_hostname,nic_nmcli

Then start your main interface manually. Here enp0s3:

.. raw:: html

  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>7</b><br><br>

.. code-block:: text

  ifup enp0s3

.. raw:: html

  </div><br>
  <div style="border: 1px solid; margin: 0px 0px 0px 20px; padding: 6px;">
  Major version: <b>8</b><br><br>

.. code-block:: text

  nmcli con up enp0s3

.. raw:: html

  </div><br>

Once interface is up (check using *ip a* command), execute the bluebanquise role
and the repositories_server role:

.. code-block:: text

  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --limit management1 --tags bluebanquise,repositories_server

This will install the requirements to run BlueBanquise (mostly python filters
for Ansible), and ensure the web server of local repositories is running.

Then play the whole playbook:

.. code-block:: text

  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --limit management1

And wait...

If all goes well, you can check that all services are up and running:

.. code-block:: bash

  systemctl status httpd
  systemctl status atftpd
  systemctl status dhcpd
  systemctl status named

You can replay the same ansible-playbook command over and over, Ansible will
just update/correct what is needed, and do nothing for all that is at an
expected state.

Now that management1 is up and running, it is time to deploy the other nodes.

Deploy OS on other nodes: PXE
=============================

Next step is to deploy the other nodes using PXE process.

NOTE: it is assumed here you know how to have your other nodes / VM / servers /
workstation to boot on LAN.

If your device cannot boot on LAN, use iso or usb image provided on management1
in /var/www/html/preboot_execution_environment/bin/[x86_64|arm64]. These images
will start a LAN boot automatically.

In **BlueBanquise**, PXE process has been made so that any kind of hardware able
to boot PXE, USB or CDrom can start deployment.

You can get more information and a detailed schema in the pxe_stack role section
of this documentation. Simply explained, the PXE chain is the following (files
are in /var/www/html/preboot_execution_environment):

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

Whatever the boot source, and whatever Legacy BIOS or UEFI, all converge to
http://${next-server}/preboot_execution_environment/convergence.ipxe. Then this
file chain to node specific file in nodes (this file is generated using *bootset*
command). The node specific file contains the default entry for the iPXE menu,
then node chain to its equipment_profile file, to gather group values, and chain
again to menu file. The menu file display a simple menu, and wait 10s for user
before starting the default entry (which can be os deployment, or boot to disk,
or boot diskless).

bootset
-------

Before booting remote nodes in PXE, we need to ask management1 to activate
remote nodes deployment. If not, remote nodes will not be able to grab their
dedicated configuration from management node at boot.

To manipulate nodes PXE boot, a command, **bootset**, is available.

We are going to deploy login1 and c001, c002, c003 and c004.

Let's use bootset to set them to deploy OS at next PXE boot:

.. code-block:: bash

  bootset -n login1,c[001-004] -b osdeploy

You can check the result using:

.. code-block:: bash

  bootset -n login1,c[001-004] -s

Which should return:

.. code-block:: text

  [INFO] Loading /etc/bootset/nodes_parameters.yml
  [INFO] Loading /etc/bootset/pxe_parameters.yml
  Next boot deployment: c[001-004],login1

Note that this osdeploy state will be automatically updated once OS is deployed
on remote nodes, and set to disk.

You can also force nodes that boot on PXE to boot on disk using *-b disk*
instead of *-b osdeploy*.

Please refer to the pxe_stack role dedicated section in this documentation for
more information on the bootset usage.

SSH public key
--------------

In order to log into the remote nodes without giving the password, check that
the ssh public key defined in authentication.yml in your inventory match your
management1 public key (the one generated in /root/.ssh/). If not, update the
key in authentication.yml and remember to re-run the pxe_stack role (to update
PXE related files that contains the ssh public key of the management node to be
set on nodes during deployment).

.. code-block:: bash

  ansible-playbook /etc/bluebanquise/playbooks/managements.yml --tags pxe_stack

OS deployment
-------------

Power on now the remote nodes, have them boot over LAN, and follow the
installation procedure. It should take around 5-20 minutes depending on your
hardware.

Once done, proceed to next part.

Apply other nodes configuration
===============================

Now that all the nodes have an operating system installed and running, applying
configuration on these nodes is simple.

Ensure first you can ssh passwordless on each of the freshly deployed nodes. If
yes, copy example playbooks:

.. code-block:: bash

  cp -a /etc/bluebanquise/resources/examples/simple_cluster/playbooks/computes.yml /etc/bluebanquise/playbooks/
  cp -a /etc/bluebanquise/resources/examples/simple_cluster/playbooks/logins.yml /etc/bluebanquise/playbooks/

And execute them, using --limit parameter to specify targets:

.. code-block:: bash

  ansible-playbook /etc/bluebanquise/playbooks/logins.yml
  ansible-playbook /etc/bluebanquise/playbooks/computes.yml --limit c001,c002,c003,c004

You can see that Ansible will work on computes nodes in parallel, using more CPU
on the management1 node (by spawning multiple forks).

-------------

Your cluster should now be fully deployed the generic way: operating systems are
deployed on each hosts, and basic services (DNS, repositories, time
synchronization, etc.) are up and running.

It is time to use some community roles to add specific features to the cluster
and/or specialize it.
(Please refer to each community roles dedicated documentation to get
instructions on how to use them), or continue this documentation to:

* BlueBanquise generic cluster
    * Deploy a multi icebergs cluster
    * Deploy diskless nodes
* BlueBanquise specialized cluster
    * Deploy Prometheus (Monitoring your cluster)
    * Deploy Slurm (Specialize your cluster for High Performance Computing)
    * Deploy Nomad and Consul (Deploy containers orchestration on the cluster)

You will also find a "stories" section that describes step by step few recurrent
situation you may face during the life of your cluster.

Thank your for following this training. We really hope you will enjoy our stack.
Please report us any bad or good feedback.
