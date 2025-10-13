======
Groups
======

Since the stack is based on Ansible, it is possible to create custom logical groups of nodes to organize your inventory.
Just be sure not to use reserved names.

Reserved groups and prefixs
---------------------------

The following groups are reserved (``.*`` means "everything else", it is a regex):

- ``fn_.*``: these groups are function groups. Variables stored in these groups should start with the specific ``fn_`` prefix.
    - ``fn_management``: this group should contain all manager/controler nodes.
- ``hw_.*``: these groups are hardware groups. Variables stored in these groups should start with the ``hw_`` prefix.
- ``os_.*``: these groups are operating system groups. Variables stored in these groups should start with the ``os_`` prefix.

.. warning::
  **IMPORTANT**: ``hw_`` and ``os_`` variables **are
  not standard**. You should **NEVER** set them outside hardware or os groups.
  For example, you cannot set the ``hw_console`` parameter for a single node under it's hostvars.
  If you really need to do that, add more hardware or os groups. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.

  Note however that these variables can be used at ``group_vars/all`` level.

Create a custom group
---------------------

To create a new group, simply add the group in an INI file inside ``cluster/`` folder of the inventory.
This can be a single file for all groups, or multiple files.

Syntax is the following:

.. code-block:: ini

  [my_group_name]
  my_node1
  my_node2

  [my_other_group_name]
  my_node1
  my_node3

A node can be in multiple groups.
