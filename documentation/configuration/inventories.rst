===========
Inventories
===========

Create first inventory
======================

You can now create your first cluster inventory, which acts as a text/folders based database of your cluster description.

To do so, you can either create it manually from scratch using the remaining documentation, or initialize it with the ``bluebanquise-manager`` tool.
Both methods are exposed bellow.

Create inventory using tools
----------------------------

.. code-block:: text

  bluebanquise-manager create-inventory

.. note::

  This tool was made to cover basic clusters. In order to create a complex inventory, please refer to the documentation.
  It is possible to use both the tool and custom files. The tool will always prefix its files with ``bbm_`` prefix. Edit these files with care.
  Other files will be ignored by the tool, but not during Ansible execution.

Create inventory manually
-------------------------

Create inventories folder, and then create inside this path a new folder with your desired inventory name.
In this example, we will call our inventory **default**.

.. code-block:: text

  mkdir -p /var/lib/bluebanquise/inventories/
  mkdir /var/lib/bluebanquise/inventories/default/

Now create the group_vars all Ansible structure inside the inventory, along with the cluster folder.

.. code-block:: text

  mkdir -p /var/lib/bluebanquise/inventories/default/group_vars/all/
  mkdir -p /var/lib/bluebanquise/inventories/default/cluster

Now, set your cluster domain name, and the cluster timezone (tune according to your needs).

.. note::

  You can get the full list of available time zones using command ``timedatectl list-timezones``.

.. code-block:: text

  echo 'bb_domaine_name: "bluebanquise.cluster.local"' > /var/lib/bluebanquise/inventories/default/group_vars/all/dns.yml
  echo 'bb_time_zone: "Europe/Brussels"' > /var/lib/bluebanquise/inventories/default/group_vars/all/time.yml

Now create your first network. Current configuration is basic, you will be able to add more elements later.
Our first network will be called ``net-admin``. Please note that the prefix ``net-`` is mandatory here. This will be explained in the
networks section of this documentation.

Note also that we will consider here that our primary management node will be on ip 10.10.0.1.

.. code-block:: text

  cat << EOF > /var/lib/bluebanquise/inventories/default/group_vars/all/networks.yml
  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.1
  EOF
  
Now create your nodes file, with our first management node.
We will consider that it's network interface connected on the net-admin network is named enp0s8.

.. code-block:: text

  cat << EOF > /var/lib/bluebanquise/inventories/default/cluster/nodes.yml
  all:
    hosts:

      # Management nodes
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

Finally, create groups files, to register our management node in 3 groups: 1 function group (``fn_``), 1 os group (``os_``), and 1 hardware group (``hw_``).
Customize groups names to your needs, but make sure ``fn_management`` is preserved. This is a specific naming to identify management servers, and your
management nodes should always be in this group.

.. code-block:: text

  cat << EOF > /var/lib/bluebanquise/inventories/default/cluster/fn
  [fn_management]
  mgt1
  EOF

  cat << EOF > /var/lib/bluebanquise/inventories/default/cluster/os
  [fn_management]
  mgt1
  EOF

  cat << EOF > /var/lib/bluebanquise/inventories/default/cluster/hw
  [fn_management]
  mgt1
  EOF

You can now check that your syntax is valid using the ansible-inventory command:

.. code-block:: text

  ansible-inventory -i /var/lib/bluebanquise/inventories/default/ --graph

If you don't see any errors, then your first inventory is ready.
You can now customize it using next parts of the documentation.
