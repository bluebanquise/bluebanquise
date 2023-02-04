=======================
[Core] - Deploy Cluster
=======================

At this point, **BlueBanquise** configuration is done. We are ready to deploy
the cluster.

We are going to proceed in the following order:

#. Deploy configuration on management1 node
#. Deploy fresh OS on the other nodes, from management1
#. Deploy configuration on the other nodes.

Management deployment
=====================

Get managements playbook
------------------------

If you used the bootstrap script, you already have the managements.yml playbook 
into *~/bluebanquise/playbooks/* folder. You can skip this step.

We are going to use the provided default playbook. This playbook will install
most of the **CORE** roles. Enough to deploy first stage of the cluster.

Copy example playbook managements to *~/bluebanquise/playbooks/*:

.. code-block:: bash

  mkdir ~/bluebanquise/playbooks/
  cp -a ~/bluebanquise/resources/examples/simple_cluster/playbooks/managements.yml ~/bluebanquise/playbooks/

Then, we will ask Ansible to read this playbook, and execute all roles listed
inside on management1 node (check hosts at top of the file).

To do so, we are going to use the **ansible-playbook** command.

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

Extra-vars allows to pass variables with maximum precedence at execution time,
for any purpose (debug, test, or simply need).

To do so, use:

* **--extra-vars** with " " and space separated variables: --extra-vars "myvar1=true myvar2=77 myvar3=hello"

Apply management1 configuration
-------------------------------

Lets apply now the whole configuration on management1. It can take some time
depending on your CPU and your hard drive.

We first ensure our NIC are up, so the repositories part is working.

.. code-block:: bash

  ansible-playbook ~/bluebanquise/playbooks/managements.yml --limit management1 --tags set_hostname,nic

Check interfaces are up (check using *ip a* command), and execute the
bluebanquise role and the repositories_server role:

.. code-block:: text

  ansible-playbook ~/bluebanquise/playbooks/managements.yml --limit management1 --tags repositories_server

This will install the requirements to ensure the web server of local repositories is running.

Then play the whole playbook:

.. code-block:: text

  ansible-playbook ~/bluebanquise/playbooks/managements.yml --limit management1

And wait...

If all went well, you can check that all services are up and running.

.. note::
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
will start a LAN boot automatically, even if your computer is not PXE able
natively.

In **BlueBanquise**, PXE process has been made so that any kind of hardware able
to boot PXE, USB or CDrom can start deployment.

PXE process overview
--------------------

You can get more information and a detailed schema in the pxe_stack role section
of this documentation. Simply explained, the PXE chain is the following (files
are in /var/www/html/preboot_execution_environment):

.. code-block:: text

  DHCP request
    |
  IP obtained, next-server obtained
    |
  Download (tftp) and load bluebanquise iPXE ROM
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
``http://${next-server}/preboot_execution_environment/convergence.ipxe``. Then this
file chain to node specific file in nodes (this file is generated using *bootset*
command). The node specific file contains the default entry for the iPXE menu,
then node chain to its equipment_profile file, to gather group values, and chain
again to menu file. The menu file display a simple menu, and wait 10s for user
before starting the default entry (which can be os deployment, or boot to disk,
or boot diskless).

The following slides explain the whole PXE process of the BlueBanquise stack:

.. raw:: html

  <!-- from https://www.w3schools.com/howto/howto_js_slideshow.asp -->
  <script>
  var slideIndex = 1;
  showSlides(slideIndex);
  // Next/previous controls
  function plusSlides(n) {
    showSlides(slideIndex += n);
  }
  // Thumbnail image controls
  function currentSlide(n) {
    showSlides(slideIndex = n);
  }
  function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    var dots = document.getElementsByClassName("dot");
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex-1].style.display = "block";
    dots[slideIndex-1].className += " active";
  }
  </script>
  <!-- Slideshow container -->
  <div class="slideshow-container">
     <!-- Full-width images with number and caption text -->
     <div class="mySlides">
       <div class="numbertext">1 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide1.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">2 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide2.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">3 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide3.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">4 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide4.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">5 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide5.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">6 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide6.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">7 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide7.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">8 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide8.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">9 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide9.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">10 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide10.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">11 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide11.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">12 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide12.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">13 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide13.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">14 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide14.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">15 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide15.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">16 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide16.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">17 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide17.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">18 / 18</div>
       <img src="_static/deploy_bluebanquise_pxe_slides/Slide18.PNG" style="width:100%">
     </div>
     <!-- Next and previous buttons -->
     <a class="prev" onclick="plusSlides(-1)">&#10094;</a>
     <a class="next" onclick="plusSlides(1)">&#10095;</a>
  </div>
  <br>
  <!-- The dots/circles -->
  <div style="text-align:center">
    <span class="dot" onclick="currentSlide(1)"></span>
    <span class="dot" onclick="currentSlide(2)"></span>
    <span class="dot" onclick="currentSlide(3)"></span>
    <span class="dot" onclick="currentSlide(4)"></span>
    <span class="dot" onclick="currentSlide(5)"></span>
    <span class="dot" onclick="currentSlide(6)"></span>
    <span class="dot" onclick="currentSlide(7)"></span>
    <span class="dot" onclick="currentSlide(8)"></span>
    <span class="dot" onclick="currentSlide(9)"></span>
    <span class="dot" onclick="currentSlide(10)"></span>
    <span class="dot" onclick="currentSlide(11)"></span>
    <span class="dot" onclick="currentSlide(12)"></span>
    <span class="dot" onclick="currentSlide(13)"></span>
    <span class="dot" onclick="currentSlide(14)"></span>
    <span class="dot" onclick="currentSlide(15)"></span>
    <span class="dot" onclick="currentSlide(16)"></span>
    <span class="dot" onclick="currentSlide(17)"></span>
    <span class="dot" onclick="currentSlide(18)"></span>
  </div>
  <!-- Addon from Benoit Leveugle: force slide1 after page load -->
  <script type="module">
    currentSlide(1)
  </script>

bootset
-------

Before booting remote nodes in PXE, we need to ask management1 to activate
remote nodes deployment. If not, remote nodes will not be able to grab their
dedicated configuration from management node at boot.

To manipulate nodes PXE boot, a command, **bootset**, is available.

We are going to deploy login1, storage1 and compute1, compute2, compute3 and compute4.

Let's use bootset to set them to deploy OS at next PXE boot (bootset must be launched using sudo if not root):

.. code-block:: bash

  sudo bootset -n login1,storage1,c[001-004] -b osdeploy

You can check the result using:

.. code-block:: bash

  sudo bootset -n login1,storage1,c[001-004] -s

Which should return:

.. code-block:: text

  [INFO] Loading /etc/bootset/nodes_parameters.yml
  [INFO] Loading /etc/bootset/pxe_parameters.yml
  Next boot deployment: c[001-004],login1,storage1

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

  ansible-playbook ~/bluebanquise/playbooks/managements.yml --tags pxe_stack

OS deployment
-------------

Power on now the remote nodes, have them boot over LAN, and watch the automatic
installation procedure. It should take around 5-20 minutes depending on your
hardware.

Once done, proceed to next part.

Apply other nodes configuration
===============================

Now that all the nodes have an operating system installed and running, applying
configuration on these nodes is simple.

Ensure first you can ssh passwordless on each of the freshly deployed nodes.

.. note::
On some Linux distributions, if DHCP leases are short, you may loose
ip shortly after system is booted. If that happen, reboot system to get an ip
again. This issue is solved once the nic_nmcli role has been applied on hosts,
as it sets ip statically.

If yes, copy example playbooks:

.. code-block:: bash

  cp -a ~/bluebanquise/resources/examples/simple_cluster/playbooks/computes.yml ~/bluebanquise/playbooks/
  cp -a ~/bluebanquise/resources/examples/simple_cluster/playbooks/logins.yml ~/bluebanquise/playbooks/
  cp -a ~/bluebanquise/resources/examples/simple_cluster/playbooks/storages.yml ~/bluebanquise/playbooks/

And execute them, using --limit parameter to specify targets:

.. code-block:: bash

  ansible-playbook ~/bluebanquise/playbooks/logins.yml
  ansible-playbook ~/bluebanquise/playbooks/storages.yml
  ansible-playbook ~/bluebanquise/playbooks/computes.yml --limit compute1,compute2,compute3,compute4

You can see that Ansible will work on computes nodes in parallel, using more CPU
on the management1 node (by spawning multiple forks).

-------------

Your cluster should now be fully deployed the generic way: operating systems are
deployed on each hosts, and basic services (DNS, repositories, time
synchronization, etc.) are up and running.

It is time to use some `COMMUNITY <https://github.com/bluebanquise/community>`_
roles to add specific features to the cluster and/or specialize it.
(Please refer to each community roles dedicated documentation to get
instructions on how to use them), or continue this documentation to 
go into advanced configurations.

You will also find a "FAQ" section that could help with few recurrent
situation you may face during the life of your cluster.

Thank your for following this training. We really hope you will enjoy the stack.
Please report us any bad or good feedback.
