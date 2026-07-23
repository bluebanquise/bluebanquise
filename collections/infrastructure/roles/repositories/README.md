# Repositories

## Description

These settings simply configure repositories for client hosts.

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

You can also specify the variable repositories_network when executing these settings.
For example: 

```yaml
- role: bluebanquise.infrastructure.repositories
  vars:
    repositories_network: "net-other-network"
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

### Full definition (explicit URL)

Instead of relying on the automatic URL mechanism, repositories can be fully defined with an explicit URL and all parameters supported by the underlying Ansible module.

**RHEL / AlmaLinux / Rocky / Oracle / CentOS:**

```yaml
bb_repositories:
  - name: os_base
    baseurl: http://my-server/repositories/el9/x86_64/os/
    enabled: 1
    state: present
```

All parameters from the [yum_repository module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yum_repository_module.html) are supported.

**Ubuntu / Debian:**

```yaml
bb_repositories:
  - repo: deb http://my-server/repositories/ubuntu/24.04/x86_64/os/ noble main
    state: present
```

All parameters from the [apt_repository module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_repository_module.html) are supported.

**OpenSuse Leap:**

```yaml
bb_repositories:
  - name: base
    baseurl: http://my-server/repositories/leap/16/x86_64/os/
    enabled: 1
    state: present
```

All parameters from the [zypper_repository module](https://docs.ansible.com/ansible/latest/collections/community/general/zypper_repository_module.html) are supported.

### Remove native repositories

If you wish to remove native OS repositories, to rely only on local ones (air gapped cluster for example), you need to use the pxe_stack role of the collection. (These settings do not support removing repositories for now.)

Simply define:

```yaml
pxe_stack_preserve_repositories: false
```

And native repositories will be removed during hosts deployment (PXE install, not playbook execution).
