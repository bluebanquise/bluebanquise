==========
Extensions
==========

Our core cluster is installed and reachable, but it has no shared storage, no user, and no job
scheduler yet. Let's add them, one at a time, always with the same recipe: extend the inventory,
add the role to the playbooks, run, and check.

Let's follow this order: users' homes live on the NFS share, and Slurm needs users to run jobs.

Add NFS storage
===============

Update the inventory
--------------------

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

``/home`` is writable by login and all compute workers, ``/software`` is read only. See the
:doc:`nfs <../../configuration/storage/nfs>` role documentation for all parameters.

Update the playbooks
--------------------

In ``playbooks/storage.yml``, the ``nfs`` role, as a server:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.nfs
        tags: nfs
        vars:
          nfs_profile:
            - server

In ``playbooks/login.yml``, ``playbooks/computes.yml`` and ``playbooks/computes_gpu.yml``, as a
client:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.nfs
        tags: nfs
        vars:
          nfs_profile:
            - client

Run and check
-------------

The server first, then its clients:

.. code-block:: bash

  ansible-playbook playbooks/storage.yml -i inventories/example_cluster -b --tags nfs
  ansible-playbook playbooks/login.yml -i inventories/example_cluster -b --tags nfs
  ansible-playbook playbooks/computes.yml -i inventories/example_cluster -b --tags nfs
  ansible-playbook playbooks/computes_gpu.yml -i inventories/example_cluster -b --tags nfs

.. code-block:: bash

  ssh login df -h /home /software

Both should be mounted from ``storage``.

Add a user
==========

Update the inventory
--------------------

Let's create our first user, keats. ``group_vars/all/users.yml``:

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

  Replace the password hash and the SSH key with real ones: these are placeholders. See the
  :doc:`users <../../configuration/system/users>` role documentation for all options.

Update the playbooks
--------------------

keats' home lives on the NFS share. NFS exports protect files from the root user of clients
(``root_squash``, the default): root on login cannot write in keats' home, and so cannot create it
nor write its SSH keys. So we create the user on storage first, where ``/home`` is a local folder,
and on clients we only declare the user, without touching its home.

In ``playbooks/storage.yml``:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.users
        tags: users

In ``playbooks/login.yml``, ``playbooks/computes.yml`` and ``playbooks/computes_gpu.yml``, after
the ``nfs`` role:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.users
        tags: users
        vars:
          users_enable_ssh_authorized_keys: false

Run and check
-------------

.. code-block:: bash

  ansible-playbook playbooks/storage.yml -i inventories/example_cluster -b --tags users
  ansible-playbook playbooks/login.yml -i inventories/example_cluster -b --tags users
  ansible-playbook playbooks/computes.yml -i inventories/example_cluster -b --tags users
  ansible-playbook playbooks/computes_gpu.yml -i inventories/example_cluster -b --tags users

.. code-block:: bash

  ssh login id keats
  ssh login ls -la /home/keats

keats exists, with the same uid everywhere, and its home is on the share.

Add Slurm
=========

Generate a munge key
--------------------

All Slurm hosts share a secret key, used by munge to authenticate each other: 1024 random bytes.
Let's generate one on mgt1, and encode it in base64:

.. code-block:: bash

  dd if=/dev/urandom of=munge.key bs=1 count=1024
  base64 -w 0 munge.key
  rm munge.key

Copy the resulting string, we paste it in the inventory just below. As it is a secret, consider
encrypting it with `Ansible Vault <https://docs.ansible.com/ansible/latest/vault_guide/index.html>`_
if the inventory is stored in git.

Update the inventory
--------------------

``group_vars/all/slurm.yml``:

.. code-block:: yaml

  slurm_cluster_name: example_cluster
  slurm_controller_hostname: mgt1
  slurm_munge_key_b64: <paste-your-base64-encoded-munge-key-here>
  slurm_selecttype: "select/cons_tres"
  slurm_grestypes: gpu
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

Two partitions: ``cpu``, with the 4 CPU workers (the default one), and ``gpu``, with the 4 GPU
workers. ``slurm_selecttype`` and ``slurm_grestypes`` let jobs request GPUs.

Slurm also needs to know how many GPUs each GPU worker offers. Let's add one line to the
``hw_specs`` of ``group_vars/hw_gpu_worker/settings.yml``:

.. code-block:: yaml

  hw_specs:
    slurm_extra_nodes_parameters: "Gres=gpu:4"
    cpu:
      ...

See the :doc:`slurm <../../specialisation/hpc_cluster/slurm>` role documentation for accounting and
other features, and :doc:`../../resources/nvidia` for GPUs.

Update the playbooks
--------------------

In ``playbooks/management.yml``, the controller:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.slurm
        tags: slurm
        vars:
          slurm_profile: controller

In ``playbooks/login.yml``, the submitter (users submit jobs from there):

.. code-block:: yaml

      - role: bluebanquise.infrastructure.slurm
        tags: slurm
        vars:
          slurm_profile: submitter

In ``playbooks/computes.yml`` and ``playbooks/computes_gpu.yml``, compute nodes:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.slurm
        tags: slurm
        vars:
          slurm_profile: compute

Run and check
-------------

The controller first, so it is ready when compute nodes register:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventories/example_cluster -b --tags slurm
  ansible-playbook playbooks/login.yml -i inventories/example_cluster -b --tags slurm
  ansible-playbook playbooks/computes.yml -i inventories/example_cluster -b --tags slurm
  ansible-playbook playbooks/computes_gpu.yml -i inventories/example_cluster -b --tags slurm

.. code-block:: bash

  sinfo

Both partitions, ``cpu`` and ``gpu``, should be listed, each with its 4 nodes ``idle``. If a node is
``down`` or ``unk``, give ``slurmd`` a minute to register, then check ``systemctl status slurmd`` on
that node, and ``systemctl status slurmctld`` on mgt1.

-----

Our cluster now has shared storage, a user, and a job scheduler. Time to run a first job, in
:doc:`slurm_job`!
