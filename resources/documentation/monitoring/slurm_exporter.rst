Slurm_exporter
==============

The slurm_exporter is an open source exporter for Prometheus, and can be found
here: https://github.com/vpenso/prometheus-slurm-exporter

By default, the slurm_exorter runs under the port 9817.

To access the metrics, either do::

  curl http://localhost:9817/metrics

or access it directly in a browser. However, using curl can be handy, because
you can grep the output, and do other nice things with it.

You should get something like this:

.. code-block:: text

  # TYPE promhttp_metric_handler_requests_total counter
  promhttp_metric_handler_requests_total{code="200"} 3029
  promhttp_metric_handler_requests_total{code="500"} 0
  promhttp_metric_handler_requests_total{code="503"} 0
  # HELP slurm_cpus_alloc Allocated CPUs
  # TYPE slurm_cpus_alloc gauge
  slurm_cpus_alloc 65792
  # HELP slurm_cpus_idle Idle CPUs
  # TYPE slurm_cpus_idle gauge
  slurm_cpus_idle 0
  # HELP slurm_cpus_other Mix CPUs
  # TYPE slurm_cpus_other gauge
  slurm_cpus_other 15616
  # HELP slurm_cpus_total Total CPUs
  # TYPE slurm_cpus_total gauge
  slurm_cpus_total 81408
  # HELP slurm_nodes_alloc Allocated nodes
  # TYPE slurm_nodes_alloc gauge
  slurm_nodes_alloc 257
  # HELP slurm_nodes_comp Completing nodes
  # TYPE slurm_nodes_comp gauge
  slurm_nodes_comp 0
  # HELP slurm_nodes_down Down nodes
  # TYPE slurm_nodes_down gauge
  slurm_nodes_down 28


Metrics
-------

Here is an extract from the github page:

.. code-block:: text

  ## Exported Metrics

  ### State of the CPUs

  * **Allocated**: CPUs which have been allocated to a job.
  * **Idle**: CPUs not allocated to a job and thus available for use.
  * **Other**: CPUs which are unavailable for use at the moment.
  * **Total**: total number of CPUs.

  - [Information extracted from the SLURM **sinfo** command](https://slurm.schedmd.com/sinfo.html)
  - [Slurm CPU Management User and Administrator Guide](https://slurm.schedmd.com/cpu_management.html)

  ### State of the Nodes

  * **Allocated**: nodes which has been allocated to one or more jobs.
  * **Completing**: all jobs associated with these nodes are in the process of being completed.
  * **Down**: nodes which are unavailable for use.
  * **Drain**: with this metric two different states are accounted for:
    - nodes in ``drained`` state (marked unavailable for use per system administrator request)
    - nodes in ``draining`` state (currently executing jobs but which will not be allocated for new ones).
  * **Fail**: these nodes are expected to fail soon and are unavailable for use per system administrator request.
  * **Error**: nodes which are currently in an error state and not capable of running any jobs.
  * **Idle**: nodes not allocated to any jobs and thus available for use.
  * **Maint**: nodes which are currently marked with the __maintenance__ flag.
  * **Mixed**: nodes which have some of their CPUs ALLOCATED while others are IDLE.
  * **Resv**: these nodes are in an advanced reservation and not generally available.

  [Information extracted from the SLURM **sinfo** command](https://slurm.schedmd.com/sinfo.html)

  ### Status of the Jobs

  * **PENDING**: Jobs awaiting for resource allocation.
  * **PENDING_DEPENDENCY**: Jobs awaiting because of a unexecuted job dependency.
  * **RUNNING**: Jobs currently allocated.
  * **SUSPENDED**: Job has an allocation but execution has been suspended and CPUs have been released for other jobs.
  * **CANCELLED**: Jobs which were explicitly cancelled by the user or system administrator.
  * **COMPLETING**: Jobs which are in the process of being completed.
  * **COMPLETED**: Jobs have terminated all processes on all nodes with an exit code of zero.
  * **CONFIGURING**: Jobs have been allocated resources, but are waiting for them to become ready for use.
  * **FAILED**: Jobs terminated with a non-zero exit code or other failure condition.
  * **TIMEOUT**: Jobs terminated upon reaching their time limit.
  * **PREEMPTED**: Jobs terminated due to preemption.
  * **NODE_FAIL**: Jobs terminated due to failure of one or more allocated nodes.

  [Information extracted from the SLURM **squeue** command](https://slurm.schedmd.com/squeue.html)

  ### Scheduler Information

  * **Server Thread count**: The number of current active ``slurmctld`` threads.
  * **Queue size**: The length of the scheduler queue.
  * **Last cycle**: Time in microseconds for last scheduling cycle.
  * **Mean cycle**: Mean of scheduling cycles since last reset.
  * **Cycles per minute**: Counter of scheduling executions per minute.
  * **(Backfill) Last cycle**: Time in microseconds of last backfilling cycle.
  * **(Backfill) Mean cycle**: Mean of backfilling scheduling cycles in microseconds since last reset.
  * **(Backfill) Depth mean**: Mean of processed jobs during backfilling scheduling cycles since last reset.


You can see more by looking at the local metrics.

Start service
-------------

To start the service, simply run:

.. code-block:: text

  systemctl start slurm_exporter

.. note:: all exporter services are under the /etc/systemd/system directory, and most binaries are under the /usr/local/bin directory

Alerts
------

All the alerts for the slurm_exporter are stored under /etc/prometheus/alerts/

Some of them include :

* High RAM usage
* High CPU usage
* High mount volume
* Host out of inodes
* Unusual disk write latency
* etc...

Dashboard
---------

A dashboard is provided on the exporter github page.
