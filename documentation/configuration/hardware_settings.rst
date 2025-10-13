=================
Hardware settings
=================

.. warning::
  **IMPORTANT**: ``hw_`` and ``os_`` variables **are
  not standard**. You should **NEVER** set them outside hardware or os groups.
  For example, you cannot set the ``hw_console`` parameter for a single node under it's hostvars.
  If you really need to do that, add more hardware or os groups. If you do not respect this
  rule, unexpected behavior will happen during configuration deployment.

  Note however that these variables can be used at ``group_vars/all`` level.

Once an hardware group has been defined into ``cluster/`` folder, you can create a group's dedicated folder
inside ``group_vars/`` directory. The folder name must match the group name. For example, for group
``hw_supermicro_X13QEH``, directory path will be ``group_vars/hw_supermicro_X13QEH``.

Once this directory has been created you can configure the hardware settings of this group.
Create a file named ``settings.yml`` inside the group folder, and then see bellow for available parameters.

Equipment type
==============

**This key is very important**, as it will enable or not specific features in some stack's roles.

Use ``hw_equipment_type`` key to set the type of the equipment. For example ``server`` or ``switch``, etc.

Please note that ``server`` value is the value that triggers PXE, conman, etc for a node. Each server node to be deployed via PXE should be of type ``server``.
You can set other types namings according to your wishes (``switch``, ``switches``, ``storage_bay_controller``, whatever).

For example:

.. code-block:: yaml

  hw_equipment_type: server

Hardware componants
===================

You can define the node components using the ``hw_specs`` key.

These values will be used by some roles of the stack to generate their configuration.

.. code-block:: yaml

  hw_specs:
    cpu:
      name: Intel 6416H
      cores: 144
      cores_per_socket: 18
      sockets: 4
      threads_per_core: 2
    gpu:
      - NVIDIA A100-SXM4-40GB

Note that gpu key is a list of GPU, while cpu key is a dict that defines specific CPU keys:

* ``cores``: total number of cores on the system (virtual ones included)
* ``cores_per_socket``: total number of cores per CPU
* ``sockets``: total number of sockets on the motherboard
* ``threads_per_core``: total number of threads per core (HyperThreading)

In normal time: ``cores = threads_per_core*cores_per_socket*sockets``.

If needed, you can define the board CPU architecture using the dedicated ``hw_architecture`` key.
Possible values are either ``x86_64`` or ``aarch64``.

.. code-block:: yaml

  hw_architecture: aarch64

Console
=======

If the hardware group refer to servers, a console can be enabled using ``hw_console`` key.

For example:

.. code-block:: yaml

  hw_console: console=tty0 console=ttyS1,115200

Please note that the console can be obtained from your server manufacturer/vendor.
If they don't know it, try ttyS0, then ttyS1, then ttyS2. Its nearly always one of these.

Hardware authentication
=======================

On most server systems, a BMC or equivalent allows to remotely manage the equipment.
However, in order to use it, a specific protocol and credentials are needed.

The hw_board_authentication key allows to define a list of ways to authenticate with the equipments of the group.

Reserved keys are: protocol, user, and password. Other keys can be added if relevant and if an external role to use them is provided.

.. code-block:: yaml

  hw_board_authentication:
    - protocol: IPMI
      user: ADMIN
      password: ADMIN

Note that on some board, both IPMI and RedFish can be activated at the same time, which is the reason why this is a list.
