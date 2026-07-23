===============
Example cluster
===============

The rest of this documentation explains each concept - networks, groups, roles, deployment - on
its own. This section instead builds one complete, realistic cluster end to end, referencing
back to those sections at each step instead of re-explaining every variable from scratch.

The example cluster has 9 hosts across 3 networks: a management server, a login/gateway node, an
NFS storage server, 4 CPU compute workers and 4 GPU compute workers. It is deployed in two
stages: the core cluster first (networking, PXE provisioning, base configuration), then optional
extensions on top (shared storage, a standard user, Slurm) - so that each stage stays focused
and easy to follow.

.. toctree::
   :maxdepth: 1

   example_cluster/overview
   example_cluster/bootstrap_and_inventory
   example_cluster/deployment
   example_cluster/extensions
   example_cluster/slurm_job
