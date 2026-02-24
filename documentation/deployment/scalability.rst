===========
Scalability
===========

At some point, you might want to increase the size of the cluster or achieve high availability (also refered as HA), or just allow some kind of load balancing.

I propose a strategy based on my personal experience, in hope it might suits your needs.

The concept is based on the Corrosync / Pacemaker couple, along few other tools.

Architecture:

* X worker nodes, for example 2000.

These X nodes are split into "herds", which are logical groups of nodes that a single management node is able to handle. 500 or 600 seems a reasonable size for an herd.

* N management nodes, N being equal to the number "herds". In our example, 2000 / 500 = 4, so 4 management nodes.

* 1 NFS storage bay, with hardware redundancy. This component is critical and should be chosen with care. It will be mounted on each management node.

  .. note::
    It is possible to get ride of the NFS storage bay, using replication tools like DRBD or any other parallel FS.
