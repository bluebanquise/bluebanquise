================
Core: deployment
================

Our inventory is ready: now comes the fun part! In this page, we configure mgt1, deploy the
operating system of the 8 other hosts over the network, and apply their base configuration. Shared
storage, users and Slurm come next, in :doc:`extensions`.

All commands run as the ``bluebanquise`` user, from its home:

.. code-block:: bash

  cd /var/lib/bluebanquise
  mkdir -p playbooks

Configure mgt1
==============

``playbooks/management.yml``:

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
      - role: bluebanquise.infrastructure.firewall
        tags: firewall
      - role: bluebanquise.infrastructure.dhcp_server
        tags: dhcp_server
      - role: bluebanquise.infrastructure.dns_server
        tags: dns_server
      - role: bluebanquise.infrastructure.dns_client
        tags: dns_client
      - role: bluebanquise.infrastructure.http_server
        tags: http_server
      - role: bluebanquise.infrastructure.pxe_stack
        tags: pxe_stack
      - role: bluebanquise.infrastructure.ssh_client
        tags: ssh_client
      - role: bluebanquise.infrastructure.time
        tags: time
        vars:
          time_profile: server
      - role: bluebanquise.infrastructure.clustershell
        tags: clustershell
      - role: bluebanquise.infrastructure.bluebanquise_power
        tags: bluebanquise_power

The ``firewall`` role comes before the services, as each of them opens its ports in firewalld,
which must already be running. ``dns_server`` comes before ``dns_client``, so mgt1 has a working DNS
server before using it.

We start with the network interfaces and repositories, so the rest of the run can install packages.
As we are connected to mgt1 through its ``datacenter`` interface, let's double check its definition
in the inventory first: we would not want to cut the branch we are sitting on!

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventories/example_cluster -b --limit mgt1 --tags nic,repositories

Check with ``ip a`` that ``eth1`` (``net-admin``, ``10.10.0.1``) and ``eth2`` (``net-bmc``,
``10.11.0.1``) are up, and with ``ip route`` that the default route goes through ``192.168.0.200``.
Then, let's run everything:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventories/example_cluster -b --limit mgt1

This takes a few minutes. You can run it again as often as you like: only what differs from the
inventory gets changed. See :doc:`../../deployment/apply_configuration` for all the options of
``ansible-playbook``.

Provide the installation media
==============================

mgt1 now serves DHCP, DNS, HTTP and the PXE files. The last thing it needs is the RHEL 10
installation media, for both architectures of our cluster (x86_64 for most hosts, arm64 for GPU
workers). ``bluebanquise-netboots-installer`` downloads and extracts them at the right place:

.. code-block:: bash

  sudo bluebanquise-netboots-installer install rhel_10 x86_64
  sudo bluebanquise-netboots-installer install rhel_10 arm64

The default catalog uses Rocky Linux 10 ISOs; it can be edited to use another RHEL 10 compatible
distribution, or local copies (see :doc:`../../deployment/provision_os`).

Deploy the operating systems
============================

Let's tell the 8 hosts to deploy their operating system at their next network boot, and check:

.. code-block:: bash

  sudo bluebanquise-bootset -n login,storage,c[001-004],g[001-004] -b osdeploy
  sudo bluebanquise-bootset -n login,storage,c[001-004],g[001-004] -s

All 8 hosts should be listed under ``menu-default=osdeploy``.

Now, power them on. Compute workers have a BMC, so we can do it from mgt1 with ``bbp`` (installed
by the ``bluebanquise_power`` role); login and storage have no BMC in our example, so let's press
their power button:

.. code-block:: bash

  bbp c[001-004],g[001-004] boot pxe
  bbp c[001-004],g[001-004] power on

Each host gets its address from DHCP, loads iPXE, downloads its own file
``pxe/nodes/<hostname>.ipxe``, then the file of its equipment profile (console, kernel parameters,
partitioning, SSH keys...), and installs RHEL 10, unattended. It takes 5 to 20 minutes, all hosts in
parallel. The **pxe_stack** role documentation details the whole boot chain, if you are curious.

Let's follow the progress:

.. code-block:: bash

  sudo bluebanquise-bootset -n login,storage,c[001-004],g[001-004] -s

The status of each host goes from ``osdeploy running`` (installation started) to
``osdeploy completed`` (installation done). At that moment, the host is automatically switched to
``menu-default=disk``, so it boots on its freshly installed system instead of reinstalling it.

Once installed, hosts accept SSH connections from the ``bluebanquise`` user of mgt1, thanks to the
key set in ``os_admin_ssh_keys``. Let's check:

.. code-block:: bash

  ssh c001 hostname

Apply the base configuration
============================

All hosts share the same base. ``playbooks/login.yml``:

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
      - role: bluebanquise.infrastructure.firewall
        tags: firewall
      - role: bluebanquise.infrastructure.dns_client
        tags: dns_client
      - role: bluebanquise.infrastructure.ssh_remote_keys
        tags: ssh_remote_keys
      - role: bluebanquise.infrastructure.time
        tags: time
        vars:
          time_profile: client

``playbooks/storage.yml`` and ``playbooks/computes.yml`` are identical, with
``hosts: "fn_storage"`` and ``hosts: "fn_compute"``.

``playbooks/computes_gpu.yml`` (``hosts: "fn_compute_gpu"``) adds the ``gpu`` role at the end, to
install Nvidia drivers and CUDA. All its settings are already in the ``hw_gpu_worker`` group:

.. code-block:: yaml

      - role: bluebanquise.infrastructure.gpu
        tags: gpu

login comes first, as it is the gateway of all other hosts: once it is configured, they can reach
the internet through it.

.. code-block:: bash

  ansible-playbook playbooks/login.yml -i inventories/example_cluster -b
  ansible-playbook playbooks/storage.yml -i inventories/example_cluster -b
  ansible-playbook playbooks/computes.yml -i inventories/example_cluster -b
  ansible-playbook playbooks/computes_gpu.yml -i inventories/example_cluster -b

Each playbook targets a function group, so Ansible configures all its hosts in parallel. Add
``--limit c001`` to try on a single host first.

Let's check that a compute worker reaches the internet through login, and that GPUs are there:

.. code-block:: bash

  ssh c001 curl -sI https://bluebanquise.com | head -1
  clush -bw g[001-004] nvidia-smi -L

-----

Our core cluster is up: all hosts are installed, networked, reachable with SSH, protected by their
firewall, and agree on the time. Well done! Let's now make it useful, with :doc:`extensions`.
