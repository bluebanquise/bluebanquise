===========
Inventories
===========

The inventory is the heart of a BlueBanquise cluster. It is a set of plain text files, organized in
folders, that describes everything about your cluster: its networks, its hosts, their hardware and
operating system, and the settings of each service. Think of it as a small database, that you can
read, edit with any text editor, and keep under version control.

Roles read this description, and turn it into configuration on the hosts. So the better the
inventory describes the cluster, the less you will have to do by hand.

Create your first inventory
===========================

Let's create a first, minimal inventory, with a single management host. We will call it
**new_cluster**, and store it in the ``bluebanquise`` user home, next to other inventories you might
create later.

.. code-block:: text

  mkdir -p /var/lib/bluebanquise/inventories/new_cluster/group_vars/all/
  mkdir -p /var/lib/bluebanquise/inventories/new_cluster/cluster/

Global settings
---------------

Set the cluster domain name and time zone (see :doc:`general_settings` for details):

.. code-block:: text

  echo 'bb_domain_name: "bluebanquise.cluster.local"' > /var/lib/bluebanquise/inventories/new_cluster/group_vars/all/dns.yml
  echo 'bb_time_zone: "Europe/Brussels"' > /var/lib/bluebanquise/inventories/new_cluster/group_vars/all/time.yml

First network
-------------

Now let's create our first network, ``net-admin``. The ``net-`` prefix matters: it tells the stack
this is a management network, on which hosts are deployed and reached (see :doc:`networks`). Our
management host will use the address ``10.10.0.1`` on it.

.. code-block:: text

  cat << EOF > /var/lib/bluebanquise/inventories/new_cluster/group_vars/all/networks.yml
  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1
  EOF

First host
----------

Next, our first host, the management host ``mgt1``, connected to ``net-admin`` through its
``enp0s8`` interface:

.. code-block:: text

  cat << EOF > /var/lib/bluebanquise/inventories/new_cluster/cluster/nodes.yml
  all:
    hosts:

      # Management hosts
      mgt1:
        # bmc:
        #   name: bmgt1
        #   ip4: 10.10.100.1
        #   network: net-admin
        #   mac: 2a:2b:3c:4d:5e:6f
        network_interfaces:
          - interface: enp0s8
            ip4: 10.10.0.1
            network: net-admin
            mac: 1a:2b:3c:4d:1e:9f
  EOF

Groups
------

Finally, every host belongs to 3 groups: a function group (``fn_``), an operating system group
(``os_``), and a hardware group (``hw_``). Name them as you like, with one exception:
``fn_management`` is reserved for management hosts, and the stack relies on it, so always keep your
management hosts in it.

.. code-block:: text

  cat << EOF > /var/lib/bluebanquise/inventories/new_cluster/cluster/fn
  [fn_management]
  mgt1
  EOF

  cat << EOF > /var/lib/bluebanquise/inventories/new_cluster/cluster/os
  [os_ubuntu_24]
  mgt1
  EOF

  cat << EOF > /var/lib/bluebanquise/inventories/new_cluster/cluster/hw
  [hw_MSI_X99A_SLI]
  mgt1
  EOF

.. note::

  Ansible group names may only contain letters, digits and underscores: prefer ``os_ubuntu_24``
  to ``os_ubuntu_24.04``.

Check it
--------

Let's ask Ansible how it understands our inventory:

.. code-block:: text

  ansible-inventory -i /var/lib/bluebanquise/inventories/new_cluster/ --graph
  ansible-inventory -i /var/lib/bluebanquise/inventories/new_cluster/ --host mgt1

The first command shows groups and their hosts, the second all the variables ``mgt1`` inherits. If no
error shows up, congratulations, your first inventory is ready! The next pages of this documentation
will enrich it step by step.

Optional: keep it in git
------------------------

We warmly recommend turning the inventory into a git repository, especially when several people edit
it. You will be able to see what changed, when, and to go back in time when something goes wrong.

.. code-block:: text

  cd /var/lib/bluebanquise/inventories/new_cluster/
  git init
  git add .
  git commit -m "First commit"

Then, simply remember to commit each change.

Where to set variables
======================

BlueBanquise relies on Ansible inventories, and so on their variables inheritance and precedence
mechanism. The inventory tree looks like this:

.. code-block:: text

  inventory_root/
  ├── cluster
  ├── group_vars
  │   └── all
  └── host_vars

.. warning::

  Ansible reads **all** YAML files of the inventory, whatever their name. Do not keep backup copies
  like ``networks.yml.bkp`` inside it: they would be read too!

Imagine each host looking at the inventory from its own angle: all hosts see the same files, but each
one gathers a slightly different set of variables.

1. Every host is a member of the ``all`` group, so it reads all files of ``group_vars/all/``.
2. A host member of a group, for example ``red``, also reads all files of ``group_vars/red/``.
3. A host, for example ``c001``, also reads all files of ``host_vars/c001/``.
4. Finally, a host reads the variables set under its name in the files of ``cluster/`` (like
   ``network_interfaces`` in ``cluster/nodes.yml`` above).

When the same variable is set at several places, the most specific one wins:

.. code-block:: text

  inventory_root/
  ├── cluster (1)
  ├── group_vars
  │   ├── all (3)
  │   └── red (2)
  └── host_vars
      └── c001 (1)

``host_vars`` and ``cluster/`` host variables (same level) > ``group_vars/<group>/`` >
``group_vars/all/``.

You can use all of this freely to describe your cluster, with one rule to keep in mind: ``os_`` and
``hw_`` prefixed variables must only be set in ``group_vars/`` folders (OS and hardware groups, or
``all``), never in ``host_vars`` (see :doc:`groups`).

``[SCHEMA: inventory-precedence]``
  *The inventory tree above drawn as folders, with arrows from each level to a host "c001" in the
  middle, and a podium (1, 2, 3) showing that host_vars/cluster beats group_vars/<group>, which beats
  group_vars/all.*
