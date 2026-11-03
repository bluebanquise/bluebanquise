================
General settings
================

Before describing networks and hosts, let's give our cluster a few global settings. They are shared
by all roles of the stack, so they only need to be set once.

Domain name and time zone
=========================

Create the file ``group_vars/all/dns.yml``, with the domain name of the cluster:

.. code-block:: yaml

  bb_domain_name: bluebanquise-cluster.local

Then the file ``group_vars/all/time.yml``, with the time zone of the cluster:

.. code-block:: yaml

  bb_time_zone: Europe/Brussels

.. tip::

  ``timedatectl list-timezones`` lists all available time zones.

Of course, tune these values to your needs. File names are only a convention to keep things tidy:
Ansible reads all files of ``group_vars/all/``, whatever their name.

Global variables
================

Global variables start with the ``bb_`` prefix. A role always uses its own dedicated variable first
when it is set (for example ``time_time_zone`` for the ``time`` role), then the global one, then its
default value. This way, a single global setting covers the whole cluster, while each role can
still be tuned on its own.

.. list-table::
   :header-rows: 1

   * - Variable
     - Default
     - Description
   * - ``bb_domain_name``
     - none
     - Domain name of the whole cluster.
   * - ``bb_time_zone``
     - ``Europe/Brussels``
     - Time zone of the whole cluster.
   * - ``bb_repositories``
     - none
     - Package repositories to configure on hosts (see the ``repositories`` role).
   * - ``bb_start_services``
     - ``true``
     - Start services, and restart them on configuration changes.
   * - ``bb_enable_services``
     - ``true``
     - Enable services at boot.
   * - ``bb_services_firewall_zone``
     - ``public``
     - Firewalld zone in which services open their ports.
   * - ``bb_restrict_to_group``
     - ``all``
     - Restrict the hosts some roles take into account (DHCP, DNS, hosts file, PXE, consoles,
       power management, ssh client) to an Ansible group.
   * - ``bb_enable_flat_optimizations``
     - ``false``
     - Use an optimized generation logic for the hosts file on very large clusters.

The full list, with the roles using each variable, is in the data model reference
(``resources/data_model.md`` at the root of the repository).

Services global settings
========================

``bb_start_services`` and ``bb_enable_services`` are mainly useful for high availability clusters,
where a cluster manager decides on which host a service runs: services are then installed and
configured everywhere, but neither started nor enabled by Ansible. You can safely ignore them
otherwise.

.. code-block:: yaml

  bb_start_services: true
  bb_enable_services: true

See :doc:`services` for how to tune them per role, and :doc:`../scalability/high_availability` for
their typical usage.
