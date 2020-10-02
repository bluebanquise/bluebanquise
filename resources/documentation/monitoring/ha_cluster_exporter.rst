Ha_cluster_exporter
===================

The ha_cluster_exporter is an open source exporter, and can be found here:
https://github.com/ClusterLabs/ha_cluster_exporter

By default, the ha_cluster_exorter runs under the port 9664.

To access the metrics, either do:

.. code-block:: text

  curl http://localhost:9664/metrics

Or access it directly in a browser. However, using curl can be handy, because
you can grep the output, and do other nice things with it.

You should get something like this:

.. code-block:: text

  # HELP ha_cluster_corosync_member_votes How many votes each member node has contributed with to the current quorum
  # TYPE ha_cluster_corosync_member_votes gauge
  ha_cluster_corosync_member_votes{local="true",node="mgmt1-2",node_id="1"} 1
  # HELP ha_cluster_corosync_quorate Whether or not the cluster is quorate
  # TYPE ha_cluster_corosync_quorate gauge
  ha_cluster_corosync_quorate 1
  # HELP ha_cluster_corosync_quorum_votes Cluster quorum votes; one line per type
  # TYPE ha_cluster_corosync_quorum_votes gauge
  ha_cluster_corosync_quorum_votes{type="expected_votes"} 2
  ha_cluster_corosync_quorum_votes{type="highest_expected"} 2
  ha_cluster_corosync_quorum_votes{type="quorum"} 1
  ha_cluster_corosync_quorum_votes{type="total_votes"} 1
  # HELP ha_cluster_corosync_ring_errors The total number of faulty corosync rings
  # TYPE ha_cluster_corosync_ring_errors gauge
  ha_cluster_corosync_ring_errors 0
  # HELP ha_cluster_pacemaker_config_last_change The timestamp of the last change of the cluster configuration
  # TYPE ha_cluster_pacemaker_config_last_change counter
  ha_cluster_pacemaker_config_last_change 1.593617322e+09
  # HELP ha_cluster_pacemaker_fail_count The Fail count number per node and resource id
  # TYPE ha_cluster_pacemaker_fail_count gauge
  ha_cluster_pacemaker_fail_count{node="mgmt1-2",resource="fs-conman"} 0
  ha_cluster_pacemaker_fail_count{node="mgmt1-2",resource="fs-data-http"} 0
  ha_cluster_pacemaker_fail_count{node="mgmt1-2",resource="fs-data-pgsql"} 0
  ha_cluster_pacemaker_fail_count{node="mgmt1-2",resource="fs-grafana-database"} 0
  ha_cluster_pacemaker_fail_count{node="mgmt1-2",resource="fs-prometheus-database"} 0
  ha_cluster_pacemaker_fail_count{node="mgmt1-2",resource="fs-rsyslog"} 0


Some of the information given are the following:

* Pacemaker fails
* Pacemaker constraints
* Pacemaker migration threshold
* Pacemaker node status
* Status of Pacemaker resources
* Pacemaker stonith (enabled or not)

You can see more by looking at the local metrics, and by checking the github
page.

Alerts
------

All the alerts for the node_exporter are stored under
/etc/prometheus/alerts/ha.yml

Some of them include :

* Not quorate
* Long standby
* Failed services
* Failed resources
* Failcount>migration threshold
* Stonith not enabled
* Negative location constraints

Start service
-------------

To start the service, simply run:

.. code-block:: text

  systemctl start ha_cluster_exporter

.. note::
  All exporter services are under the /etc/systemd/system directory,
  and most binaries are under the /usr/local/bin directory.

Dashboards
----------

there are several dashboards for the ha.

Here is what they show:

* Pacemaker nodes (Total  nodes, online nodes, expected up, DC)
* Quorum votes (expected votes, highest expected vote, total votes)
* Is quorate?
* Ring errors
* Last pacemaker change
* Resources (names, agent,status,…)
* Alerts (name, severity, instance…)
* Etc...
