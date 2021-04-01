Prometheus server
-----------------

Description
^^^^^^^^^^^

This role deploy prometheus server with alertmanager.

Instructions
^^^^^^^^^^^^

Default ports
"""""""""""""

Prometheus is available at http://localhost:9090

Alertmanager is available at http://localhost:9093

Node_exporter is available at http://localhost:9100

General configuration
"""""""""""""""""""""

By default, role will inherit from values set in its defaults folder.
You may wish to update these values to your needs, as these values set the
different timings used by Prometheus.

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

.. note::
  The prometheus_server role will try to read the prometheus_client
  related files, to generate its configuration (register exporters to scrape for
  each equipment profile group of nodes). See the prometheus_client role
  documentation for more details.

.. seealso::
  * https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config
  * https://www.robustperception.io/whats-the-difference-between-group_interval-group_wait-and-repeat_interval

Alerting
""""""""

By default, the role will only add a simple alerts file into the
/etc/prometheus/alerts folder. This file contains a basic alert that fire when
an exporter is down.

You will probably wish to add more alerts. Few alerts are proposed by the stack,
and are provided as examples in the /usr/share/doc/bluebanquise/prometheus/
folder.

You can simply copy the whole files that are needed, or a part of them, and tune
them according to your needs.

.. note::
  When possible, we added our references from the web inside the example files.

To be done
^^^^^^^^^^

Allow groups alerts selection.

Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
