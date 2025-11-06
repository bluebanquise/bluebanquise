==========
Hosts file
==========

Hosts file (/etc/hosts) is generated using all the nodes provided in the inventory.

There are few settings related to its generation.

External hosts
==============

It is possible to define external hosts to be added into hosts file.
To do so, define ``hosts_file_external_hosts`` this way:

.. code:: yaml

  hosts_file_external_hosts:
    myhost: 10.10.10.10
    mysecondhost: 7.7.7.7
    mythirdhost:
        ip4: 10.10.10.33
        alias:
        - machine3
        - extmachine3

Domain name
===========

The role will use either ``bb_domain_name`` or ``hosts_file_domain_name`` variable to set FQDN. Default is ``cluster.local`` if none is set.
Note that ``hosts_file_domain_name`` precedence the global variable ``bb_domain_name`` if both are set. 

Extended naming
===============

User can enable or disable extended naming using the ``hosts_file_enable_extended_names`` variable.
Default is ``true``.

For example, for an host defined this way:

.. code:: yaml

  c001:
    alias:
        - foobar
    network_interfaces:
        - name: eth0
        ip4: 10.10.3.1
        network: net-admin
        - name: eth1
        ip4: 10.20.3.1
        network: para
        alias: fuuuuu

If ``hosts_file_enable_extended_names: true``, then the following content will be written by default into /etc/hosts file (assuming here domain name set is ``bluebanquise.local``):

.. code:: text

    10.10.0.3 c001 c001.bluebanquise.local foobar
    10.10.3.1 c001-net-admin
    10.20.3.1 c001-para fuuuuu


While if ``hosts_file_enable_extended_names: false``, then the following content will be written into ``/etc/hosts`` file:

.. code:: text

    10.10.0.3 c001 c001.bluebanquise.local foobar
