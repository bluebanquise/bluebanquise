Adding or Removing a node
=========================

Adding c00x node in your inventory
----------------------------------

Open your inventory file /etc/bluebanquise/inventory/cluster/nodes/computes.yml:

.. code-block:: yaml

   mg_computes:
     children:
       equipment_typeC:
         hosts:
           c001:
             alias:
               - compute001
             bmc:
               name: bmc-c001
               ip4: 10.11.103.1
               mac: 00:25:90:fe:f3:cc
               network: ice1-1
             network_interfaces:
               - interface: eno2
                 ip4: 10.11.3.1
                 mac: 00:25:90:fd:10:79
                 network: ice1-1
               - interface: ib0
                 ip4: 10.20.3.1
                 network: interconnect-1
                 type: infiniband

Add the following yaml code and be sure to replace the items below (mac, ip4, network):

.. code-block:: yaml

    c00x:
      alias:
        - compute00x
      bmc:
        name: bmc-c00x
        ip4: 10.11.103.2
        mac: 00:25:90:fe:f3:cd
        network: ice1-1
      network_interfaces:
        - interface: eno2
          ip4: 10.11.3.2
          mac: 00:25:90:fd:10:78
          network: ice1-1
        - interface: ib0
          ip4: 10.20.3.2
          network: interconnect-1
          type: infiniband


Finally, your inventory file should look like this.

.. code-block:: yaml

  mg_computes:
    children:
      equipment_typeC:
        hosts:
          c001:
            bmc:
              name: bmc-c001
              ip4: 10.11.103.1
              mac: 00:25:90:fe:f3:cc
              network: ice1-1
            network_interfaces:
              - interface: eno2
                ip4: 10.11.3.1
                mac: 00:25:90:fd:10:79
                network: ice1-1
              - interface: ib0
                ip4: 10.20.3.1
                network: interconnect-1
                type: infiniband
          c00x:
            bmc:
              name: bmc-c00x
              ip4: 10.11.103.2
              mac: 00:25:90:fe:f3:cd
              network: ice1-1
            network_interfaces:
              - interface: eno2
                ip4: 10.11.3.2
                mac: 00:25:90:fd:10:78
                network: ice1-1
              - interface: ib0
                ip4: 10.20.3.2
                network: interconnect-1
                type: infiniband


You can create the inventory graph with the ansible-inventory command:

.. code-block:: text

  ansible-inventory --graph
  @all:
    |--@mg_ management:
    |  |--@equipment_typeM
    |  |  |--mngt0-1
    |--@mg_computes:
    |  |--@equipment_typeC:
    |  |  |--c001
    |  |  |--c00x              <--- NEW NODE ADDED


Removing a node in your inventory
---------------------------------

To remove a node, perform the opposite procedure.
