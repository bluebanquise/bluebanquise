Hosts file
----------

Description
^^^^^^^^^^^

This role provides a basic /etc/hosts files.

Instructions
^^^^^^^^^^^^

This role will gather all hosts from the inventory, and add them, using all
their known internal network connections ip, into */etc/hosts* file.

In case of multiple icebergs system, administrator can reduce the scope of this
gathering using **hosts_file.range** variable in
*group_vars/all/general_settings/general.yml*.
Setting **range** to *all* will use all Ansible inventory hosts, while setting
**range** to *iceberg* will reduce the gathering to the current host iceberg.

.. code-block:: yaml

  hosts_file:  <<<<<<<<
    range: all # can be all (all hosts) or iceberg (iceberg only)

External hosts defined in *group_vars/all/general_settings/external.yml*
at variable **external_hosts** will be automatically added in the */etc/hosts*
file.

Input
^^^^^

Mandatory inventory vars:

**hostvars[host]**

* network_interfaces
   * .ip4
   * .mac

Optional inventory vars:

**hostvars[hosts]**

* alias
* global_alias
* bmc
   * .ip4
   * .mac
   * .name

Output
^^^^^^

Files generated:

* /etc/hosts

Changelog
^^^^^^^^^

* 1.0.7: Clean code. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.4: Rewrite whole macro, add BMC alias. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Accelerated mode. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Added role version. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
