Prometheus server
-----------------

Description
^^^^^^^^^^^

This role deploy prometheus server with alertmanager.

Instructions
^^^^^^^^^^^^

Prometheus is available at http://localhost:9090

Alertmanager is available at http://localhost:9093

Node_exporter is available at http://localhost:9100

In order to allow the role to deploy, you need to add the following 
content under a file inventory/group_vars/all/addons/monitoring.yml :

.. code-block:: yaml

  prometheus:
    scrape_interval: 1m
    evaluation_interval: 2m
    alertmanager:
      group_wait: 1m
      group_interval: 10m
      repeat_interval: 3h

See the main Prometheus documentation if you wish to tune these parameters.

To be done
^^^^^^^^^^

Allow groups alerts selection.

Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
