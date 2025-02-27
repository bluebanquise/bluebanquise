======================
Bootstrap BlueBanquise
======================

BlueBanquise can be used to deploy from a simple IT room for students, to High
Performance Computing clusters. Configuration is the same in both cases, only
size and specialized roles are different.

In this documentation, most of the time, we will refer to "servers", but any
kind of workstation will work the same way.

This documentation will cover the configuration of a very simple cluster:

.. image:: images/clusters/documentation_example_single_island.svg
   :align: center

More complex clusters are detailed later, once the generic part is done.

.. note::
   It is important to note that the documentation focus on main inventory parameters of the stack.
   However, **more features are available in the stack**. Read roles Readme files to learn
   more about each role capabilities.

The first step is to bootstrap the first management server/workstation of the
cluster.

This procedure mainly depend on the Linux distribution chosen. Please follow the
target system procedure, but first step is to download iso and write it on an
USB device to install manually first management node operating system.

.. image:: images/misc/linux_usb_stick.svg
   :align: center

Depending of your Linux distribution, choose the bootstrap steps to follow:

* :ref:`Bootstrap RHEL like system`
* :ref:`Bootstrap Ubuntu like system`
* :ref:`Bootstrap Debian like system`
* :ref:`Bootstrap SUSE like system`

Install RHEL like system
========================

In the following documentation, the RHEL logo will means "this part is dedicated
to RHEL like distributions", and so will concern the following distributions:

.. raw:: html

  <div style="padding: 6px;">
  <b>RHEL</b> <img src="_static/logo_rhel.png">, <b>CentOS</b> <img src="_static/logo_centos.png">, <b>RockyLinux</b> <img src="_static/logo_rocky.png">, <b>OracleLinux</b> <img src="_static/logo_oraclelinux.png">, <b>CloudLinux</b> <img src="_static/logo_cloudlinux.png">, <b>AlmaLinux</b> <img src="_static/logo_almalinux.png">
  </div><br><br>

Currently supported Linux RHEL like distributions are:

* Major version: 8
    * RHEL
    * RockyLinux
    * OracleLinux
    * CloudLinux (with external repositories)
    * AlmaLinux
* Major version: 9
    * RHEL
    * RockyLinux
    * OracleLinux
    * CloudLinux (with external repositories)
    * AlmaLinux

.. note::
  In the following documentation, we will always use *redhat/8/x86_64/* or
  *redhat/9/x86_64/* when setting path. Adapt this to your target distribution
  and architecture.
  Distribution keywords supported are: **redhat**, **rhel**, **centos**,
  **rockylinux**, **oraclelinux**, **cloudlinux**, **almalinux**. All these 
  keywords are linked to **redhat**.
  And supported architecture are **x86_64** or **arm64**.

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 4 Gb RAM
* >= 40 Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 2 Gb RAM (Anaconda PXE part needs a lot of RAM, once system is installed, can be reduced to 1Gb)
* >= 20 Gb HDD

OS installation
---------------

Simply write iso **directly** on USB stick like a binary image, do not use a
special tool.

You can follow the `Almalinux installation guide <https://wiki.almalinux.org/documentation/installation-guide.html>`_
for that, which is very well made.

Then install the Linux operating system manually (boot on USB, etc).

It is recommended to only choose minimal install during packages selection
(core or minimal server), to reduce load and attack surface.
Also, it is **STRONGLY** recommended to let system in English (US), and only
set your keyboard and time zone to your country.

Once done, proceed to :ref:`Boottsrap script`.

Install Ubuntu/Debian like system
=================================

.. raw:: html

  <div style="padding: 6px;">
  <b>Ubuntu</b> <img src="_static/logo_ubuntu.png">, <b>Debian</b> <img src="_static/logo_debian.png">
  </div><br><br>

Currently supported Linux Ubuntu distributions are:

* Ubuntu 20.04
* Ubuntu 22.04
* Ubuntu 24.04

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 8 Gb RAM
* >= 40 Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 6 Gb RAM (PXE part needs a lot of RAM, once system is installed, can be reduced to 1Gb)
* >= 20 Gb HDD

OS installation
---------------

Simply write iso **directly** on USB stick like a binary image, do not use a
special tool.

You can follow installation guide of 
`Ubuntu <https://help.ubuntu.com/community/Installation/FromUSBStick>`_ or 
`Debian <https://wiki.debian.org/DebianInstall>`_ for that.


Then install the Linux operating system manually (boot on USB, etc).

It is recommended to only choose minimal install during packages selection
(core or minimal server), to reduce load and attack surface. Remember to 
ask for openssh-server installation during additional packages selection.
Also, it is **STRONGLY** recommended to let system in English (US), and only
set your keyboard and time zone to your country.

Once done, proceed to :ref:`Boottsrap script`.


Install SUSE like system
========================

OpenSuse Leap 15
----------------

Notes:

* You can also use SLES 15, but you will require an active SLES subscription to receive updates.

The following configuration is recommended:

* >= 2 CPU/vCPU
* >= 4 Gb RAM
* >= 40 Gb HDD

And the following minimal configuration is the strict minimal if you wish to
test the stack in VMs:

* >= 1 vCPU
* >= 2 Gb RAM
* >= 20 Gb HDD

Simply write iso **directly** on USB stick like a binary image, do not use a
special tool.

You can follow the `OpenSuse documentation <https://en.opensuse.org/Create_installation_USB_stick>`_ for that, it is well made.

Then install the Linux operating system manually (boot on USB, etc).

It is recommended to only choose minimal install during packages selection, to reduce load and attack surface.
Also, it is **STRONGLY** recommended to let system in English (US), and only
set your keyboard and time zone to your country.

Once done, proceed to :ref:`Boottsrap script`.

Boottsrap script
================

Now that you have install your primary system, which will act as your management node,
it is time to bootstrap the BlueBanquise stack on it.



-------------

It is now time to configure BlueBanquise.
