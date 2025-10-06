============
Repositories
============

File ``group_vars/all/repositories.yml`` configure repositories to
use for all nodes.
Repositories are listed inside this file under ``repositories`` key.

.. note::

  Using groups and variable precedence, repositories can be
  tuned for each group of nodes, or even each node. This is very useful if for example
  you only wish to enable a specific repository on a single group of nodes.
  To do so, just redefine the repositories inside the group folder (``group_vars/hw_supermicro_with_gpu/repositories.yml`` for example),
  and this new definition will precedence the global one for this group of nodes

There are 2 ways to define a repository.
Either using the stack automatic mechanism (which involves you organized repositories as expected by the stack but benefit of some integrated features)
or by specifying a full definition with URL and parameters of the repository.

Automatic mechanism
===================

It is possible to just define repositories with their name,
configure the target server in networks settings, and the stack will automatically bind nodes to it.

For developers, logic is the following (I split the line into 2 parts to make it human readble):

.. code-block:: jinja2

  http://{{
    networks[repositories_network | default(j2_node_main_network, true)]['services']['repositories'][0]['hostname'], true | 
    default(networks[repositories_network | default(j2_node_main_network, true)]['services']['repositories'][0]['ip4'], true) | 
    default(networks[repositories_network | default(j2_node_main_network, true)]['services_ip'], true) |
    default('', true) }}
  /repositories/
    {{ os_operating_system['repositories_environment'] | default('', true) }}/
    {{ os_operating_system['distribution'] | default('', true) }}/
    {{ os_operating_system['distribution_version'] | default(os_operating_system['distribution_major_version']) | default('', true)}}/
    {{ ansible_architecture }}/

Define repository server in networks
------------------------------------

In your management network, you can either use ``services_ip`` key to share the server with other services,
or define it under ``services:repositories`` as a list.
Note that:

1. Currently, only the first hostname or ip4 of the list will be used.
2. When both hostname and ip4 are defined, hostname precedence ip4.
3. When both ``services_ip`` and ``services:repositories`` are defined, ``services:repositories`` will precedence ``services_ip``.

Examples:

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services:
        repositories:
          - hostname: mgt1
            ip4: 10.10.0.1

Will result in server ``mgt1`` for repositories.

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services:
        repositories:
          - ip4: 10.10.0.1

Will result in server ``10.10.0.1`` for repositories.

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.2
      services:
        repositories:
          - hostname: mgt1
            ip4: 10.10.0.1

Will result in server ``mgt1`` for repositories.

.. code-block:: yaml

  networks:
    net-admin:
      subnet: 10.10.0.0
      prefix: 16
      services_ip: 10.10.0.2
      services:

Will result in server ``10.10.0.2`` for repositories.

Then, simply set the repository with its expected name inside ``group_vars/all/repositories.yml`` file:

.. code-block:: yaml

  repositories:
    - name: myrepo

You can also set multiple repositories:

.. code-block:: yaml

  repositories:
    - name: os
    - name: nvidia-cuda

Create repositories on server
-----------------------------

On the repositories server node, you will need to create a folder for each repository, using this structure:

.. code-block:: bash

                  Distribution    Version   Architecture    Repository name
                        +             +       +               +
                        |             +--+    |               |
                        +-----------+    |    |    +----------+
                                    |    |    |    |
                                    v    v    v    v
       /var/www/html/repositories/redhat/8/x86_64/myrepo/

.. note::

  When using OpenSuse Leap, path is not ``/var/www/html`` but ``/srv/www/htdocs``.

Distribution and version to be used are defined in os groups, for example:

.. code-block:: yaml

  os_operating_system:
    distribution: ubuntu
    distribution_version: 24.04
    distribution_major_version: 24

Will result in /var/www/html/repositories/ubuntu/24.04/x86_64/myrepo being used (or /var/www/html/repositories/ubuntu/24.04/aarch64/myrepo on an aarch64 system).

If only major version is set, it will be used instead:

.. code-block:: yaml

  os_operating_system:
    distribution: ubuntu
    distribution_major_version: 24

Will result in /var/www/html/repositories/ubuntu/24/x86_64/myrepo

Repositories repositories
-------------------------

For convenience, you can also set a dedicated key under ``os_operating_system``, called ``repositories_environment``. This will be added inside the url path just under ``repositories/``:

.. code-block:: yaml

  os_operating_system:
    repositories_environment: production
    distribution: ubuntu
    distribution_major_version: 24

Will result in /var/www/html/repositories/production/ubuntu/24/x86_64/myrepo

Full definition
===============

RHEL like system
----------------

.. raw:: html

  <div style="padding: 6px;">
  <b>RHEL</b> <img src="_static/logo_rhel.png">, <b>CentOS</b> <img src="_static/logo_centos.png">, <b>RockyLinux</b> <img src="_static/logo_rocky.png">, <b>OracleLinux</b> <img src="_static/logo_oraclelinux.png"><br> <b>CloudLinux</b> <img src="_static/logo_cloudlinux.png">, <b>AlmaLinux</b> <img src="_static/logo_almalinux.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - name: os_base
      baseurl: http://my-server/repositories/el8/
      enabled: 1
      state: present

Stack should support all available parameters listed in `the Ansible yum_repository_module. <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yum_repository_module.html>`_

Ubuntu or Debian like systems
-----------------------------

.. raw:: html

  <div style="padding: 6px;">
  <b>Ubuntu</b> <img src="_static/logo_ubuntu.png">, <b>Debian</b> <img src="_static/logo_debian.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - repo: deb http://my-server/repositories/ubuntu22/ stable main
      state: present

Stack should support all available parameters listed in `the Ansible apt_repository_module. <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_repository_module.html>`_

Suse like system
----------------

.. raw:: html

  <div style="padding: 6px;">
  <b>Suse</b> <img src="_static/logo_suse.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - name: base
      baseurl: http://my-server/repositories/leap15/
      enabled: 1
      state: present

Stack should support all available parameters listed in `the Ansible zypper_repository_module. <https://docs.ansible.com/ansible/latest/collections/community/general/zypper_repository_module.html>`_
