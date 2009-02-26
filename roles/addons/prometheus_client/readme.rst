Prometheus client
-----------------

Description
^^^^^^^^^^^

This role deploy node_exporter for Prometheus queries.

Instructions
^^^^^^^^^^^^

Node_exporter is available at http://localhost:9100

exporters configuration file to add to inventory/group_vars/equipment_type_X
depending on where the exporter should be:

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

  # Define alerts related to selected exporters
  alerts:
    Exporter_down:

To be done
^^^^^^^^^^

Allow groups alerts selection.

Changelog
^^^^^^^^^

* 1.0.0: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. johnnykeats <johnny.keats@outlook.com>
 
