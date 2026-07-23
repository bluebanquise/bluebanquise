============
Provision OS
============



Pull os images
==============

If you plan to use PXE on your cluster to deploy OS on servers through the network, you will need to obtain desired OS isos.

A small tool is available to ease this task.



==============
Deploy Cluster
==============

At this point, **BlueBanquise** configuration is done. We are ready to deploy
the cluster.

We are going to proceed in the following order:

#. Deploy configuration on management1 host
#. Deploy fresh OS on the other hosts, from management1
#. Deploy configuration on the other hosts.

It is assumed that you already have deployed a fresh operating system on the management host management1.

Install vital dependencies
==========================

Use the provided bootstrap tool to install needed dependencies for your current system (recent python) and setup bluebanquise user.
Note that you need the ``sudo`` command to be installed on the system.

Using root user (or a sudo user), launch the bootstrap script.

The script will install needed packages (mostly python), create the ``bluebanquise`` user with home at ``/var/lib/bluebanquise``,
set this user sudoer, install Ansible in a virtual environment in this user's home, and generate an ssh keys pair for this user.

Script is verbose to help you debug in case of issues.

.. code-block:: bash

  curl -o online_bootstrap.sh https://raw.githubusercontent.com/bluebanquise/bluebanquise/master/bootstrap/online_bootstrap.sh
  chmod +x online_bootstrap.sh 
  ./online_bootstrap.sh

Now, login as bluebanquise user. Remaining documentation assumes you are using the bluebanquise user.

.. code-block:: bash

  sudo su - bluebanquise

Management deployment
=====================

Import inventory
----------------

Import the inventory previsouly created in this documentation into ``/var/lib/bluebanquise/inventory``.

Set BlueBanquise repository
---------------------------

In order to be able to download BlueBanquise packages (mostly for pex_stack role), you need to add BlueBanquise repository into the inventory.
Repository is differend depending of OS.
Create file ``/var/lib/bluebanquise/inventory/group_vars/all/repositories.yml`` with the following content:

* RHEL like system:

.. raw:: html

  <div style="padding: 6px;">
  <b>RHEL</b> <img src="_static/logo_rhel.png">, <b>CentOS</b> <img src="_static/logo_centos.png">, <b>RockyLinux</b> <img src="_static/logo_rocky.png">, <b>OracleLinux</b> <img src="_static/logo_oraclelinux.png"><br> <b>CloudLinux</b> <img src="_static/logo_cloudlinux.png">, <b>AlmaLinux</b> <img src="_static/logo_almalinux.png">
  </div><br><br>

* EL9:

.. code-block:: yaml

  bb_repositories:
    - name: bluebanquise
      baseurl: http://bluebanquise.com/repository/releases/latest/el9/x86_64/bluebanquise/
      enabled: 1
      state: present

* EL10:

.. code-block:: yaml

  bb_repositories:
    - name: bluebanquise
      baseurl: http://bluebanquise.com/repository/releases/latest/el10/x86_64/bluebanquise/
      enabled: 1
      state: present

* Ubuntu or Debian like systems:

.. raw:: html

  <div style="padding: 6px;">
  <b>Ubuntu</b> <img src="_static/logo_ubuntu.png">, <b>Debian</b> <img src="_static/logo_debian.png">
  </div><br><br>

* Ubuntu 24.04:

.. code-block:: yaml

  bb_repositories:
    - repo: deb [trusted=yes] http://bluebanquise.com/repository/releases/latest/u24/x86_64/bluebanquise/ noble main
      state: present

* Ubuntu 26.04:

.. code-block:: yaml

  bb_repositories:
    - repo: deb [trusted=yes] http://bluebanquise.com/repository/releases/latest/u26/x86_64/bluebanquise/ resolute main
      state: present

* Debian 13:

.. code-block:: yaml

  bb_repositories:
    - repo: deb [trusted=yes] http://bluebanquise.com/repository/releases/latest/deb13/x86_64/bluebanquise/ trixie main
      state: present

* Suse like system:

.. raw:: html

  <div style="padding: 6px;">
  <b>Suse</b> <img src="_static/logo_suse.png">
  </div><br><br>

.. code-block:: yaml

  bb_repositories:
    - name: bluebanquise
      disable_gpg_check: true
      baseurl: https://bluebanquise.com/repository/releases/latest/lp16/x86_64/bluebanquise/

Create management playbook
--------------------------

Create ``/var/lib/bluebanquise/playbooks`` folder and add a file called ``management1.yml`` playbook into this folder,
with the following content:

.. code-block:: yaml

  ---
  - name: management playbook
    hosts: "management1"
    roles:

      # Infrastructure

      - role: bluebanquise.infrastructure.hosts_file
        tags: hosts_file
      - role: bluebanquise.infrastructure.local_configuration
        tags: local_configuration
      - role: bluebanquise.infrastructure.repositories
        tags: repositories
      - role: bluebanquise.infrastructure.nic
        tags: nic
      - role: bluebanquise.infrastructure.dhcp_server
        tags: dhcp_server
      - role: bluebanquise.infrastructure.dns_client
        tags: dns_client
      - role: bluebanquise.infrastructure.dns_server
        tags: dns_server
      - role: bluebanquise.infrastructure.http_server
        tags: http_server
      - role: bluebanquise.infrastructure.pxe_stack
        tags: pxe_stack
      - role: bluebanquise.infrastructure.ssh_client
        tags: ssh_client
      - role: bluebanquise.infrastructure.time
        tags: time
        vars:
          time_profile: server

Note that this is a basic example to have a working basic cluster. More roles are available in the infrastructure collection.

Then, we will ask Ansible to read this playbook, and execute all roles listed
inside on management1 host (check hosts at top of the file).

To do so, we are going to use the ``ansible-playbook`` command.

Ansible-playbook
----------------

``ansible-playbook`` is the command used to ask Ansible to execute a playbook.

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

Note: you need to use json syntax to pass dicts or list to extra vars.

Apply management1 configuration
-------------------------------

Lets apply now the whole configuration on management1. It can take some time
depending on your CPU and your hard drive, and your network connection when using external repositories.

We first ensure our NICs are up, so the repositories part is working.
Ensure not to cut your connection if working remotely.

.. code-block:: text

  ansible-playbook playbooks/managements.yml -b -i inventory --limit management1 --tags local_configuration,nic

Check interfaces are up (check using ``ip a`` command), and then setp repositories:

.. code-block:: text

  ansible-playbook playbooks/managements.yml -b -i inventory --limit management1 --tags repositories

Then play the whole playbook:

.. code-block:: text

  ansible-playbook playbooks/managements.yml -b -i inventory --limit management1

And wait...

If all went well, you can check that all services are up and running.

.. note::
  You can replay the same ansible-playbook command over and over, Ansible will
  just update/correct what is needed, and do nothing for all that is at an
  expected state.

Now that management1 is up and running, it is time to deploy the other hosts.

Deploy OS on other hosts: PXE
=============================

Next step is to deploy the other hosts using PXE process.

NOTE: it is assumed here you know how to have your other hosts / VM / servers /
workstation to boot on LAN.

If your device cannot boot on LAN, use iso or usb image provided on management1
in /var/www/html/pxe/bin/[x86_64|arm64]. These images
will start a LAN boot automatically, even if your computer is not PXE able
natively.

In **BlueBanquise**, PXE process has been made so that any kind of hardware able
to boot PXE, USB or CDrom can start deployment.

PXE process overview
--------------------

You can get more information and a detailed schema in the pxe_stack role section
of this documentation. Simply explained, the PXE chain is the following (files
are in /var/www/html/pxe):

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
``http://${next-server}/pxe/convergence.ipxe``. Then this
file chain to host specific file in hosts (this file is generated using *bluebanquise-bootset*
command). The host specific file contains the default entry for the iPXE menu,
then host chain to its equipment_profile file, to gather group values, and chain
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

bluebanquise-bootset
--------------------

Before booting remote hosts in PXE, we need to ask management1 to activate
remote hosts deployment. If not, remote hosts will not be able to grab their
dedicated configuration from management host at boot.

To manipulate hosts PXE boot on management1 (aka set PXE chain configuration), a command, ``bluebanquise-bootset``, is available.

We are going to deploy login1, storage1 and compute1, compute2, compute3 and compute4.

Let's use bluebanquise-bootset to set them to deploy OS at next PXE boot (bluebanquise-bootset must be launched using sudo if not root):

.. code-block:: bash

  sudo bluebanquise-bootset -n login1,storage1,c[001-004] -b osdeploy

You can check the result using:

.. code-block:: bash

  sudo bluebanquise-bootset -n login1,storage1,c[001-004] -s

Which should return:

.. code-block:: text

  [INFO] Loading /etc/bluebanquise-bootset/nodes_parameters.yml
  [INFO] Loading /etc/bluebanquise-bootset/pxe_parameters.yml
  Next boot deployment: c[001-004],login1,storage1

Note that this osdeploy state will be automatically updated once OS is deployed
on remote hosts, and set to disk.

You can also force hosts that boot on PXE to boot on disk using ``-b disk``
instead of ``-b osdeploy``.

Please refer to the pxe_stack role dedicated section in this documentation for
more information on the bluebanquise-bootset usage.

SSH public key
--------------

In order to log into the remote hosts without giving the password, check that
the ssh public key defined in your os groups inventory (``os_admin_ssh_keys key``) matches your
management1 public key (the one generated in /var/lib/bluebanquise/.ssh/). If not, update the
inventory and remember to re-run the pxe_stack role (to update
PXE related files that contains the ssh public key of the management host to be
set on hosts during deployment).

.. code-block:: bash

  ansible-playbook playbooks/managements.yml -b -i inventory --limit management1 --tags pxe_stack

OS deployment
-------------

Power on now the remote hosts, have them boot over LAN, and watch the automatic
installation procedure. It should take around 5-20 minutes depending on your
hardware.

Once done, proceed to next part.

Apply other hosts configuration
===============================

Now that all the hosts have an operating system installed and running, applying
configuration on these hosts is simple.

Ensure first you can ssh passwordless on each of the freshly deployed hosts.

.. note::
  On some Linux distributions, if DHCP leases are short, you may loose
  ip shortly after system is booted. If that happen, reboot system to get an ip
  again. This issue is solved once the nic role has been applied on hosts,
  as it sets ip statically.

We will deploy configuration on compute1 host as an example.

Create file ``playbooks/computes.yml`` with the following content:

.. code-block:: yaml

  ---
  - name: computes playbook
    hosts: "fn_compute" # This is a group
    roles:

      # Infrastructure

      - role: bluebanquise.infrastructure.hosts_file
        tags: hosts_file
      - role: bluebanquise.infrastructure.local_configuration
        tags: local_configuration
      - role: bluebanquise.infrastructure.repositories
        tags: repositories
      - role: bluebanquise.infrastructure.nic
        tags: nic
      - role: bluebanquise.infrastructure.ssh_remote_keys
        tags: ssh_remote_keys
      - role: bluebanquise.infrastructure.time
        tags: time
        vars:
          time_profile: client

And execute it while targeting compute1 (if you do not limit it, it will deploy configuration in parallel on all the members of the fn_compute group):

.. code-block:: bash

  ansible-playbook playbooks/computes.yml -b -i inventory --limit compute1

If you do not set the limite, and have multiple compute hosts up and running,
you will see that Ansible will work on computes hosts in parallel, using more CPU
on the management1 host (by spawning multiple forks).

-------------

Your cluster should now be fully deployed the generic way: operating systems are
deployed on each hosts, and basic services (DNS, repositories, time
synchronization, etc.) are up and running.

You can now use the other sections to go futher and specialize your cluster.

Thank your for following this training. I really hope you will enjoy the stack.
Please report me any bad or good feedback.
