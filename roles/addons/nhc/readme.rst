Node Health Checker
-------------------

Description
^^^^^^^^^^^

This role install and configure NHC.

To find more information on NHC or grab latest release, refer to `project github <https://github.com/mej/nhc>`_

Instructions
^^^^^^^^^^^^

General usage
"""""""""""""

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

You can force usage of a static file content instead of a generated one by 
setting **nhc_static_configuration** into inventory.
**nhc_static_configuration** is a multi lines variable that should contain 
the full desired content of the target nhc.conf file.

For example:

  nhc_static_configuration: |
    * || export TS=1
    * || export DEBUG=0
    * || export DF_FLAGS="-Tk"
    * || export DFI_FLAGS="-Ti"
    * || check_ps_service -u root -S sshd
    ...   

Advanced usage
""""""""""""""

It is possible to force copy of multiple nhc files (custom checks, scripts, etc) 
by setting variable *nhc_files* as a list of files names that should be copied 
from files folder of the role to */etc/nhc* to the target host.

For example:

.. code-block:: yaml

  nhc_files:
    - my_custom_check.nhc

You can require installation of additional custom packages (for example
smartmontools, dmidecode, etc), by providing a list named
**nhc_custom_packages_to_install**. This can be useful when using custom nhc
checks.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
