===============
Example cluster
===============

The rest of this documentation explains each concept (networks, groups, roles, deployment) on its
own. In this section, we do something different: we build together one complete, realistic cluster,
from an empty inventory to a first Slurm job, pointing to the detailed pages along the way rather
than re-explaining every variable.

Our example cluster has 9 hosts on 3 networks: a management server, a login node that is also the
gateway to the outside world, an NFS storage server, 4 CPU compute workers and 4 GPU compute
workers. We build it in two stages, so each one stays focused and easy to follow:

#. **The core cluster**: networks, operating system deployment over PXE, and base configuration.
#. **Extensions**: shared storage, a standard user, and the Slurm job scheduler.

Take your time, and enjoy the ride!

.. toctree::
   :maxdepth: 1

   example_cluster/overview
   example_cluster/bootstrap_and_inventory
   example_cluster/deployment
   example_cluster/extensions
   example_cluster/slurm_job
