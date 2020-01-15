DNS client
----------

Description
^^^^^^^^^^^

This role provides a basic /etc/resolv.conf file.

Instructions
^^^^^^^^^^^^

Configuration is made in *group_vars/all/general_settings/external.yml*.

It is possible to add here external DNS servers for clients:

.. code-block:: yaml

  external_dns:
    dns_client:  <<<<<<<<<<
      - 208.67.220.220

Note that this/these external(s) dns will be placed after the cluster internal dns in resolution order.

Changelog
^^^^^^^^^

* 1.0.2: Added variable for role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
