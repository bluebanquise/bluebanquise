# Changelog

## 1.5.0 - Next-release

### Major changes

#### Overall changes

  - add Ubuntu 18.04 and 20.04 partial support (#582)

#### New roles

  - filesystem: set filesystems (#573)
  - modprobe: load/unload kernel modules (#573)
  - mount: mount devices (#573)
  - parted: set partitions (#573)
  - sudoers: add users or groups to sudoers (#573)

#### Roles improvement or fix

  - all: add compatibility with multiple RHEL like distributions (#560)
  - advanced_dhcp_server: fix issue with added spaces. Could prevent DHCP to start (#561)
  - diskless:
    - fix issues with dnf command in the livenet module (#528)
    - fix issues preventing access to nodes booting a livenet image (#525)
    - notify in readme/page that firewall does not work in chroot (#569)
    - fix python path of diskless files (#590)
  - kernel_config: prevent crash if variable ep_kernel_parameters is undefined (#559)
  - log_server/client:
    - allow custom configuration path (#591)
  - nic_nmcli:
    - add dns4 and dns4_search vars logic (#585)
    - improve role capabilities (#558)
  - pxe_stack: fix issues with hostname not set during kickstart on RHEL 8.3 (#522)
  - set_hostname: add fqdn capability (#543)
  - ssh_master: add custom config variable (#579)
  - time:
    - allow to set sysconfig OPTIONS for chronyd (#552)
    - allow to add additional networks for server to reply (#555)
    - allow custom configuration path (#591)

### Breaking changes

## 1.4.0

### Major changes

#### New roles

  - addons/kernel_config: set or update kernel parameters and sysctl (#481)
  - addons/lmod: allow to install Lmod and specify custom modulefiles path (#390)
  - addons/lvm: allow to configure lvm storage (#446)
  - addons/nhc: allow to install and setup nhc (#448)
  - addons/singularity: allow to install Singularity (#403)

#### Roles improvement or fix

  - addons/nic_nmcli:
    - add all ansible nmcli module capabilities (#444)
    - add routes handling on interfaces (#469)
    - convert to new inventory format (#401)
  - addons/ofed:
    - add tunables to set soft/hard memlock limits. Default to unlimited (#492)
  - advanced_core/advanced_dhcp_server:
    - add multiple entries per host capability (#470)
    - add custom options definition for each host (#470)
    - add patterns capability to write hosts configuration (#470)
    - improve template rendering time (#470)
  - core/conman:
    - run the conman service with user conman (#493, #496)
  - core/hosts_file:
    - prevent many blank lines when hosts have no network_interfaces in the inventory (#406)
  - core/log_client:
    - add a new parameter to set rsyslog default verbosity (#466)
    - add a new parameter to change default rsyslog configuration (#488)
  - core/pxe_stack:
    - change bootset configuration files path (issue with multiple icebergs) (#514)
  - core/rsyslog_server and core/rsyslog_client:
    - allow custom server port (#397)
  - core/ssh_master:
    - add ssh jump capability in multi icebergs context (one level only) (#395)

### Breaking changes

#### Introduce new vlan format

VLAN format now comply with the base Ansible nmcli module.

* **vlan_id** is replaced by **vlanid**
* **physical_interface** when defining a vlan is replaced by **vlandev**

## 1.3.0 - 2020-08-31

### Major changes

#### New roles

  - core/access_control: allow to enforce SELinux configuration
  - core/bluebanquise: install BlueBanquise requiremens on Ansible controller
  - core/firewall: allow to configure the firewall service
  - advanced-core/advanced_dns_server: provide DNS master/slave configuration
  - addons/powerman: configure [powerman](https://github.com/chaos/powerman)
  - addons/root_password: allow to update the root password at scale
  - addons/sssd: provide basic SSSD configuration to connect to an LDAP client

#### Roles improvement

  - core/dhcp_server:
    - set default lease times
    - add support of multiple DNS servers
    - add service to firewall configuration
  - core/dns_client:
    - add support of multiple DNS servers
  - core/dns_server:
    - update serial in SOA after any change to the DNS map
    - add service to firewall configuration
  - core/nfs_server:
    - add service to firewall configuration
  - core/nic:
    - fix VLAN and BOND support
  - core/pxe_stack:
    - add support of major distribution version in repository path
    - add support of $basearch variable (dnf/yum)
    - add status to bootset command (-s)
    - get the kickstart file from bootset command (-k)
    - add services to firewall configuration
  - core/repositories_client:
    - add support of major distribution version in repository path
    - add support of $basearch variable (dnf/yum)
    - add support for excluding packages from CentOS and RHEL repositories
  - core/repositories_server:
    - add service to firewall configuration
  - core/time:
    - add iburst to allow faster boot time recovery
    - add service to firewall configuration
  - advanced-core/advanced_dhcp_server:
    - add support of multiple DNS servers
    - add service to firewall configuration
  - addons/diskless:
    - add option to update existing images interactively
    - add option to remove existing images
    - add support for SELinux in Livenet images
    - add SSH public key injection in Livenet images
  - addons/users_basic:
    - merge add and remove actions

#### Internal Jinja2 variables move to a dedicated inventory

BlueBanquise implements some core logic with internal Jinja2 variables (j2_*)
that allow to compute data from the user inventory. Previously, those j2
variables were defined in the inventory examples and each user was responsible
to keep them in sync with its own inventory when a new release was made
available.

Starting with BlueBanquise 1.3, those j2 variables are now defined in a
dedicated inventory at the root of the project (directory ./internal/). (#269)

The ansible.cfg file is updated accordingly:

  ```
  inventory      = inventory,internal
  ```

With this change you will need to make the following changes:

Remove the following files from inventory/group_vars/all/j2_variables/ :

  - accelerated_mode.yml
  - equipment.yml
  - icebergs.yml
  - network.yml
  - README.md

Once deleted, you can then move the configuration file
inventory/group_vars/all/j2_variables/internal_variables.yml to
inventory/group_vars/all/general_settings/.

Now delete inventory/group_vars/all/j2_variables/.

### Breaking changes

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

#### Rename the group_vars/all/all_equipments directory

The `group_vars/all/all_equipments` directory is renamed
`group_vars/all/equipment_all`.

Use the commands below to convert existing inventories:

  ```
  # git mv inventory/group_vars/all/all_equipments inventory/group_vars/all/equipment_all
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
  inventory/group_vars/equipment_*/equipment_profile.yml

  # sed -i -e 's/^authentication:$/---/' \
             -e 's/^  //' \
             -e 's/^\([a-z]\)/authentication_\1/' \
  inventory/group_vars/all/equipment_all/authentication.yml \
  inventory/group_vars/equipment_*/authentication.yml
  ```

Note: Do not run the sed commands more than once.

#### access_control is not a boolean anymore

Note: The new name of *access_control* is *ep_access_control*.

For SELinux, the supported values are: **enforcing**, **permissive**, or
**disabled**.

Example:
  ```
  ep_access_control: enforcing  # SELinux: enforcing, permissive, disabled
  ```

### Deprecation notice

 - Variable `external_repositories` is deprecated and will be removed in a
   future release. Update your inventory to use `repositories` instead. (#270)
 - Jinja2 macros defined in roles/macros/ will be removed in a future release.
