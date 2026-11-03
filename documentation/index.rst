BlueBanquise Documentation
==========================

.. image:: images/multiple_icebergs.svg
   :align: center

Welcome to the BlueBanquise documentation!

These pages explain how to deploy, configure and take care of clusters with the BlueBanquise
unified stack, from a few workstations to very large HPC clusters. Whether you are discovering the
stack or looking for a specific setting, we hope you will find your way easily. New here? Start with
the Introduction, then follow the Walkthrough: it builds a complete cluster, step by step.

If something is unclear, missing or wrong, please
`tell us <https://github.com/bluebanquise/bluebanquise/issues>`_: every feedback helps make this
documentation better for everyone.

.. image:: images/Cc-by-nc-sa_icon.svg
   :align: center

..
   Reminder for the maintainers (this comment is not rendered): schemas still to draw.
   Each one is described in place, in its page, by a [SCHEMA: <name>] block. Once a schema is
   drawn, replace its block by an image, and remove it from this list.

   * bluebanquise-stack-overview (introduction/what_is_bluebanquise.rst): inventory, collection,
     roles families and cluster hosts, as layers.
   * example-cluster-topology (walkthrough/example_cluster/overview.rst): the 3 networks and 9 hosts
     of the walkthrough, with the routes to the internet.
   * example-cluster-groups-matrix (walkthrough/example_cluster/bootstrap_and_inventory.rst): hosts
     versus fn/hw/os groups grid.
   * example-cluster-firewall-zones (walkthrough/example_cluster/bootstrap_and_inventory.rst):
     topology colored by firewall zone, gateway policy on login, rich rule on storage.
   * inventory-precedence (configuration/inventories.rst): inventory folders and variables
     precedence podium.
   * deployment-strategy (deployment/strategy.rst): timeline of the 8 deployment steps.
   * pxe-boot-chain (deployment/provision_os.rst): iPXE chain between a host and the management
     host, up to the stage report switching the host to disk. Could also replace the PNG slides.
   * operations-tools (operations/operations.rst): the management host and its day to day tools.
   * nvidia-gpu-stack (resources/nvidia.rst): repositories, driver/CUDA and Slurm gres layers on a
     GPU host.
   * icebergs-hierarchy (scalability/scalability.rst): top iceberg and lower icebergs, with
     services chaining. Existing multiple_icebergs*.svg images (images/) may be reused.
   * herds-and-ha (scalability/scalability.rst): flat network, management hosts sharing virtual
     IPs, herds of hosts.
   * ha-building-blocks (scalability/high_availability.rst): keepalived, haproxy, DRBD and
     Pacemaker/Corosync on three management hosts.

------------

.. toctree::
   :maxdepth: 2
   :caption: Introduction:
   :numbered:

   introduction/what_is_bluebanquise
   introduction/installation
   introduction/vocabulary

.. toctree::
   :maxdepth: 1
   :caption: Walkthrough:
   :numbered:

   walkthrough/example_cluster

.. toctree::
   :maxdepth: 2
   :caption: General configuration:
   :numbered:
   :titlesonly:

   configuration/inventories
   configuration/general_settings
   configuration/networks
   configuration/hosts
   configuration/groups
   configuration/os_settings
   configuration/hardware_settings
   configuration/services
   configuration/system
   configuration/storage

.. toctree::
   :maxdepth: 1
   :caption: Specialisation configuration:
   :numbered:

   specialisation/hpc_cluster

.. toctree::
   :maxdepth: 1
   :caption: Deployment:
   :numbered:

   deployment/strategy
   deployment/provision_os
   deployment/apply_configuration

.. toctree::
   :maxdepth: 1
   :caption: Operations:
   :numbered:

   operations/operations

.. toctree::
   :maxdepth: 1
   :caption: Scalability and high availability:
   :numbered:

   scalability/scalability
   scalability/high_availability

.. toctree::
   :maxdepth: 1
   :caption: Resources:
   :numbered:

   resources/nvidia
   resources/mellanox
