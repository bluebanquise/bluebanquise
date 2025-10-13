======
System
======

Set global settings
-------------------

The first step in building the inventory is to set global settings.
This includes the name of the cluster, the domain name of the cluster, and the time zone of the cluster.

Create file ``group_vars/all/global.yml`` with the following content:

.. code-block:: yaml

  bb_domain_name: bluebanquise-cluster.local
  bb_time_zone: Europe/Brussels
  bb_cluster_name: bluebanquise-cluster

Tune these values according to your needs.

Note that these variables are used by all roles of the stack. However, each role can overwrite the global settings by its own.
Please refer to each service parameters for more details.
