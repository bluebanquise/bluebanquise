==========
Operations
==========

The cluster is deployed: congratulations! Now begins its day to day life. This page gathers the
tools the stack provides to take care of it, so you know where to look when a host needs a reboot, a
console, an update or a closer look.

All commands below run on the management host. Most of them accept hosts as a *nodeset*, the compact
ClusterShell notation: ``c001``, ``c[001-004]``, ``c[001-004],login1``, or a group, ``@fn_compute``.

Run commands on many hosts: ClusterShell
========================================

The ``clustershell`` role writes every Ansible group of the inventory as a ClusterShell group. Let's
list them:

.. code-block:: bash

  nodeset -LL

Then ``clush`` runs a command on many hosts at once, over SSH, and ``-b`` gathers identical outputs
together, which keeps things readable even on thousands of hosts:

.. code-block:: bash

  clush -bw @fn_compute uptime
  clush -bw c[001-004] 'systemctl is-active chronyd'

Power: bluebanquise-power and powerman
======================================

Hosts having a ``bmc`` in the inventory, and credentials in their hardware group
(``hw_board_authentication``), can be powered on and off remotely.

The ``bluebanquise_power`` role installs ``bluebanquise-power``, and its short alias ``bbp``. It
speaks IPMI and Redfish, and can also choose the next boot device, which is perfect to trigger a
redeployment:

.. code-block:: bash

  bbp c001 power status
  bbp c[001-004] boot pxe
  bbp c[001-004] power reset
  bbp --delay 2 --random c[001-100] power on

The ``--delay`` and ``--random`` options spread power on over time, so hundreds of hosts do not draw
current all at the same instant. ``--dryrun`` shows what would be done, without touching anything.

The ``powerman`` role provides the classic powerman daemon, for IPMI hosts:

.. code-block:: bash

  powerman --query c[001-004]
  powerman --on c[001-004]

Consoles: conman
================

When a host does not answer anymore, its serial console is often the best way to understand why. The
``conman`` role connects to all consoles through BMCs (IPMI Serial over LAN, or SSH for Redfish
BMCs), and logs them continuously, so you can even read what happened before you connected.

.. code-block:: bash

  conman c001

To leave the console, press ``Enter``, then ``&``, then ``.``.

Hosts need a serial console in their kernel parameters for this to work, through ``hw_console`` in
their hardware group (see :doc:`../configuration/hardware_settings`).

Network boot: bluebanquise-bootset
==================================

``bluebanquise-bootset`` tells hosts what to do at next network boot. To redeploy a host:

.. code-block:: bash

  sudo bluebanquise-bootset -n c001 -b osdeploy
  bbp c001 boot pxe
  bbp c001 power reset

And to follow it:

.. code-block:: bash

  sudo bluebanquise-bootset -n c001 -s

See :doc:`../deployment/provision_os`, and the **pxe_stack** role documentation, for all options
(boot sequences, memory tests, diskless images...).

Updates
=======

The ``update_reboot`` role upgrades all packages of hosts, and reboots them when something was
upgraded, waiting for them to come back before the playbook continues. It does nothing by default,
so we enable it explicitly, for example for a single run:

.. code-block:: bash

  ansible-playbook playbooks/computes.yml -i inventories/new_cluster -b --tags update_reboot \
    -e "update_reboot_upgrade_packages=true update_reboot_reboot=true"

Add ``--limit`` to update hosts by small batches, and keep the cluster available while doing so.

To stay on a given kernel version whatever the updates, see the kernel version lock of
:doc:`../configuration/os_settings`.

Logs
====

The ``rsyslog`` role centralizes logs: clients (``rsyslog_profile: client``) send their logs to the
server (``rsyslog_profile: server``), which stores them in ``/var/log/rsyslog/<host>/``, rotated by
the ``logrotate`` role. Reading the logs of a host, even unreachable, is then just:

.. code-block:: bash

  less /var/log/rsyslog/c001/messages

For searches across all hosts, the ``loki`` role stores these logs in Loki, to be queried from
Grafana (``grafana`` role), for example ``{job="syslog", host="c001", level="error"}``.

Monitoring
==========

The ``prometheus`` role deploys Prometheus, Alertmanager and Karma on the management host, and
exporters on hosts, to collect metrics: load, memory, temperatures through BMCs (``ipmi_exporter``),
Slurm jobs, and more. With the ``grafana`` role, we get nice dashboards on top.

By default:

* Prometheus answers on ``http://<management host>:9090``,
* Alertmanager on port ``9093``,
* Karma, the alerts dashboard, on port ``8080``,
* Grafana on port ``3000``.

Prometheus is a *metrics* tool: it tells you how things evolve over time. To be warned when
something breaks, configure alerts (see the **prometheus** role documentation).

Hardware errors
===============

The ``rasdaemon`` role collects hardware errors reported by the kernel (memory ECC errors, PCIe
errors, machine checks...). On a host, ``ras-mc-ctl --summary`` and ``ras-mc-ctl --errors`` show
them. Combined with ``nhc`` (Node Health Check) on HPC clusters, faulty hosts can be removed from
production before they make jobs fail.

``[SCHEMA: operations-tools]``
  *The management host in the center, with one arrow per tool towards a row of hosts: clush (SSH),
  bbp and powerman (BMC, power icon), conman (BMC, console icon), bluebanquise-bootset (PXE files),
  rsyslog (logs arrows coming back from hosts), prometheus (metrics arrows coming back from
  hosts).*
