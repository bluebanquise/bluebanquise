Node_exporter
=============

The node_exporter is an official exporter from prometheus, and can be found here: https://github.com/prometheus/node_exporter

By default, the node_exporter runs under the port 9100.

To access the metrics, either do::
  
  curl http://172.16.0.2:9100/metrics

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


There are a lot of information given by node_exporter. It is a very heavy exporter, so that is why it is not running on the compute nodes. 

Some of the information given are the following:

•       Cpu core throttle
•       Cpu max,min,scaled frequency
•       Cpu time spent in each mode
•       Discards total time
•       Disk information (discard time,discarded sectors,discards completed, discards merged,disk io, disk io time, disk io time weighted seconds, disk read bytes, disk read time,…)
•       Filesystem (avail bytes, errors, mount points,etc…)
•       Temperature sensors values
•       Infiniband
•       Memory usage, etc…
•       Network( mtu bytes, protocols, received bytes, etc…)
•       Nfs requests
•       Scrape
•       Etc…

you can see more by looking at the local metrics.


Alerts
^^^^^^

All the alerts for the node_exporter are stored under /etc/prometheus/alerts/node.yml

Some of them include :

* High RAM usage 
* High CPU usage
* High mount volume
* Host out of inodes
* Unusual disk write latency
* etc...

Start service
^^^^^^^^^^^^^

To start the service, simply run ::

  systemctl start node_exporter

.. note:: all exporter services are under the /etc/systemd/system directory, and most binaries are under the /usr/local/bin directory

Dashboard
^^^^^^^^^

Grafana open source dashboard:

•       General info (structure, release, system, version,domain name)
•       CPU Busy
•       Used RAM, Used Max Mount, CPU IO wait, CPU Cores, etc..
•       Mounts (Available, used, etc...)
•       System load
•       CPU Basic

To access the dashboard: access the isma, port 3000::

  172.16.0.2:3000 

you can do some "port forwarding":: 
  
  ssh root@10.106.60.78 -L 82:172.16.0.2:3000




 
