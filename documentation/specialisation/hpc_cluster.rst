===========
HPC cluster
===========

High Performance Computing clusters are where BlueBanquise was born, and they remain one of its
favorite playgrounds.

On top of the general configuration, an HPC cluster usually needs:

* A fast interconnect, like InfiniBand, to let computations spread over many hosts talk to each
  other with very low latency (``interconnect`` role).
* A job scheduler, to share compute hosts fairly between users: Slurm (``slurm`` role).
* Containers designed for HPC, so users can bring their own software environment: Singularity
  (``singularity`` role).

Some useful companions are documented in :doc:`../configuration/system`: ``lmod`` for environment
modules, ``nhc`` to check hosts health before they run jobs, and ``gpu`` for GPU drivers. If your
cluster has Nvidia GPUs, :doc:`../resources/nvidia` gathers all the steps in one place.

Here is the detailed configuration of the roles dedicated to HPC clusters.

.. toctree::
   :maxdepth: 1
   :caption: HPC cluster dedicated roles:

   hpc_cluster/interconnect
   hpc_cluster/slurm
   hpc_cluster/singularity
