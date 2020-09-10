Prometheus
==========

In this topic, we will see how to configure and deploy both prometheus_server
and prometheus_client Ansible roles.

Prerequisites
-------------

* Have ansible installed
* Know how to use playbooks

Also, make sure those packages are present on your system (they should be in the
bluebanquise or any other repository):

* prometheus
* alertmanager
* karma
* ipmi_exporter
* snmp_exporter
* grafana

Installation
------------

Prometheus Server
^^^^^^^^^^^^^^^^^

First create file
/etc/bluebanquise/inventory/group_vars/all/addons/prometheus.yml with the
following content:

.. code-block:: yaml

  prometheus:
  scrape_interval: 1m
  evaluation_interval: 2m
  alertmanager:
    group_wait: 1m
    group_interval: 10m
    repeat_interval: 3h

.. seealso:: https://www.robustperception.io/whats-the-difference-between-group_interval-group_wait-and-repeat_interval

Now, simply add to the playbook of your choice (which is for the Prometheus
server) the prometheus_server role (change the values of enable_services and start_services accordingly):

.. code-block:: yaml
  
  vars:
    - enable_services: true
    - start_services: true
  roles:
    - role: prometheus_server
      tags: prometheus_server


Then run:

.. code-block:: text

  ansible-playbook /etc/ansible/playbooks/<your server playbook> --tags prometheus_server

Now prometheus_server should be installed and configured with a minimal
configuration.

The configuration file for Prometheus is located under
/etc/prometheus/prometheus.yml.
It contains all the exporters to scrape, and more.

It is now time to configure client side. Note that while the
/etc/bluebanquise/inventory/group_vars/all/addons/prometheus.yml file is only
used by the prometheus_server role, the client files seen in next section will
be shared by both server and client role. Server will use it to know which
exporters to scrap on who, and clients will use it to know which exporters to
install locally.

Prometheus Client
^^^^^^^^^^^^^^^^^

For each *equipment_profile*, create a file called monitoring.yml that contains
the desired exporters to be deployed, into equipment_profile folder of your
target hosts groups.

For example, to set exporters to be scrapped and installed on all hosts of
equipment_profile equipment_XX, create the file
/etc/ansible/inventory/group_vars/equipment_XX/monitoring.yml, with the
following content:

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
        scrape_interval: 10m
        scrape_timeout: 4m
        port: 9664

This will setup here two exporters on these equipments: node_exporter and
ha_cluster_exporter.

Also don't forget to add the name of the package you want to install and the
service name.

.. note::
  As you can see, you can also add the scrape_interval (which is how
  often the metrics get scraped), and the scrape_timeout (which represents how
  long until a scrape request times out).

.. note::
  If you want to add exporters, make sure your package contains the
  binary and the .service file, put preferably under /usr/local/bin and
  /etc/systemd/system.

Now simply add to the playbook of your choice (which is for the Prometheus
clients) the prometheus_client role (change the values  of enable_services and start_services accordingly):

.. code-block:: yaml

  vars:
     - enable_services: true
     - start_services: true
  roles:
     - role: prometheus_client
       tags: prometheus_client

Then run:

.. code-block:: text

  ansible-playbook /etc/ansible/playbooks/<your client playbook> --tags prometheus_client

Now prometheus_client should be installed.

Also, re-execute the prometheus_server role on the management node hosting the
Prometheus server, to ensure Prometheus is now aware of these new exporters to
scrape.

.. code-block:: text

  ansible-playbook /etc/ansible/playbooks/<your server playbook> --tags prometheus_server

Prometheus.yml
--------------

File /etc/prometheus/prometheus.yml is where all the exporters and the scrape
related variables are stored for the Prometheus server to run.
It looks something like this:

.. code-block:: yaml

  global:
    scrape_interval: 1m
    evaluation_interval: 2m

  rule_files:
    - 'alerts/*.yml'

  alerting:
    alertmanagers:
    - static_configs:
      - targets:
        - localhost:9093

  scrape_configs:

    # I watch myself
    - job_name: 'prometheus_master'
      scrape_interval: 30s
      static_configs:
        - targets: ['localhost:9090']

  # GENERIC EXPORTER
  # All equipment profiles and their exporters
    - job_name: 'equipment_R_node_exporter'
      scrape_interval:
      scrape_timeout:
      static_configs:
        - targets: ['management1-1:9100']
        - targets: ['management1-2:9100']

Few notes:

* **rule_files** is where the alert related configurations are located
* **alerting** is where Prometheus should send alerts (i.e. Alertmanager)
* **scrape_configs** is where are defined all the exporters that server need to listen to, with the targets, and so on

.. seealso:: https://prometheus.io/docs/prometheus/latest/configuration/configuration/

It is now time to learn variables before using them in the Prometheus interface.

Variables
---------

There are 4 types of variable in Prometheus:

1. Counters
2. Gauges
3. Histograms
4. Summaries

Counters
^^^^^^^^

Counters are used for metrics that can only increase.
It is an incremental counter, that is used in order to know how rapidly
something grows for example.

.. note::

    For example, it is used for the number of packets that is transmitted by a switch interface.
    Using the irate function of Prometheus, we can then tell how many packets were transmitted in a given interval.

It can also be used for error counts, tasks completed, and so on.

Gauges
^^^^^^

Gauges are used for metrics that can go up, but can also decrease.
It gives a specific value for the time set.

.. note::

    For example, it is used for the temperature of the BMCs.
    This way, you have the temperature for any given time.
    It can also be used for memory usage, number of requests, and so on.

It can be used with function like min, max, average, and so on to get the
desired result.

Histograms & Summaries
^^^^^^^^^^^^^^^^^^^^^^

Histograms and summaries are more complex variable types, and are used less
often, which is the reason why we won't go too much in the details.
Histograms and summaries are both used for getting the request durations, or
the response sizes.
Their main goal is to watch for data that fall in a certain category.

.. seealso:: https://prometheus.io/docs/practices/histograms/

Queries
-------

In order to query a **metric** with Prometheus, you have to go to the Prometheus
web page.
By default, it is located at **http://localhost:9090** .

To query a metric, simply type in the metric name. You also have a dropdown list
with all the available metrics to query.

.. image:: /monitoring/capture/prometheus/query1.PNG
   :width: 80 %

If you want specific metrics (with one or more specific labels):

.. code-block:: text

  query_name{instance="instance"}

For example, ipmi_fan_speed_rpm{name="P-FAN1"} will only return the fan_speed of
the fan name "P-FAN-1":

.. image:: /monitoring/capture/prometheus/query2.PNG
   :width: 80 %

In the graph tab, you can also see the variation of the value over time.
You can also choose from when to when.

.. image:: /monitoring/capture/prometheus/query3.PNG
   :width: 80 %

Regex
^^^^^

You can also use the same queries, but with regex.

If you want the attribute to follow the given regex, the global syntax for is:

.. code-block:: text

  query{attribute=~"regex_value"}

Or if you don't want the attribute to follow the regex:

.. code-block:: text

  query{attribute!~"regex_value"}

.. note::

  The **tilda** here is very important.

Using this syntax, you can:

* get the metrics which attribute corresponds to a list

For example:

.. code-block:: text

  ipmi_fan_speed_rpm{name=~"MB-FAN5|MB-FAN4|S-FAN2"}

will return:

.. image:: /monitoring/capture/prometheus/query4.PNG
   :width: 50 %

* follow a pattern

For example:

.. code-block:: text

  ipmi_fan_speed_rpm{name=~".*.FAN.*"}

will return all the ipmi_fan_speed_rpm metrics with the string "FAN" in its
name label.

Another example:

.. code-block:: text

  ipmi_fan_speed_rpm{__name__=~"ipmi.*",instance=~"001-bmc"}

will return all the metrics which name starts with ipmi, and which instance is
001-bmc.

.. image:: /monitoring/capture/prometheus/query5.PNG
   :width: 50 %

Boolean operators
^^^^^^^^^^^^^^^^^

You can also combine different metrics, using boolean operators. There are
several operators in Prometheus. Some of them are the following:

* == (equal)
* != (not-equal)
* > (greater-than)
* < (less-than)
* >= (greater-or-equal)
* <= (less-or-equal)

These are used in order to get the results that correspond to the condition.
For example:

.. code-block:: text

  ipmi_up==1

will only return the instances of the query that are equal to one.

It is also possible to use logic operators:

* and (intersection)
* or (union)
* unless (complement)

Vector1 and vector2 results in a vector consisting of the elements of vector1
for which there are elements in vector2 with exactly matching label sets.
Other elements are dropped. The metric name and values are carried over from the
left-hand side vector.

For example:

.. code-block:: text

  node_exporter_build_info and ignoring(revision, version,goversion,branch,package) node_cpu_package_throttles_total

will return:

.. code-block:: text

  node_exporter_build_info{branch="HEAD",goversion="go1.12.5",instance="1-2:9100",job="equipment_R_node_exporter",revision="3db77732e925c08f675d7404a8c46466b2ece83e",version="0.18.1"}

because it has the same instance name and job name as a node_cpu_package_throttles_total.

Vector1 or vector2 results in a vector that contains all original elements (label sets + values) of vector1 and additionally all elements of vector2 which do not have matching label sets in vector1.

For example:

.. code-block:: text

  node_exporter_build_info or node_cpu_package_throttles_total

will return:

.. code-block:: text

  node_exporter_build_info{branch="HEAD",goversion="go1.12.5",instance="1-2:9100",job="equipment_R_node_exporter",revision="3db77732e925c08f675d7404a8c46466b2ece83e",version="0.18.1"}
  node_cpu_package_throttles_total{instance="1-2:9100",job="equipment_R_node_exporter",package="0"}
  node_cpu_package_throttles_total{instance="1-2:9100",job="equipment_R_node_exporter",package="1"}

Vector1 unless vector2 results in a vector consisting of the elements of vector1 for which there are no elements in vector2 with exactly matching label sets. All matching elements in both vectors are dropped.

There are also other types of boolean operators, like group_left or group_right,
in the online documentation.

.. seealso:: https://prometheus.io/docs/prometheus/latest/querying/operators/

Functions & aggregations
^^^^^^^^^^^^^^^^^^^^^^^^

Prometheus comes with a variety of querying functions. We will go through some
of the major ones:

* delta
* irate
* avg
* sum
* min, max

delta
"""""

*delta()* calculates the difference of value between the value from X minutes
ago and the current value.

Example:

.. code-block:: text

  delta(ipmi_current_amperes[5m])

.. image:: /monitoring/capture/prometheus/query6.PNG
   :width: 80 %

rate & irate
""""""""""""

*rate()* gives you the per second average rate of change over your range
interval.
*irate()* is the per second rate of change at the end of your range interval

The difference between rate and delta, is that rate automatically adjusts for
resets. It means that it only works with "counter" variables, i.e. a variable
that can only increase.
For example, if a metric value changes like this:

* 0
* 4
* 6
* 10

and resets:

* 2

Rate will capture the change, and will take the value of 2 as if it were 12 to
get the rate.

avg
"""

*avg()* returns the average value of **all** query results.

By default, it returns the avg value by job:

.. code-block:: text

  avg(ipmi_current_amperes)

.. image:: /monitoring/capture/prometheus/query8.PNG
   :width: 50 %

But you can also average by any other attribute, using avg(query) by(attribute):

.. image:: /monitoring/capture/prometheus/query9.PNG
   :width: 80 %

avg_over_time
"""""""""""""

*avg_over_time()* is self explanatory, it gives you the average value of a
metric during the given interval, **for each instance**.

For example if ipmi_current_amperes had the values: 2, 4, 6 in the last 5m:

.. code-block:: text

  avgi_over_time(ipmi_current_amperes[5m])

would return 4.

output example:

.. image:: /monitoring/capture/prometheus/query7.PNG
   :width: 80 %

sum, min, max
"""""""""""""

Self explanatory.
Works the same way as *avg*, and can be used with _over_time too.

more
""""

For *more* info, check:

.. seealso:: https://prometheus.io/docs/prometheus/latest/querying/functions/

It is now time to understand how alerts work in Prometheus.

Alerts
------

Alerts are located in the /etc/prometheus/alerts/ directory.

An example of alert:

.. code-block:: yaml

  groups:
  - name: Alerts for nodes
    rules:
    - alert: high_RAM_ Usage
      expr: (1 - (node_memory_MemAvailable_bytes{job=~".*.R.*"} / (node_memory_MemTotal_bytes{job=~".*.R.*"})))* 100 > 90
      for: 1m
      labels:
        severity: warning
      annotations:
        summary: " (instance {{ $labels.instance }})"
        description: "memory usage greater than 90%  \n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"

This alert will be seen as *pending* by Prometheus when the condition in
**expr:** is verified, in this case, when the percentage of used RAM is greater
than 90%.
It will seen as *firing* when the condition is met for X minutes, hours, or
days, X being in the **for** field.
It will be fired with an extra label called severity, which is set to *warning*
in this case.
The annotations section is here to set a summary and description of the alert.
You can access the variables of the metric by using de global variables
{{ $value }} or {{ $labels }}.

Tip: if you need a same alert to fire a warning after a t_1 desired time, and
then fire a critical after a longer t_2 time, duplicate the alert, with the
exact same name and arguments, changing only **for** and **severity**. The
Alertmanager configuration is made to handle these case: when same name,
a critical alert will overlap a warning alert.

Alertmanager
^^^^^^^^^^^^

Alertmanager is an additional tool for Prometheus, used to manage alerts.

**Alertmanager DO NOT evaluate alerts**, this is Prometheus task. Alertmanager
is a tool to manage alerts already fired by Prometheus.

By default, it's located under the management node's ip address, port 9093.
Configuration file of Alertmanager is under /etc/alertmanager/alertmanager.yml.

By default it looks like this:

.. code-block:: yaml

  global:
    smtp_smarthost: 'localhost:25'
    smtp_from: 'alertmanager@your_domain'
    smtp_require_tls: false

  route:
    group_by: ['alertname', 'job']
    group_wait: 1m
    group_interval: 10m
    repeat_interval: 3h
    receiver: sys-admin-team

  receivers:
    - name: 'sys-admin-team'
      email_configs:
        - to: 'sys-admin-team@site.com'

  inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']

You can find more about it here:

.. seealso:: https://prometheus.io/docs/alerting/latest/configuration/

And here are examples of some alerts:

.. seealso:: https://awesome-prometheus-alerts.grep.to/rules.html
