Variables description
=====================

Reserved groups and prefixs
---------------------------

The following groups are reserved (``xxxx`` means "everything else"):

- ``fn_xxxx``: these groups are function groups. Variables stored in these groups should start with the specific ``fn_`` prefix.
    - ``fn_management``: this group should contain all manager/controler nodes.
- ``hw_xxxx``: these groups are hardware groups. Variables stored in these groups should start with the ``hw_`` prefix.
- ``os_xxxx``: these groups are operating system groups. Variables stored in these groups should start with the ``os_`` prefix.

The following variables are reserved:

- ``bb_xxxx``: these variables are transverse variables, meaning these can be used by multiple roles and should precedence roles' default variables.
- ``j2_xxxx``: these variables are logic variables, meaning these contain Jinja2 code.

Note also that each role's variables are prefixed by the role name.

.. image:: images/misc/warning.svg
   :align: center
|
.. warning::
  **IMPORTANT**: ``hw_`` and ``os_`` variables **are
  not standard**. You should **NEVER** set them outside hardware or os groups.
  For example, you cannot set the ``hw_console`` parameter for a single node under it's hostvars.
  If you really need to do that, add more hardware or os groups. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.

Global settings
---------------

- **bb_cluster_name**: define cluster name. Default: ``bluebanquise``
- **bb_domain_name**: define cluster domain name. Default: ``cluster.local``
- **bb_time_zone**: define cluster time zone. Default: ``Europe/Brussels``

Host settings
-------------

Network settings
----------------

Hardware settings
-----------------

OS settings
-----------

Kernel
------

Repositories
------------

File ``group_vars/all/repositories.yml`` configure repositories to
use for all nodes (using groups and variable precedence, repositories can be
tuned for each group of nodes, or even each node).

It is important to set correct repositories to avoid issues during deployments.

There are 2 ways to define a repository.
Either specifying a full URL and parameters of the repository,
or using the stack automatic mechanism (which involves your organized repositories as expected by the stack).

Full definition
^^^^^^^^^^^^^^^

* RHEL like system:

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

* Ubuntu or Debian like systems:

.. raw:: html

  <div style="padding: 6px;">
  <b>Ubuntu</b> <img src="_static/logo_ubuntu.png">, <b>Debian</b> <img src="_static/logo_debian.png">
  </div><br><br>

.. code-block:: yaml

  repositories:
    - repo: deb http://my-server/repositories/ubuntu22/ stable main
      state: present

Stack should support all available parameters listed in `the Ansible apt_repository_module. <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_repository_module.html>`_

* Suse like system:

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

