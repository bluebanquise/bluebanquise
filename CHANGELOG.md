# Changelog

## 1.3.0 RC2 - 2020-08-20

### Breaking changes:

#### Introduce new network_interfaces format

In previous releases, the `network_interfaces` parameter was a dictionary with
the interface names as keys.

Previous inventory format (<= 1.2):

  ```
  network_interfaces:
    enp0s3:
      ip4: 10.10.0.1
      mac: 08:00:27:dc:f8:f5
      network: ice1-1
    ib0:
      ip4: 10.20.0.1
      network: interconnect-1
  ```

The `network_interfaces` parameter is now a list where each element includes all
the information for a given interface.

New inventory format:

  ```
  network_interfaces:
    - interface: enp0s3
      ip4: 10.10.0.1
      mac: 08:00:27:dc:f8:f5
      network: ice1-1
    - interface: ib0
      ip4: 10.20.0.1
      network: interconnect-1
  ```

The rules below apply:

1. The main resolution network of hosts is the value of the *network* parameter
   of the **first** item of the list (e.g., c001 will be on the same line than
   c001-ice1-1 in the hosts file).
2. First management network related item in the list will be the ansible main
   ssh target interface (from ssh_master role), and also the main management
   network interface for the client (services_ip to target on client side).

With the example above, if one wish direct resolution to be on *interconnect-1*,
they must simply move it to the first position in the list. Command `ping c001`
will then resolve to *interconnect-1*, while `ssh c001` will still use
management network *ice1-1*.

The `network_interfaces parameter` is defined for each host of the inventory. A
[script](tools/inventory-converter-1.3-network_interfaces.py) is available to
convert existing inventories to the new format.

  ```
  Usage: ./tools/inventory-converter-1.3-network_interfaces.py inventory/cluster/nodes/file.yml
  ```

#### Merge all networks definition in a single file

To prepare the deprecation of *hash behaviour* in Ansible, all the networks must
be merged in the same file, under the `networks` key.

Use the commands below to convert existing inventories:

  ```
  # awk '!/^networks:$/ || ++ctr != 2' inventory/group_vars/all/networks/* > inventory/group_vars/all/networks.yml
  # rm -r inventory/group_vars/all/networks/
  ```

#### Rename the group_vars/all/all_equipment directory

The `group_vars/all/all_equipment` directory is renamed
`group_vars/all/equipment_all`.

Use the commands below to convert existing inventories:

  ```
  # git mv group_vars/all/all_equipment group_vars/all/equipment_all
  ```

#### Remove the equipment_profile and authentication keys

To prepare the deprecation of *hash_behaviour* in Ansible, the dictionaries
*equipment_profile* and *authentication* are removed. The parameters defined in
these dictionaries are kept and must now be prefixed respectively with *ep_* and
*authentication_*.

The configuration files must be kept in the directories:

 - inventory/group_vars/all/equipment_all/
 - inventory/group_vars/equipment_xxx/

Use the commands below to convert existing inventories:

  ```
  # sed -i -e 's/^equipment_profile:$/---/' \
             -e 's/^  //' \
             -e 's/^\([a-z]\)/ep_\1/' \
  inventory/group_vars/all/equipment_all/equipment_profile.yml \
  inventory/group_vars/equipment_type*/equipment_profile.yml

  # sed -i -e 's/^authentication:$/---/' \
             -e 's/^  //' \
             -e 's/^\([a-z]\)/authentication_\1/' \
  inventory/group_vars/all/equipment_all/authentication.yml \
  inventory/group_vars/equipment_type*/authentication.yml
  ```

#### access_control is not a boolean anymore

Note: The new name of *access_control* is *ep_access_control*.

For SELinux, the supported values are: **enforcing**, **permissive**, or
**disabled**.

Example:
  ```
  ep_access_control: enforcing  # SELinux: enforcing, permissive, disabled
  ```
