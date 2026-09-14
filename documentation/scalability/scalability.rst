===========
Scalability
===========

BlueBanquise proposes 2 ways to scale clusters, depending of your target architecture.

Vertical scalability
====================

Vertical scalability uses the concept of "icebergs" in BlueBanquise.

The cluster is organized in a pyramidal shape. Instead of using a single flat network, cluster is physically separated into icebergs (also named islands)
which are autonomous small clusters: each iceberg possesses its own network subnet, its own set of management servers, etc.

.. note::
    All icebergs can still share a same interconnect or high speed network, only admininstration networks are separated in the icebergs concept.

Horizontal scalability
======================



