Cloning
-------

Description
^^^^^^^^^^^

This role provides ipxe files for Clonezilla live usage.

Instructions
^^^^^^^^^^^^

The Clonezilla Live iso is needed for this role to run properly. The following iso version was used for validating this role: **clonezilla-live-20191024-eoan-amd64.iso**

The iso must be mounted in the *preboot_execution_environment/clone/clonezilla* folder or the content copied inside this directory.

Call bootset using -b clone -i myimage to clone a node into myimage, and -b deploy_clone -i myimage to deploy myimage on the target node.

By default, sda device is targeted, and clone parameters are:

.. code-block:: text

    ocs-sr -q2 -batch -j2 -z1 -i 2096 -fsck-src-part-y -senc -p reboot savedisk myimage.img sda

It is possible to force other clone parameters by setting extra-parameters during bootset invocation. For example, to clone sdb disk, use:

.. code-block:: text

    bootset -n mynode -i myimage -b clone -e "ocs-sr -q2 -batch -j2 -z1 -i 2096 -fsck-src-part-y -senc -p reboot savedisk myimage.img sdb"

Refer to clonezilla live documentation about other parameters.

Same apply to deploy clone. By Default, sda is targeted, and restore clone parameters are:

.. code-block:: text

    ocs-sr -g auto -e1 auto -e2 -r -j2 -batch -p reboot restoredisk myimage.img sda

It is possible to replace these parameters using extra parameters when invoking bootset.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
