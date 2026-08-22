================
Run a Slurm job
================

With :doc:`extensions` applied, the cluster has a standard user (``keats``) and a working Slurm
controller. This page submits a first job as that user, from the login node - the same way a
real cluster user would.

Connect as keats
=================

From your workstation, or from mgt1:

.. code-block:: bash

  ssh keats@login

Sanity check the cluster
==========================

.. code-block:: bash

  sinfo

.. code-block:: text

  PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
  cpu*         up   infinite      4   idle c[001-004]
  gpu          up   infinite      4   idle g[001-004]

.. code-block:: bash

  squeue

should return an empty queue (no jobs running yet).

Submit a trivial job
======================

Run a command across the whole ``cpu`` partition:

.. code-block:: bash

  srun --partition=cpu --nodes=4 hostname

.. code-block:: text

  c001
  c002
  c003
  c004

And on the ``gpu`` partition:

.. code-block:: bash

  srun --partition=gpu --nodes=4 hostname

.. code-block:: text

  g001
  g002
  g003
  g004

Submit a batch job
====================

For anything longer than a one-liner, use ``sbatch``. Create ``~/hello_cluster.sh``:

.. code-block:: bash

  #!/bin/bash
  #SBATCH --job-name=hello_cluster
  #SBATCH --partition=cpu
  #SBATCH --nodes=1
  #SBATCH --output=%x-%j.out

  echo "Hello from $(hostname), running as $(whoami)"
  df -h /home /software

Submit it and watch it run:

.. code-block:: bash

  sbatch ~/hello_cluster.sh
  squeue
  cat hello_cluster-<jobid>.out

The output should show the job landed on one of ``c001``-``c004``, running as ``keats``, with
both ``/home`` and ``/software`` visible - confirming the compute worker, the Slurm scheduler,
and the NFS share added in :doc:`extensions` are all working together.

-----

That completes the walkthrough: a 9-host, 3-network cluster taken from a bare RHEL 10 management
server to a working Slurm job submitted by a standard user. From here, the rest of this
documentation covers every role and setting used along the way in full detail.
