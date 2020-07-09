Repositories client
-------------------

Description
^^^^^^^^^^^

This role simply configure repositories for client hosts.

Instructions
^^^^^^^^^^^^

See repositories_server role instructions for general repositories path details.

Repositories are set in **repositories** variable. Two shapes are available: a
simple one and an advanced one.

Simple one:

.. code-block:: yaml

  repositories:
    - os
    - bluebanquise
    - myrepo

Advanced one, to be combined with simple one as desired:

.. code-block:: yaml

  repositories:
    - os
    - bluebanquise
    - name: epel
      baseurl: 'https://dl.fedoraproject.org/pub/epel/$releasever/$basearch/'
      proxy: 'https://proxy:8080'

Available advanced variables are:

* name
* baseurl
* enabled
* exclude
* gpgcheck
* gpgkey
* proxy

Repository static path is computed using variables defined in the equipment_profile.

.. code-block:: yaml

  operating_system:
    distribution: centos # centos, redhat, debian, ubuntu, opensuse, etc.
    distribution_major_version: 8
    # Define a minor distribution version to use for pxe_stack
    #distribution_version: 8.0
    # Overwrite the default $releasever on the target
    #repositories_releasever: 8.0
    # Add the $environment in the repositories path (eg. production, staging)
    #repositories_environment: production

It is assumed here that equipment_profile.hardware.cpu.architecture is x86_64.

If equipment_profile is:

  operating_system:
    distribution: centos # centos, redhat, debian, ubuntu, opensuse, etc.
    distribution_major_version: 8

Then path will be: repositories/centos/8/x86_64/

If equipment_profile is:

  operating_system:
    distribution: centos # centos, redhat, debian, ubuntu, opensuse, etc.
    distribution_major_version: 8
    repositories_releasever: 8.1

Then path will be: repositories/centos/8.1/x86_64/

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* repositories[item]

Output
^^^^^^

Repositories are set.

To be done
^^^^^^^^^^

Need to clear up the Ubuntu repositories process, still not clear how to handle
own made repos and officials repos as Ubuntu add local repos everywhere in the
sources.list file.

Changelog
^^^^^^^^^

* 1.0.7: Simplified version of the role. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Deprecate external_repositories. Bruno Travouillon <devel@travouillon.fr>
* 1.0.5: Added support for excluding packages from CentOS and RHEL repositories. Neil Munday <neil@mundayweb.com>
* 1.0.4: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.0.3: Add support of major release version. Bruno <devel@travouillon.fr>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
