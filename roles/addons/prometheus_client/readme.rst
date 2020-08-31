Prometheus client
-----------------

Description
^^^^^^^^^^^

This role deploy exporters on clients for Prometheus queries.

Instructions
^^^^^^^^^^^^

Each role has its own http port. For example, Node_exporter is available at
http://localhost:9100 .

In order for this role to install and start exporters on the host, a
configuration is required in the Ansible inventory.

A file is needed for each equipment_profile group that should be monitored.

For example, to have equipment_typeC nodes installing and testing the
node_exporter, you will need to create file
inventory/group_vars/equipment_typeC/monitoring.yml with the following content:

.. code-block:: yaml

  monitoring:
    exporters:
      node_exporter:
        package: node_exporter
        service: node_exporter
        port: 9100

And for example, on your management nodes, you may wish to have more exporters
setup to monitor much more things. This would be here, assuming managements
nodes are from equipment group equipment_typeM, a file
inventory/group_vars/equipment_typeM/monitoring.yml with the following content:

.. code-block:: yaml

  monitoring:
    exporters:
      node_exporter:
        package: node_exporter
        service: node_exporter
        port: 9100
      ha_cluster_exporter:
        package: ha_cluster_exporter
        service: ha_cluster_exporter
        port: 9664
      slurm_exporter:
        package: slurm_exporter
        service: slurm_exporter
        scrape_interval: 5m
        scrape_timeout: 5m
        port: 9817

You can see here that it is possible to customize the scrape_interval and
scrape_timeout.

.. note::
  Note that the ipmi_exporter and snmp_exporter do not need to be included here
  as their behavior are different (they act as relay for other targets) and so are
  directly deployed by the prometheus_server role.

To be done
^^^^^^^^^^

Allow groups alerts selection.

Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. johnnykeats <johnny.keats@outlook.com>
