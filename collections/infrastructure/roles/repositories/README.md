# Repositories

## Description

This role simply configure repositories for client hosts.

## Instructions

### Define repositories

Repositories are set in **bb_repositories** variable. Two shapes are available: a
simple one and an advanced one.

Simple one:

```yaml
bb_repositories:
  - os
  - bluebanquise
  - myrepo
```

Advanced one, to be combined with simple one as desired:

```yaml
bb_repositories:
  - os
  - bluebanquise
  - name: epel
    baseurl: 'https://dl.fedoraproject.org/pub/epel/$releasever/$basearch/'
    proxy: 'https://proxy:8080'
```

Available advanced variables depends of the target OS. Please refer to the following pages to know available parameters:

* RHEL: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yum_repository_module.html
* Debian or Ubuntu: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_repository_module.html
* Suse: https://docs.ansible.com/ansible/latest/collections/community/general/zypper_repository_module.html

When using simple format, repository static URL path is computed using variables defined in the equipment group and in networks.
The following variables are mandatory for this feature to work properly:

**Network**:

```yaml
networks:
  net-my-network:
    services_ip: 10.10.0.1
```

Or 

```yaml
networks:
  net-my-network:
    services:
      repositories:
        - ip4: 10.10.0.1
          hostname: my-repository-server
```

**Equipment variables:**

```yaml
os_operating_system:
  distribution: redhat # centos, redhat, debian, ubuntu, opensuse, etc.
  distribution_major_version: 8
  # Optional: define a minor distribution version to force (repositories/PXE)
  #distribution_version: 8.0
  # Optional: add an environment in the repositories path (eg. production, staging) (repositories/PXE)
  #repositories_environment: production
```

For example, if equipment_profile is:

```yaml
os_operating_system:
  distribution: centos
  distribution_major_version: 8
```

Then path will be: repositories/centos/8/$basearch/

If equipment_profile is:

```yaml
os_operating_system:
  distribution: centos
  distribution_major_version: 8
  distribution_version: 8.1
```

Then path will be: repositories/centos/8.1/$basearch/

If equipment_profile is:

```yaml
os_operating_system:
  distribution: centos
  distribution_major_version: 8
  distribution_version: 8.1
  repositories_environment: production
```

Then path will be: repositories/production/centos/8.1/$basearch/

### Remove native repositories

If you wish to remove native OS repositories, to rely only on local ones (air gapped cluster for example), you need to use the pxe_stack role of the collection. (This role does not support removing repositories for now.)

Simply define:

```yaml
pxe_stack_preserve_repositories: false
```

And native repositories will be removed during nodes deployment (PXE install, not playbook execution).

## Changelog

* 1.3.8: Set default network and handle RedHat os. Jean-pascal Mazzilli <jp.mazzilli@gmail.com>
* 1.3.7: Fix services ip precedence. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.6: Fix extra space in automatic url. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.5: Adapt role to support BB 2.0 networks. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.4: Update to BB 2.0 format. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.3.3: Support gpgkey for Ubuntu. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.3.2: Flush handlers at the end of role repositories_client. #sla31
* 1.3.1: Updated SUSE subtask to handle missing repo definition when repo is a dictionary. Neil Munday <neil@mundayweb.com>
* 1.3.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Add OpenSuSE support and correct ansible warning for included tasks loop. Neil Munday <neil@mundayweb.com>
* 1.1.3: Improve Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.2: Incorporated fix for issue 534. Neil Munday <neil@mundayweb.com>
* 1.1.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.8: Add state parameter. Bruno Travouillon <devel@travouillon.fr>
* 1.0.7: Simplified version of the role. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Deprecate external_repositories. Bruno Travouillon <devel@travouillon.fr>
* 1.0.5: Added support for excluding packages from CentOS and RHEL repositories. Neil Munday <neil@mundayweb.com>
* 1.0.4: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.3: Add support of major release version. Bruno <devel@travouillon.fr>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
