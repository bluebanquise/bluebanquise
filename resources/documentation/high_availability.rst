=================
High Availability
=================

In production environment, high availability is often needed to ensure
continuous cluster operations.

To achieve that, one of the possible solution is to setup an Active-Passive
HA (high availability) cluster. The BlueBanquise stack COMMUNITY
**high_availability** role can setup a Corosync - Pacemaker cluster.

Services then run as "resources" in that cluster, and migrate from one management
server to another. If one the management servers pool member crash, resources
running on it just migrate to another management to ensure continuous production.

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> schema

It is assumed in the following part that your hardware is composed of multiple
management nodes and a storage ARRAY shared by all management.
Some resources need to store data (database, state, etc.) and so need a shared
storage space to recover when migrating from one management to another.

Prepare HA
==========

First step is to follow standard process, to deploy an isolated management node.
