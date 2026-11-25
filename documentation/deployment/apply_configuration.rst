===================
Apply configuration
===================

Our hosts now run an operating system: it is time to give them their role in the cluster. In
BlueBanquise, this is always done the same way: we write playbooks, listing the roles each kind of
host needs, and we ask Ansible to run them with the ``ansible-playbook`` command.

The good news is that this step is the one you will repeat the most during the life of the cluster,
and it is safe to repeat: roles are idempotent, they only change what is not already as the
inventory describes it.

Playbooks
=========

A playbook tells Ansible which roles to run on which hosts. The ``hosts`` line is usually a function
group, so one playbook covers one kind of host. Let's keep all of them in
``/var/lib/bluebanquise/playbooks/``.

Here is a playbook for compute hosts:

.. code-block:: yaml

  ---
  - name: computes playbook
    hosts: "fn_compute"
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

A few habits make playbooks pleasant to live with:

* Give each role a tag named after the role, so you can run it alone (see below).
* Keep the order logical: network and repositories first, as other roles need them, then the
  firewall, then services.
* Some roles have several profiles, selected with a variable: ``time`` (``time_profile: server`` or
  ``client``), ``slurm`` (``slurm_profile: controller``, ``compute`` or ``submitter``), ``nfs``
  (server or client, see its documentation). Set them in the playbook, next to the role, as above.

Reference playbooks
-------------------

The BlueBanquise repository, cloned by the bootstrap script in
``/var/lib/bluebanquise/bluebanquise/``, contains the playbooks used by the project's automated
tests, in ``resources/workflow/playbooks/``. They are a nice source of inspiration, as each one
gathers roles of the same family:

.. list-table::
   :header-rows: 1

   * - Playbook
     - Roles
   * - ``infrastructure.yml``
     - Core of a cluster: sshd, cloudinit, http_proxy, clustershell, conman, dhcp_server,
       dns_client, dns_server, firewall, hosts_file, http_server, nic, pxe_stack, repositories,
       local_configuration, ssh_client, ssh_remote_keys, time, update_reboot, users
   * - ``hpc.yml``
     - slurm (controller, compute, submitter), nhc, lmod
   * - ``file_systems.yml``
     - nfs, xfs_quota
   * - ``logging.yml``
     - rsyslog (server, client), logrotate, loki
   * - ``monitoring.yml``
     - prometheus
   * - ``high_availability.yml``
     - pcs, drbd, haproxy, keepalived
   * - ``hardware.yml``
     - rasdaemon, bluebanquise_power
   * - ``containers.yml``
     - podman
   * - ``databases.yml``
     - mariadb
   * - ``security.yml``
     - auditd

They all target ``fn_management``, as tests run on a single host: copy the roles you need into your
own playbooks, with the right ``hosts`` line.

Run a playbook
==============

From the ``bluebanquise`` user home:

.. code-block:: bash

  cd /var/lib/bluebanquise
  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b

``-i`` points to the inventory, and ``-b`` (``--become``) lets Ansible use sudo on target hosts.
Ansible works on all hosts of the playbook in parallel, and prints a summary at the end, the
``PLAY RECAP``: for each host, how many tasks were ``ok`` (already fine), ``changed``, ``failed``,
or ``unreachable``. A second run right after the first one should show no ``changed`` task at all.

Target some hosts: limit
------------------------

``--limit`` restricts the run to some hosts, or groups:

.. code-block:: bash

  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --limit c001
  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --limit c001,c002
  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --limit 'c00[1:4]'

This is very handy to try a change on a single host before rolling it out to all.

Run some roles: tags and skip-tags
----------------------------------

Roles are tagged in the playbook, and many tasks inside roles carry tags too. ``--tags`` only runs
what matches, ``--skip-tags`` runs everything else:

.. code-block:: bash

  # Only update hosts files and time configuration
  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --tags hosts_file,time

  # Configure everything, but do not touch running services
  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --skip-tags service

Tags shared by most roles:

.. list-table::
   :header-rows: 1

   * - Tag
     - Tasks
   * - ``package``
     - Packages installation.
   * - ``template``
     - Configuration files generation.
   * - ``service``
     - Services start, restart and enablement.
   * - ``firewall``
     - Firewall ports and services opening.
   * - ``identify``
     - Hostname setting, in the ``local_configuration`` role.

For example, ``--tags template`` regenerates configuration files without installing or starting
anything, and ``--skip-tags package`` is useful when repositories are temporarily unreachable.

.. note::

  A misspelled tag is not an error for Ansible: it simply matches nothing, and nothing runs (or
  nothing is skipped). If a run seems to do nothing, check your tags first.

Pass variables: extra-vars
--------------------------

``-e`` (``--extra-vars``) sets variables with the highest precedence, above the inventory. It is
perfect for a one shot test, or to choose a behavior at run time:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventories/new_cluster -b -e "bb_start_services=false"
  ansible-playbook playbooks/management.yml -i inventories/new_cluster -b -e '{"time_external_pools": ["pool.ntp.org"]}'

Use JSON syntax, as in the second example, to pass lists or dictionaries. Anything you want to keep
belongs in the inventory, though: extra-vars are forgotten as soon as the run ends.

Preview changes: check and diff
-------------------------------

Before applying a change to a whole cluster, we can ask Ansible what it would do:

.. code-block:: bash

  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --check --diff --limit c001

``--check`` changes nothing, and ``--diff`` shows, for each file, the lines that would change. Some
tasks depend on previous ones (a package not installed yet, for example), so a check run may report
errors that a real run would not: it is a preview, not a promise.

Other useful options
--------------------

* ``-v`` to ``-vvvv``: more and more verbose output, to understand why a task fails.
* ``--start-at-task "<task name>"``: start a playbook from a given task.
* ``--list-tasks`` and ``--list-tags``: show what a playbook would run, without running anything.
* ``-f <number>`` (``--forks``): number of hosts handled in parallel (5 by default in Ansible, raise
  it on large clusters if the management host has enough CPU).

Configure the whole cluster
===========================

Once each kind of host has its playbook, configuring the whole cluster is just running them one
after the other:

.. code-block:: bash

  ansible-playbook playbooks/management.yml -i inventories/new_cluster -b
  ansible-playbook playbooks/logins.yml -i inventories/new_cluster -b
  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b

And when something changes in the inventory (a new host, a new network, a new user), run again the
playbooks of the hosts concerned, possibly limited to the relevant tags. That's all there is to it:
the inventory describes, the playbooks apply.

.. note::

  When you add a host, remember the management host also needs to know it: re-run on the management
  host the roles that list hosts (``hosts_file``, ``dhcp_server``, ``dns_server``, ``pxe_stack``,
  ``conman``, ``ssh_client``...) before deploying the new host.
