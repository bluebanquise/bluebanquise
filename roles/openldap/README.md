# OpenLDAP

WARNING: This role need a full revamp and should be considered beta.

## Description

This role provides a basic but UNSECURE ldap server and associated SSSD
configuration on clients. It also provides phpldapadmin configuration to
manage LDAP sever.

Note that to grab rpms for RHEL 8, the following source can be used:
https://ltb-project.org/download#packages_for_red_hatcentos

## Instructions

### Server side

Add the following variables into your inventory:

```yaml
ldap_settings:
  manager_password_hash: '{SSHA}VhOAYNMM9UczGgn6CB1W1YLSowAdamXA'
  manager_password: root
```

You should replace those passwords for more secure ones, you can do so on an server that you have the slappasswd command available:

```
$  slappasswd -h {SSHA} -s abcd123
{SSHA}z9ktNJF1HLU0hUp1x+0ZFJVFxU8yCR8v
```

The default backend database that this role expects is 'hdb', if you are using some diferent one, for instance 'mdb', just add the openldap_backend_db option to vars, example for 'mdb':
```
openldap_backend_db: mdb
```

Deploy the role, then login into http://localhost/phpldapadmin to manage LDAP.

Keep in mind this role is for the time being unsecure.

### Client side

LDAP servers URL must be configured in the inventory like the example below:

```yaml
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
```

The following example configure LDAP secured server *my-ldap-server-1* as first
server and *my-ldap-server-2* as second server.

## To be done

Role need whole revamp.
- Enable encryption to secure this role.
- remove manager_password plaintext requirement.

## Changelog

* 1.1.0: Fixed some bugs and added The possibility to set other options for backend DB <lucassouzasantos@gmail.com>
* 1.0.2: Support multiple and secured connections to LDAP servers. <mathis.gavillon@atos.net>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
