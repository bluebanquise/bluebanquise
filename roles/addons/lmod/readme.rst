lmod
----

Description
^^^^^^^^^^^

This role simply install Lmod tool (https://lmod.readthedocs.io/) and 
set custom path if needed.

Instructions
^^^^^^^^^^^^

Note that Lmod is available on EPEL repository, and requires Centos PowerTools to 
to get all dependencies.

If custom path are needed, define variable lmod_path, as a list, in the inventory.

For example:

.. code-block:: yaml

  lmod_path:
    - /etc/modulefiles
    - /soft/modules

These will be added in file /etc/profile.d/modules_extra_path.sh, and so be available 
to all users. 

Optional inventory vars:

**hostvars[inventory_hostname]**

* lmod_path (list)

Output
^^^^^^

Packages installed:

* Lmod

Files generated:

* /etc/profile.d/modules_extra_path.sh (optional)

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
