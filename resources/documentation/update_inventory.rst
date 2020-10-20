Updating your inventory
=======================

Changing MAC Address
--------------------

You can update your inventory to change a MAC Address or a hostname.
To do this, modify the value of the key in the yml inventories files.
Examples of keys: **mac**, **ip4**, **interface**, **network**


Example to change the c001 node mac address:

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
                 mac: 00:25:90:fd:10:79   <-- change this MAC address
                 network: ice1-1
               - interface: ib0
                 ip4: 10.20.3.1
                 network: interconnect-1
                 type: infiniband
