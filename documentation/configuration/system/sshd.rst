====
SSHD
====

Open SSH server (also known as SSHD) configuration allows to secure the users access to nodes.

A good strategy is to prevent users to login on nodes they don't need to,
and avoid having a node capable of ssh on all other nodes (except your management node, or better a push node, that would not be the management node).

The BlueBanquise role will simply create a configuration file in the sshd include dir, so that this configuration is loaded first and precedence default settings.

.. note::

  To prevent any access issues, by default all variables of this role are empty, and so without configuration set, this role will do nothing.

Disable passwords
=================

It is advised to prevent password usages.

To do so, set ``sshd_PasswordAuthentication`` to **no**:

.. code-block:: yaml

  sshd_PasswordAuthentication: no

Disable root access
===================

It is advised to prevent root ssh access.

To do so, set ``sshd_PermitRootLogin`` to **no**:

.. code-block:: yaml

  sshd_PermitRootLogin: no

Users access
============

It is possible to restrict access to specific users.

Variables ``sshd_DenyUsers``, ``sshd_AllowUsers``, ``sshd_DenyGroups``, ``sshd_AllowGroups`` are available.
Note that openssh server daemon will use these variables in **this exact order** to determine if a user can or not access,
and first occurence found will precedence everything else.

.. note:: 

  Remember that to push configuration, you need to let the bluebanquise user connect through ssh.
  You might not need any other users being able to use ssh on most nodes, so restricting access to only the bluebanquise user
  on most nodes would make sens.

Example:

.. code-block:: yaml

    sshd_DenyUsers:
    sshd_AllowUsers: bluebanquise anotheruser
    sshd_DenyGroups:
    sshd_AllowGroups:

Other settings
==============

You can add any other openssh server settings using the ``sshd_raw`` variable.
This is a multi lines variables.

Example:

.. code-block:: yaml

  sshd_raw: |
    X11Forwarding no
    PermitTunnel no
