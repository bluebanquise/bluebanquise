Slurm
-----

Description
^^^^^^^^^^^

This role provides slurm configuration for server, client and login nodes.

Instructions
^^^^^^^^^^^^

**IMPORTANT**: first thing to do is to generate a new munge key file. To do so,
go into files folder of the role and generate a new munge.key file using:

.. code-block:: text

  dd if=/dev/urandom bs=1 count=1024 > munge.key

We do not provide default munge key file, as it is considered a security risk.

Then, in the inventory addon folder (inventory/group_vars/all/addons) that should
be created if not exist, add a slurm.yml file with the following content, tuned
according to your needs:

.. code-block:: yaml

  slurm:
    slurm_packaging: after_17 # Can be before_17 or after_17. If using BlueBanquise packages, use after_17. For OpenHPC 1.3, use before_17.
    cluster_name: bluebanquise
    control_machine: management1
    MpiDefault: pmi2 # Optional
    nodes_equipment_groups:
      - equipment_typeC

To use this role for all 3 types of nodes, simply add a vars in the playbook
when loading the role. Extra vars is **slurm_profile**.

For a controller (server), use:

.. code-block:: yaml

  - role: slurm
    tags: slurm
    vars:
      slurm_profile: controller

For a compute node (client), use:

.. code-block:: yaml

  - role: slurm
    tags: slurm
    vars:
      slurm_profile: node

And for a login (passive client), use:

.. code-block:: yaml

  - role: slurm
    tags: slurm
    vars:
      slurm_profile: passive

To be done
^^^^^^^^^^

* slurmdbd + mariadb
* static file

Changelog
^^^^^^^^^

* 1.0.2: Update role, remove munge key. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
