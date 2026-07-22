====================
Core: deployment
====================

With the inventory from :doc:`bootstrap_and_inventory` in place, this page deploys the core
cluster: configure mgt1, PXE-provision the other 8 hosts, then push their base configuration.
Still no NFS, users or Slurm at this point - that is :doc:`extensions`.

Deploy configuration on mgt1
=============================

Create ``playbooks/management.yml``:

.. code-block:: yaml

  ---
  - name: management playbook
    hosts: "fn_management"
    roles:
      - role: bluebanquise.infrastructure.hosts_file
        tags: hosts_file
      - role: bluebanquise.infrastructure.local_configuration
        tags: local_configuration
      - role: bluebanquise.infrastructure.repositories
        tags: repositories
      - role: bluebanquise.infrastructure.nic
        tags: nic
      - role: bluebanquise.infrastructure.dhcp_server
        tags: dhcp_server
      - role: bluebanquise.infrastructure.dns_client
        tags: dns_client
      - role: bluebanquise.infrastructure.dns_server
        tags: dns_server
      - role: bluebanquise.infrastructure.http_server
        tags: http_server
      - role: bluebanquise.infrastructure.pxe_stack
        tags: pxe_stack
      - role: bluebanquise.infrastructure.firewall
        tags: firewall
      - role: bluebanquise.infrastructure.ssh_client
        tags: ssh_client
      - role: bluebanquise.infrastructure.ssh_remote_keys
        tags: ssh_remote_keys
      - role: bluebanquise.infrastructure.time
        tags: time
        vars:
          time_profile: server

.. note::

  This uses ``local_configuration`` (which also sets the hostname) rather than the
  ``set_hostname`` role referenced by some older pages in this documentation - ``set_hostname``
  no longer exists as a standalone role, its behaviour was folded into ``local_configuration``.

Bring the network interfaces and repositories up first, so the rest of the run has a working
NIC and package access:

.. code-block:: bash

  cd /var/lib/bluebanquise
  ansible-playbook playbooks/management.yml -i inventory --become --limit mgt1 --tags nic,repositories

Check with ``ip a`` that ``eth1`` (net-admin, 10.10.0.1) and ``eth2`` (net-bmc, 10.11.0.1) are
up, then run the rest:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventory --become --limit mgt1

This is idempotent - re-running it only touches what has drifted. See
:doc:`../../deployment/apply_configuration` for more detail on tags and extra-vars.

Provision the other hosts via PXE
==================================

mgt1 now serves DHCP, DNS, and the PXE chain for the other 8 hosts. Before powering them on,
tell the ``bluebanquise-pxe-stack-daemon`` to deploy an OS on them next boot:

.. code-block:: bash

  sudo bluebanquise-bootset -n login,storage,c[001-004],g[001-004] -b osdeploy
  sudo bluebanquise-bootset -n login,storage,c[001-004],g[001-004] -s

The second command should report all 8 hosts scheduled for ``osdeploy``.

Power the 8 hosts on (directly, or over their BMC once you have out-of-band access set up) and
let them PXE boot. Each one gets an IP from DHCP, chains through iPXE to the
``bluebanquise-pxe-stack-daemon``, picks up its equipment profile (console, kernel parameters,
partitioning, ``os_admin_ssh_keys``, ...) and autoinstalls RHEL 10. Expect 5-20 minutes per host,
in parallel. See the ``pxe_stack`` role section of this documentation (and its iPXE chain
diagram) for the full boot sequence if you want to follow it step by step - the mechanism is
generic and does not need a cluster-specific diagram here.

Once a host finishes installing, it reboots to disk and should already accept SSH from mgt1
using the key set in ``os_admin_ssh_keys`` - no manual key exchange needed, it was baked in at
install time.

.. code-block:: bash

  sudo bluebanquise-bootset -n login,storage,c[001-004],g[001-004] -s

should progress from ``scheduled`` to ``started`` to ``completed`` for each host as it deploys.

Push base configuration on the other hosts
=============================================

Create ``playbooks/login.yml``:

.. code-block:: yaml

  ---
  - name: login playbook
    hosts: "fn_login"
    roles:
      - role: bluebanquise.infrastructure.hosts_file
        tags: hosts_file
      - role: bluebanquise.infrastructure.local_configuration
        tags: local_configuration
      - role: bluebanquise.infrastructure.repositories
        tags: repositories
      - role: bluebanquise.infrastructure.nic
        tags: nic
      - role: bluebanquise.infrastructure.dns_client
        tags: dns_client
      - role: bluebanquise.infrastructure.firewall
        tags: firewall
      - role: bluebanquise.infrastructure.ssh_remote_keys
        tags: ssh_remote_keys
      - role: bluebanquise.infrastructure.time
        tags: time
        vars:
          time_profile: client

``playbooks/storage.yml`` and ``playbooks/computes.yml`` follow the exact same role list, just
with ``hosts: "fn_storage"`` and ``hosts: "fn_compute"`` respectively.

``playbooks/computes_gpu.yml`` (``hosts: "fn_compute_gpu"``) adds one role, to install the GPU
drivers on top of the same base list:

.. code-block:: yaml

  ---
  - name: computes gpu playbook
    hosts: "fn_compute_gpu"
    roles:
      - role: bluebanquise.infrastructure.hosts_file
        tags: hosts_file
      - role: bluebanquise.infrastructure.local_configuration
        tags: local_configuration
      - role: bluebanquise.infrastructure.repositories
        tags: repositories
      - role: bluebanquise.infrastructure.nic
        tags: nic
      - role: bluebanquise.infrastructure.dns_client
        tags: dns_client
      - role: bluebanquise.infrastructure.firewall
        tags: firewall
      - role: bluebanquise.infrastructure.ssh_remote_keys
        tags: ssh_remote_keys
      - role: bluebanquise.infrastructure.time
        tags: time
        vars:
          time_profile: client
      - role: bluebanquise.infrastructure.gpu
        tags: gpu
        vars:
          gpu_vendor: nvidia

.. note::

  The ``gpu`` role installs from a repository you configure separately - it does not ship the
  Nvidia driver packages itself. Add an Nvidia driver repository to ``bb_repositories`` for the
  ``hw_gpu_worker`` hosts (or to a dedicated ``os_gpu`` group if you later split GPU and CPU
  workers across OS groups) before running this playbook. See the ``gpu`` role section of this
  documentation.

Run all four:

.. code-block:: bash

  ansible-playbook playbooks/login.yml -i inventory --become
  ansible-playbook playbooks/storage.yml -i inventory --become
  ansible-playbook playbooks/computes.yml -i inventory --become
  ansible-playbook playbooks/computes_gpu.yml -i inventory --become

Each playbook already scopes itself to the right function group via its ``hosts:`` line, so
Ansible fans out across all matching hosts in parallel - no ``--limit`` needed unless you want to
target a single host while testing.

-----

At this point the core cluster is fully installed, networked, reachable over SSH, firewalled,
and time-synchronized - but there is no shared storage, no non-admin users, and no job
scheduler yet. That is what :doc:`extensions` adds next.
