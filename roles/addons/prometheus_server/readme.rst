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

Here is an example of the prometheus.yml file found under /etc/bluebanquise/inventory/group_vars/all:

.. code-block:: yaml

  
  prometheus:
    scrape_interval: 1m
    evaluation_interval: 2m
    alertmanager:
      global:
        smtp_smarthost: 'localhost:25'
        smtp_sender: 'alertmanager@your_domain'
        smtp_tls: false
      route:
        group_wait: 1m
        group_interval: 10m
        repeat_interval: 3h
      receivers:
        name: 'sys-admin-team'
        email: 'sys-admin-team@site.com'  


To be done
^^^^^^^^^^

Allow groups alerts selection.

Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
