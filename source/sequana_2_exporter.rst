Sequana_2_exporter
==================

The sequana_2_exporter is an exporter made with a python script, that uses PMSM. It is used in order to get general info about the sequanas.

By default, the sequana_2_exporter runs under the port 9765.

To access the metrics, either do::
  
  curl http://172.16.0.2:9765/metrics

or access it directly in a browser. Hower, using curl can be handy, because you can grep the output, and do other nice things with it.

You should get something like this ::

  # HELP node_vmstat_pgpgin /proc/vmstat information field pgpgin.
  # TYPE node_vmstat_pgpgin untyped
  node_vmstat_pgpgin 2.25160698e+08
  # HELP node_vmstat_pgpgout /proc/vmstat information field pgpgout.
  # TYPE node_vmstat_pgpgout untyped
  node_vmstat_pgpgout 1.18421998e+09
  # HELP node_vmstat_pswpin /proc/vmstat information field pswpin.
  # TYPE node_vmstat_pswpin untyped
  node_vmstat_pswpin 47719
  # HELP node_vmstat_pswpout /proc/vmstat information field pswpout.
  # TYPE node_vmstat_pswpout untyped
  node_vmstat_pswpout 532036
  # HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
  # TYPE process_cpu_seconds_total counter
  process_cpu_seconds_total 20272.88
  # HELP process_max_fds Maximum number of open file descriptors.
  # TYPE process_max_fds gauge
  process_max_fds 1024


you can see more by looking at the local metrics.


Alerts
^^^^^^

All the alerts for the node_exporter are stored under /etc/prometheus/alerts/sequana_2_exporter.yml

Some of them include :




 






 
