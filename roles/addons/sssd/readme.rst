SSSD
---------------

Description
^^^^^^^^^^^

This role provides a basic configuration of SSSD to connect to an LDAP client.

Instructions
^^^^^^^^^^^^

LDAP servers URL must be configured in the inventory like the example below:

.. code-block:: yaml

    ## List of logical networks
    networks:
    
      ice1-1:
        subnet: 10.10.0.0
        prefix: 16
        netmask: 255.255.0.0
        broadcast: 10.10.255.255
        dhcp_unknown_range: 10.10.254.1 10.10.254.254
        gateway: 10.10.2.1
        is_in_dhcp: true
        is_in_dns: true
        services_ip:
          pxe_ip: 10.10.0.1
          dns_ip: 10.10.0.1
          repository_ip: 10.10.0.1
          authentication_servers:
            - ldaps://my-ldap-server-1
            - ldap://my-ldap-server-2
          time_ip: 10.10.0.1
          log_ip: 10.10.0.1

The following example configure LDAP secured server *my-ldap-server-1* as first server and *my-ldap-server-2* as second server.

Changelog
^^^^^^^^^

* 1.0.2: Support multiple and secured connections to LDAP servers. <mathis.gavillon@atos.net>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. oxedions <oxedions@gmail.com>
 
