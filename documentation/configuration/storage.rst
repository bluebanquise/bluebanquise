=======
Storage
=======

Sooner or later, every cluster needs to share data between its hosts: home directories that follow
users everywhere, software installed once and used by all, datasets that computations read and
results they write.

The stack offers a few ways to do so, from the simple and reliable NFS, perfect for most clusters,
to parallel file systems like Lustre, designed for very large clusters and intensive I/O.

Local storage (partitions, LVM volumes, file systems and mount points of each host) is handled by the
storage section of the ``local_configuration`` role (see :doc:`system`).

.. note::

  Not sure where to start? NFS is a great first choice. It is simple to set up, easy to debug, and
  serves comfortably clusters of a few hundred hosts.

Here is the detailed configuration available for each storage solution of the stack.

.. toctree::
   :maxdepth: 1
   :caption: Storage:

   storage/nfs
   storage/lustre_client
