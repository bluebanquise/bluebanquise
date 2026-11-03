======
Groups
======

Groups are what make an inventory pleasant to maintain: settings are given once to a group, and all
its members get them. A thousand identical compute hosts are then described as easily as one.

Every host belongs to three mandatory kinds of groups, and can belong to as many custom groups as you like.

Reserved groups and prefixes
============================

The following prefixes are reserved (``.*`` means "anything"):

- ``fn_.*``: **function groups**, what the host does (``fn_compute``, ``fn_login``...). Each host
  belongs to exactly one function group. Playbooks usually target these groups.

  - ``fn_management`` is special: it must contain the management hosts, as the stack relies on it.

- ``hw_.*``: **hardware groups**, what the host is (``hw_supermicro_X13QEH``...). Each host belongs to
  exactly one hardware group, holding the ``hw_`` variables (see :doc:`hardware_settings`).
- ``os_.*``: **operating system groups**, what the host runs (``os_rhel_10``, ``os_ubuntu_24``...).
  Each host belongs to exactly one OS group, holding the ``os_`` variables (see :doc:`os_settings`).

The combination of a hardware group and an OS group is an **equipment profile**: all hosts sharing
both are deployed the same way (see :doc:`../introduction/vocabulary`).

.. warning::

  ``hw_`` and ``os_`` prefixed variables must **only** be set in hardware or OS groups (or in
  ``group_vars/all``), **never** for a single host or in another group. For example, you cannot set
  ``hw_console`` for a single host in its host variables: all hosts of an equipment profile are
  expected to share the same values, and some roles rely on it. If a host really needs different
  values, give it its own hardware or OS group.

  Other variables (role settings, for example) can be set in any group, including hardware and OS
  groups when they are related to the hardware or the operating system.

Create a custom group
=====================

Custom groups are handy to gather hosts sharing some settings, or to target them in a playbook or
with ``--limit``: a rack, a project, the hosts of a building...

To create a group, add it in an INI file inside the ``cluster/`` folder of the inventory. It can be a
single file for all groups, or several files:

.. code-block:: ini

  [rack1]
  c00[1:9]
  c010

  [gpu_project]
  g001
  g002

Ranges like ``c00[1:9]`` (Ansible syntax, with a colon) avoid listing hosts one by one. A host can be
in as many groups as needed. Then, settings go in ``group_vars/<group>/``, as for any group.

.. note::

  Group names may only contain letters, digits and underscores.
