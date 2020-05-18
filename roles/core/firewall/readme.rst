Firewall
--------

Description
^^^^^^^^^^^

This role configures the firewall service on the hosts. It is currently
restricted to CentOS and RHEL only.

For each network interface of the host where the play runs, this role binds the
source address **subnet/prefix** to the **internal** zone if the network must
be in the firewall.

The **internal** zone is used by any other roles which needs to add services or
ports to the firewall configuration.

Instructions
^^^^^^^^^^^^

TBD

**Inventory configuration**
"""""""""""""""""""""""""""

Enable or disable the firewall in the equipment profile:

.. code-block:: yaml

  equipment_profile:
    firewall: true

When firewall is enabled, this role will add all the networks of the host where
**is_in_firewall** is true to the **internal** zone:

.. code-block:: yaml

  networks:
    ice1-1:
      subnet: 10.10.0.0
      prefix: 16
      netmask: 255.255.0.0
      broadcast: 10.10.255.255
      gateway: 10.10.2.1
      is_in_firewall: true  <<<<<<<<<<

To be done
^^^^^^^^^^

- Add support for Ubuntu and OpenSUSE

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Bruno Travouillon <devel@travouillon.fr>
