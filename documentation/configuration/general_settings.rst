================
General settings
================

Set global settings
-------------------

The first step in building the inventory is to set global settings.
This includes the name of the cluster, the domain name of the cluster, and the time zone of the cluster.

Create file ``group_vars/all/dns.yml`` with the following content:

.. code-block:: yaml

  bb_domain_name: bluebanquise-cluster.local

Create file ``group_vars/all/time.yml`` with the following content:

.. code-block:: yaml

  bb_time_zone: Europe/Brussels

Create file ``group_vars/all/global.yml`` with the following content:

.. code-block:: yaml

  bb_cluster_name: bluebanquise-cluster

Tune these values according to your needs.

Note that these variables are used by all roles of the stack. However, each role can overwrite the global settings by its own.
Please refer to each service parameters for more details.

Services global settings
------------------------

It is possible to manage all services systemd's start/stop behavior via 2 global variables:

* ``bb_start_services``: Start or not services when applying configuration.
* ``bb_enable_services``: Enable or not services at system start when applying configuration.

Example:

.. code-block:: yaml

  bb_start_services: true
  bb_enable_services: true

Default is true for both if not set.
