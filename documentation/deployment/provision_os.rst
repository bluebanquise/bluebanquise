============
Provision OS
============

This is the moment many of us enjoy the most: watching bare hosts boot from the network, install
their operating system on their own, and come back ready to be configured. Let's go through it
together.

We assume here that your inventory is ready (see the General configuration section), and that the
management host already runs its own operating system. If you are not sure in which order to do
things, :doc:`strategy` gives the big picture.

Prepare the management host
===========================

Bootstrap BlueBanquise
----------------------

The bootstrap script installs a few dependencies, creates the ``bluebanquise`` user (home
``/var/lib/bluebanquise``, sudoer), installs Ansible and the BlueBanquise collection in a virtual
environment, clones the BlueBanquise repository in ``/var/lib/bluebanquise/bluebanquise`` (for its
``ansible.cfg`` and reference files), and generates an SSH key pair for this user. The ``sudo``
command must be available. As root, or with a sudoer user:

.. code-block:: bash

  curl -o online_bootstrap.sh https://raw.githubusercontent.com/bluebanquise/bluebanquise/master/bootstrap/online_bootstrap.sh
  chmod +x online_bootstrap.sh
  sudo ./online_bootstrap.sh

The script is verbose on purpose, so you can follow what it does, and quickly spot what went wrong
if something does. Once done, let's switch to the ``bluebanquise`` user, which we will use for all
the rest of this documentation:

.. code-block:: bash

  sudo su - bluebanquise

If you created your inventory somewhere else, copy it now under ``/var/lib/bluebanquise/inventories/``.

Add the BlueBanquise repository
-------------------------------

Some roles, like ``pxe_stack``, install packages built by the BlueBanquise project (iPXE roms,
tools, Python environment). Let's make the BlueBanquise repository known to the management host, by
adding it to ``bb_repositories``, for example in ``group_vars/all/repositories.yml`` (or in the
operating system group of the management host if your cluster mixes distributions).

Pick the entry matching the distribution of the management host:

* RHEL 9 (and compatible: AlmaLinux, Rocky Linux...):

  .. code-block:: yaml

    bb_repositories:
      - name: bluebanquise
        baseurl: https://bluebanquise.com/repository/releases/latest/el9/x86_64/bluebanquise/

* RHEL 10 (and compatible):

  .. code-block:: yaml

    bb_repositories:
      - name: bluebanquise
        baseurl: https://bluebanquise.com/repository/releases/latest/el10/x86_64/bluebanquise/

* Ubuntu 24.04:

  .. code-block:: yaml

    bb_repositories:
      - repo: deb [trusted=yes] https://bluebanquise.com/repository/releases/latest/u24/x86_64/bluebanquise/ noble main

* Ubuntu 26.04:

  .. code-block:: yaml

    bb_repositories:
      - repo: deb [trusted=yes] https://bluebanquise.com/repository/releases/latest/u26/x86_64/bluebanquise/ resolute main

* Debian 13:

  .. code-block:: yaml

    bb_repositories:
      - name: bluebanquise
        trusted: true
        uris: https://bluebanquise.com/repository/releases/latest/deb13/x86_64/bluebanquise/
        suites: trixie
        components: main

* OpenSuse Leap 16:

  .. code-block:: yaml

    bb_repositories:
      - name: bluebanquise
        disable_gpg_check: true
        repo: https://bluebanquise.com/repository/releases/latest/osl16/x86_64/bluebanquise/

.. note::

  On RHEL and compatible distributions, some packages also need the CodeReady Builder repository
  (``crb``), and EPEL. The **repositories** role documentation explains all available formats.

Configure the management host
-----------------------------

Now let's apply the configuration on the management host. A playbook lists the roles to run; for a
first, basic cluster, create ``/var/lib/bluebanquise/playbooks/management.yml``:

.. code-block:: yaml

  ---
  - name: management playbook
    hosts: "fn_management"
    roles:
      - role: bluebanquise.infrastructure.hosts_file
        tags: hosts_file
      - role: bluebanquise.infrastructure.local_configuration
        tags: local_configuration
      - role: bluebanquise.infrastructure.repositories
        tags: repositories
      - role: bluebanquise.infrastructure.nic
        tags: nic
      - role: bluebanquise.infrastructure.firewall
        tags: firewall
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

The ``firewall`` role comes before the roles providing services: each of them opens its own ports in
firewalld, which must therefore already be running (see :doc:`../configuration/services`).

We first bring network interfaces and repositories up, so the rest of the run can install packages.
If you are connected remotely, double check the ``network_interfaces`` of the management host
before running this, so you do not cut the branch you are sitting on!

.. code-block:: bash

  cd /var/lib/bluebanquise
  ansible-playbook playbooks/management.yml -i inventories/new_cluster -b --limit mgt1 --tags nic,repositories

Check with ``ip a`` that interfaces are up as expected, then run the whole playbook:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventories/new_cluster -b --limit mgt1

And let it work for a few minutes. You can replay this command as many times as you like: Ansible
only changes what is not already in the expected state. :doc:`apply_configuration` explains all the
options of the ``ansible-playbook`` command.

Provide operating system images
===============================

To install hosts through the network, the management host needs the installation media of each
distribution (and architecture) you plan to deploy. They live under
``/var/www/html/pxe/netboots/<distribution>/<version>/<architecture>/`` (``/srv/www/htdocs/pxe/...``
on OpenSuse), following the ``os_operating_system`` and ``hw_architecture`` values of your
inventory.

The ``bluebanquise-netboots-installer`` tool, installed by the ``pxe_stack`` role, does all the work
for you: it downloads the ISO, checks it, and extracts it at the right place.

.. code-block:: bash

  sudo bluebanquise-netboots-installer list
  sudo bluebanquise-netboots-installer install rhel_10 x86_64
  sudo bluebanquise-netboots-installer install rhel_10 arm64

On an air-gapped cluster, download the ISO from another host, copy it on the management host, and
give it to the tool:

.. code-block:: bash

  sudo bluebanquise-netboots-installer install ubuntu_24.04 x86_64 --netboot /var/lib/bluebanquise/ubuntu-24.04-live-server-amd64.iso

The catalog of known images, ``/etc/bluebanquise/bootset/netboots_installer.yml``, is never
overwritten by the role: feel free to point it to your local mirrors, or to add new entries. The
**pxe_stack** role documentation also details how to do it manually, for each distribution.

.. note::

  At least 20 GB of free space is needed: the tool checks it before starting.

How hosts boot from the network
===============================

Before powering anything on, let's take a minute to understand what is going to happen. The
**pxe_stack** role documentation has all the details; here is the short story (files are under
``/var/www/html/pxe``):

.. code-block:: text

  DHCP request
    |
  IP and next-server obtained
    |
  Download (tftp) and load the BlueBanquise iPXE rom
    |
  DHCP request again, from the iPXE rom
    |
  iPXE chains to convergence.ipxe (http)
    |
  iPXE chains to nodes/<hostname>.ipxe (host values: what to do next)
    |
  iPXE chains to equipment_profiles/<equipment_profile>.ipxe (group values)
    |
  iPXE chains to menu.ipxe
    |
  iPXE chains to the selected entry (deploy OS, boot on disk, diskless, tools, ...)

Whatever the boot source (PXE, USB, CD) and firmware (legacy BIOS or UEFI), all paths converge to
``http://${next-server}/pxe/convergence.ipxe``. If a host cannot boot over the network on its own,
boot it on the iPXE ISO or USB images available in ``/var/www/html/pxe/bin/``: they start the very
same chain.

The menu waits 10 seconds, then starts the entry chosen for the host, its ``menu-default``.
Installers (kickstart for RHEL, autoinstall for Ubuntu, preseed for Debian, Agama for OpenSuse Leap
16, AutoYaST for Leap 15) get all their settings from the inventory: partitioning, admin password
and SSH keys, packages, kernel parameters, and more (see :doc:`../configuration/os_settings`).

These slides walk through the whole process:

.. raw:: html

  <!-- from https://www.w3schools.com/howto/howto_js_slideshow.asp -->
  <script>
  var slideIndex = 1;
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
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide1.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">2 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide2.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">3 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide3.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">4 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide4.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">5 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide5.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">6 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide6.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">7 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide7.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">8 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide8.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">9 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide9.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">10 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide10.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">11 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide11.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">12 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide12.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">13 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide13.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">14 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide14.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">15 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide15.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">16 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide16.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">17 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide17.PNG" style="width:100%">
     </div>
     <div class="mySlides">
       <div class="numbertext">18 / 18</div>
       <img src="../_static/deploy_bluebanquise_pxe_slides/Slide18.PNG" style="width:100%">
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

``[SCHEMA: pxe-boot-chain]``
  *A vertical flow of the iPXE chain above: a host on the left, the management host on the right,
  with arrows labelled DHCP, TFTP and HTTP, and one box per chained file (convergence.ipxe,
  nodes/<hostname>.ipxe, equipment profile file, menu.ipxe, osdeploy/<distribution>.ipxe). A last
  arrow from the installed host back to the PXE stack daemon, labelled "stage_report osdeploy
  completed", switching the host file to "disk".*

Choose what hosts do at next boot
=================================

Each host gets its own file, ``pxe/nodes/<hostname>.ipxe``, telling it what to do at next network
boot. We change it with the ``bluebanquise-bootset`` command (as root, or with sudo). Let's ask our
hosts to deploy their operating system:

.. code-block:: bash

  sudo bluebanquise-bootset -n login1,storage1,c[001-004] -b osdeploy

And check the result:

.. code-block:: bash

  sudo bluebanquise-bootset -n login1,storage1,c[001-004] -s

Hosts are grouped by their next boot target (``menu-default``), with their last reported status and
what remains in their boot queue:

.. code-block:: text

  menu-default=osdeploy :
    c001: [status: NA] [queue: osdeploy]
    c002: [status: NA] [queue: osdeploy]
    ...

During the installation, the status becomes ``osdeploy running``, then ``osdeploy completed``, with
its date. Once the installation succeeds, the host reports it to the PXE stack daemon, which
switches it to ``disk``: the host will not reinstall itself in a loop at next reboot.

``bluebanquise-bootset`` has a few more tricks:

* ``-b disk``: boot on the local disk.
* ``-b memtest,osdeploy``: a boot sequence, run in order. Here, a memory test first, then an OS
  deployment.
* ``-e "<kernel parameters>"``: additional kernel parameters for the next deployment.
* ``-b diskless -i <image>``: boot a diskless image.

The **pxe_stack** role documentation describes all of them.

Check SSH keys
==============

Once installed, hosts must accept SSH connections from the ``bluebanquise`` user of the management
host, without password, so Ansible can configure them. The keys allowed on deployed hosts come from
``os_admin_ssh_keys`` in your operating system groups: check the public key of the ``bluebanquise``
user (``/var/lib/bluebanquise/.ssh/id_ed25519.pub``) is part of it. If you add it now, re-run the
``pxe_stack`` role, so installation files include it:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventories/new_cluster -b --limit mgt1 --tags pxe_stack

Deploy
======

Everything is ready: power on the hosts (or use their BMC, see :doc:`../operations/operations`), let
them boot over the network, and watch the installation run. It usually takes 5 to 20 minutes,
depending on your hardware.

To follow what is going on from the management host:

* ``sudo bluebanquise-bootset -n <hosts> -s`` shows the progress of each host.
* The http server logs (``/var/log/httpd/access_log`` on RHEL, ``/var/log/apache2/access.log`` on
  Ubuntu and Debian) show each file of the chain being downloaded.
* ``journalctl -u bluebanquise-pxe-stack-daemon -f`` shows the stage reports the daemon receives.

If a host stops on an iPXE shell, read the message on its screen: it explains why (unknown host,
missing host file, missing image...). Most of the time, the host is missing from the inventory, or
the ``pxe_stack`` role must be re-run after an inventory change.

.. note::

  Some distributions use short DHCP leases at first boot. If a freshly installed host loses its IP
  address, simply reboot it: once the ``nic`` role is applied, addresses are static.

When hosts are up and reachable with SSH, the last step is to configure them: let's continue with
:doc:`apply_configuration`.
