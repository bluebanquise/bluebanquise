Customize your cluster inventory 
================================

Changing the Cluster Name
-------------------------

To change the name of your Cluster, edit the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/general.yml`` and replace ``algoric`` by your cluster name.

.. code-block:: yaml

 cluster_name: algoric

Changing the Time Zone
----------------------

To identify which time zone is closest to your present location, use the ``timedatectl`` command with the ``list-timezones`` command line option.
For example, to list all available time zones in Europe, type:

.. code-block:: shell

 timedatectl list-timezones | grep Paris
 Europe/Amsterdam
 Europe/Andorra
 Europe/Athens
 Europe/Belgrade
 Europe/Berlin
 Europe/Bratislava

Edit the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/general.yml`` and change the ``time_zone`` value:

.. code-block:: yaml

 time_zone: Europe/Paris

Changing Services Handling
--------------------------

You can decide to enable and start the services after running the ansible playbooks.
This allows you to keep control over your infrastructure. For example, for the activation of high availability, it is necessary to set the variable ``start_services`` to "false".

Change these values in the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/general.yml``:

.. code-block:: yaml

 enable_services: true # Enable or disable services on startup (set to false when using high availability)
 start_services: true # Handle start/restart of the services (set to false when using high availability)


Changing the Domain Name
------------------------

Edit the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/network.yml`` and change the ``domain_name`` value:

.. code-block:: yaml

 domain_name: tumulus.local

Changing the naming convention
------------------------------

.. warning::
   By default, **BlueBanquise** delivers the naming conventions shown below. 
   
But you can change them and update your inventories to match these rules.

Edit the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/internal_variables.yml`` and change the values.

.. code-block:: yaml
  
 iceberg_naming: iceberg
 equipment_naming: equipment
 management_networks_naming: ice
 master_groups_naming: mg
 managements_group_name: mg_managements


Disabling the SSH strict host key checking
------------------------------------------

.. warning::
   In SMC it is possible to disable the strict host key checking in the inventory.
   **By default it is an activated option.**

As a reminder, if this flag is set to 'yes', ssh will never automatically add host keys to the ``~/.ssh/known_hosts`` file, and refuses to connect to hosts whose host key has changed.
This provides maximum protection against trojan horse attacks.

To disable the SSH strict host key checking, edit the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/security.yml`` and change the ``hostkey_checking`` value:

.. code-block:: yaml

 security:
   ssh:
     hostkey_checking: true # enable or disable hostkey checking

Configure Network Time Protocol (NTP)
-------------------------------------

To synchronize with a time server, update the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/external.yml``
If you have your own time servers, replace these values:

.. code-block:: yaml

  external_time:
    time_server:
      pool: # List of possible time pools
        - pool.ntp.org
      server: # List of possible time servers
        - 0.pool.ntp.org
        - 1.pool.ntp.org
    time_client:
      pool:
      server:

Adding external Domain Name Server (DNS)
----------------------------------------

To change or add DNS servers, update the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/external.yml`` as follows:

.. code-block:: yaml

  external_dns:
    dns_server: # set as forwarders in named.conf
    dns_client: # set directly on client side in resolv.conf
      - 208.67.220.220

Adding external hosts
---------------------

To add external hosts, add them to the file ``/etc/bluebanquise/inventory/group_vars/all/general_settings/external.yml``
These hosts will be written by the ``hosts_file`` role in the ``/etc/hosts`` file.

Example:

.. code-block:: yaml
  
  external_hosts:
    sphenisc.com: 213.186.33.3
    my_external_host1: 1.2.3.4
    my_external_host2: 11.22.33.44
