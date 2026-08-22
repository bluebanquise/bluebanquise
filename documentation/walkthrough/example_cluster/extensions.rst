==========
Extensions
==========

The core cluster from :doc:`deployment` is installed, networked and reachable, but has no
shared storage, no non-admin user, and no job scheduler. Each of the three sections below adds
one optional capability, the same way every time: extend the inventory, add the relevant role to
the relevant playbook(s), re-run, verify. Do them in order - Slurm's compute nodes and login node
both expect ``keats`` to exist, and ``keats``'s home directory is meant to live on the NFS share.

Add NFS storage
================

Update the inventory
---------------------

``group_vars/all/nfs.yml``:

.. code-block:: yaml

  nfs_shares:
    - export: /home
      server: storage
      mount: /home
      clients_groups:
        - fn_login
        - fn_compute
        - fn_compute_gpu
      network: net-admin
      export_options: rw,sync
      mount_options: rw,nfsvers=4.2,bg
    - export: /software
      server: storage
      mount: /software
      clients_groups:
        - fn_login
        - fn_compute
        - fn_compute_gpu
      network: net-admin
      export_options: ro,sync
      mount_options: ro,nfsvers=4.2,bg

``/home`` is read-write for login and every compute worker; ``/software`` is read-only. See the
:doc:`nfs <../../configuration/storage/nfs>` role section of this documentation for the full
parameter list.

Update the playbooks
---------------------

Add the ``nfs`` role to ``playbooks/storage.yml``, as a server:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.nfs
        tags: nfs
        vars:
          nfs_profile:
            - server

And to ``playbooks/login.yml``, ``playbooks/computes.yml`` and ``playbooks/computes_gpu.yml``,
as a client - add it **before** the ``ssh_remote_keys``/``time`` roles already there is fine,
but it must come before the ``users`` role you will add in the next section, so that ``/home``
is already mounted before any home directory gets created on it:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.nfs
        tags: nfs
        vars:
          nfs_profile:
            - client

Re-run and verify
------------------

.. code-block:: bash

  ansible-playbook playbooks/storage.yml -i inventory --become --tags nfs
  ansible-playbook playbooks/login.yml -i inventory --become --tags nfs
  ansible-playbook playbooks/computes.yml -i inventory --become --tags nfs
  ansible-playbook playbooks/computes_gpu.yml -i inventory --become --tags nfs

.. code-block:: bash

  ssh login df -h /home /software

should show both mounted from ``storage``.

Add standard users
====================

Update the inventory
---------------------

``group_vars/all/users.yml``:

.. code-block:: yaml

  users:
    - name: keats
      uid: 2001
      gid: 2001
      home: /home/keats
      shell: /bin/bash
      comment: Standard cluster user
      password: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
      ssh_authorized_keys:
        - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF0iWc1oG+JA6FetOh6Qtqzqedy+n3In7MXRaT3USxtE keats@example.local

.. warning::

  Replace both the password hash and the SSH key with real ones of your own - these are
  placeholders. See the :doc:`users <../../configuration/system/users>` role section of this
  documentation for the full list of per-user options, and how to generate a password hash.

Update the playbooks
---------------------

Add the ``users`` role to ``playbooks/login.yml``, ``playbooks/computes.yml`` and
``playbooks/computes_gpu.yml`` - not ``storage.yml`` or ``management.yml``, since ``keats`` only
needs to log in on login and run jobs on the compute workers:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.users
        tags: users

Re-run and verify
------------------

.. code-block:: bash

  ansible-playbook playbooks/login.yml -i inventory --become --tags users
  ansible-playbook playbooks/computes.yml -i inventory --become --tags users
  ansible-playbook playbooks/computes_gpu.yml -i inventory --become --tags users

.. code-block:: bash

  ssh login id keats

should resolve, and ``/home/keats`` should exist on the NFS share added above.

Add Slurm
==========

Generate a munge key
----------------------

Slurm requires a shared munge key across the whole cluster. Generate one on mgt1 (needs the
``munge`` package installed) and base64-encode it:

.. code-block:: bash

  mungekey -c -k munge.key
  base64 -w 0 munge.key

Copy the resulting string - you will paste it into the inventory below. If ``inventory`` or
``playbooks/`` are stored in a version-controlled repository, consider encrypting this value
with `Ansible Vault <https://docs.ansible.com/ansible/latest/vault_guide/index.html>`_.

Update the inventory
---------------------

``group_vars/all/slurm.yml``:

.. code-block:: yaml

  slurm_cluster_name: example_cluster
  slurm_controller_hostname: mgt1
  slurm_munge_key_b64: <paste-your-base64-encoded-munge-key-here>
  slurm_partitions_list:
    - computes_groups:
        - fn_compute
      partition_name: cpu
      partition_configuration:
        State: UP
        Default: "YES"
    - computes_groups:
        - fn_compute_gpu
      partition_name: gpu
      partition_configuration:
        State: UP
        Default: "NO"

Two partitions, ``cpu`` (the 4 ``fn_compute`` workers, default) and ``gpu`` (the 4
``fn_compute_gpu`` workers). See the :doc:`slurm <../../specialisation/hpc_cluster/slurm>` role
section of this documentation for accounting, GPU Gres, and pam_slurm_adoption, none of which
this walkthrough enables.

Update the playbooks
---------------------

Add the ``slurm`` role to ``playbooks/management.yml``, as the controller:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.slurm
        tags: slurm
        vars:
          slurm_profile: controller

To ``playbooks/login.yml``, as a submitter:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.slurm
        tags: slurm
        vars:
          slurm_profile: submitter

And to ``playbooks/computes.yml`` and ``playbooks/computes_gpu.yml``, as compute nodes:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.slurm
        tags: slurm
        vars:
          slurm_profile: compute

Re-run and verify
------------------

Controller first, so ``slurmctld`` is up before the computes try to register against it:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventory --become --tags slurm
  ansible-playbook playbooks/login.yml -i inventory --become --tags slurm
  ansible-playbook playbooks/computes.yml -i inventory --become --tags slurm
  ansible-playbook playbooks/computes_gpu.yml -i inventory --become --tags slurm

.. code-block:: bash

  ssh mgt1 sinfo

should list both the ``cpu`` and ``gpu`` partitions, each with its 4 nodes in ``idle`` state.
If a node shows ``down`` or ``unk``, give ``slurmd`` a minute to register, or check
``systemctl status slurmd`` on that node and ``systemctl status slurmctld`` on mgt1.

-----

The cluster now has shared storage, a standard user, and a job scheduler. Continue to
:doc:`slurm_job` to submit an actual job as ``keats``.
