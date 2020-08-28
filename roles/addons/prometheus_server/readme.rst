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

By default, role will inherit from values set in its defaults folder.
You may wish to update these values to your needs, as these values set the
different timings usd by Prometheus.

To do so, create file inventory/group_vars/all/addons/prometheus.yml with the
following content:

.. code-block:: yaml

  prometheus:
    scrape_interval: 1m
    evaluation_interval: 2m
    alertmanager:
      group_wait: 1m
      group_interval: 10m
      repeat_interval: 3h

And tune according to your needs.

Note also that the prometheus_server role will try to read the prometheus_client
related files, to generate its configuration (register exporters to scrape for
each equipment profile group of nodes). See the prometheus_client role
documentation for more details.

.. seealso::
  * https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config
  * https://www.robustperception.io/whats-the-difference-between-group_interval-group_wait-and-repeat_interval

To be done
^^^^^^^^^^

Allow groups alerts selection.

Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
