Node Health Checker
-------------------

Description
^^^^^^^^^^^

This role install and configure NHC.

Instructions
^^^^^^^^^^^^

To set checks, simply create variable **nhc_checks** and provide all checks with
check name as key and arguments of this check as value. For example:

.. code-block:: yaml

  nhc_checks:
    check_hw_mem_free: 1mb
    check_fs_mount_rw: -f /scratch
    ...

If you need to define multiple time the same check, but with different arguments,
simply provide a list of arguments:

.. code-block:: yaml

  nhc_checks:
    check_hw_mem_free: 1mb
    check_fs_mount_rw:
      - -f /scratch
      - -f /home
    ...

You can force usage of a static file instead of a generated one by setting
**nhc_use_template** to *false*. In this mode, the role will by default look for
a file called *nhc.conf* in files folder of the role, and copy it to
*/etc/nhc/nhc.conf* on target host.
It is possible to force copy of multiple nhc files by setting variable
*nhc_files* as a list of files names that should be copied from files folder of
the role to */etc/nhc* on the target host.

For example:

.. code-block:: yaml

  nhc_files:
    - nhc.conf
    - my_custom_check.nhc

You can require installation of additional custom packages (for example
smartmontools, dmidecode, etc), by providing a list named
**nhc_custom_packages_to_install**. This can be useful when using custom nhc
checks.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
