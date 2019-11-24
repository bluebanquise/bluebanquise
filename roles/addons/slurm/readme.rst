Slurm
-----

Description
^^^^^^^^^^^

This role provides slurm configuration for server, client and login nodes.

Instructions
^^^^^^^^^^^^

To use this role for all 3 types of nodes, simply add a vars in the playbook when loading the role. Extra vers is **slurm_profile**.

For a controler (server), use:

.. code-block:: yaml

  - role: HPC_slurm
    tags: HPC_slurm
    vars:
      slurm_profile: controler

For a compute node (client), use:

.. code-block:: yaml

  - role: HPC_slurm
    tags: HPC_slurm
    vars:
      slurm_profile: node

And for a login (passive client), use:

.. code-block:: yaml

  - role: HPC_slurm
    tags: HPC_slurm
    vars:
      slurm_profile: passive

To be done
^^^^^^^^^^

* slurmdbd + mariadb
* static file

Changelog
^^^^^^^^^

* 1.0.1: Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
