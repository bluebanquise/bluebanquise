OpenLDAP server
---------------

Description
^^^^^^^^^^^

This role provides a basic but UNSECURE ldap server. It also provides phpldapadmin configuration to manage LDAP.

.. warning::
  While it is theoretically possible to use openldap server on RHEL/CentOS 8, 
  needed packages are no more provided in official or EPEL repositories.
  This role should only be used on RHEL/CentOS 7 versions.

Instructions
^^^^^^^^^^^^

Login into http://localhost/phpldapadmin to manage LDAP.

Keep in mind this role is for the time being unsecure.

To be done
^^^^^^^^^^

Enable encryption to secure this role.

Changelog
^^^^^^^^^

* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
