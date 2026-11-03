===============
Run a Slurm job
===============

Here we are: the cluster has a user, keats, and a working job scheduler. Let's submit a first job,
from the login node, just like a real user of the cluster would.

Connect as keats
================

From your workstation (through the ``datacenter`` network), or from mgt1:

.. code-block:: bash

  ssh keats@login

Look around
===========

.. code-block:: bash

  sinfo

.. code-block:: text

  PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
  cpu*         up   infinite      4   idle c[001-004]
  gpu          up   infinite      4   idle g[001-004]

.. code-block:: bash

  squeue

The queue is empty: no job is running yet.

A first job
===========

Let's run a command on the 4 nodes of the ``cpu`` partition:

.. code-block:: bash

  srun --partition=cpu --nodes=4 hostname

.. code-block:: text

  c001
  c002
  c003
  c004

And let's ask for 2 GPUs on a GPU worker:

.. code-block:: bash

  srun --partition=gpu --gres=gpu:2 nvidia-smi -L

Only the 2 GPUs allocated to the job are listed.

A batch job
===========

For anything longer than a single command, we use ``sbatch``. Create ``~/hello_cluster.sh``:

.. code-block:: bash

  #!/bin/bash
  #SBATCH --job-name=hello_cluster
  #SBATCH --partition=cpu
  #SBATCH --nodes=1
  #SBATCH --output=%x-%j.out

  echo "Hello from $(hostname), running as $(whoami)"
  df -h /home /software

Submit it, and watch it run:

.. code-block:: bash

  sbatch ~/hello_cluster.sh
  squeue
  cat hello_cluster-<jobid>.out

The output shows the job ran on one of the CPU workers, as keats, with ``/home`` and ``/software``
available: compute workers, Slurm, users and NFS all work together.

-----

Congratulations, you made it! We went from a single RHEL 10 management server to a 9 hosts, 3
networks cluster, running jobs for its users. Thank you for following along.

From here, the rest of this documentation describes every role and setting we used in full detail,
and many more: monitoring, logs, high availability, and so on. And :doc:`../../operations/operations`
gathers the tools to take care of the cluster day to day. Have fun with your cluster!
