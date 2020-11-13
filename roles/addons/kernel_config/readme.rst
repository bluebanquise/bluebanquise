kernel_config
-------------

Description
^^^^^^^^^^^

This role apply/update kernel parameters and sysctl parameters.

Instructions
^^^^^^^^^^^^

kernel parameters
"""""""""""""""""

The role uses 2 sources for kernel parameters:

1. *ep_kernel_parameters* from core stack, which is a string
2. *kernel_config_parameters*, which is an optional list

An example for *kernel_config_parameters* would be:

.. code-block:: yaml

  kernel_config_parameters:
    - rd.blacklist=mpt3sas
    - ipv6.disable=1
    - nopti
    ...

Role gather both and ensure all parameters set in these variables 
are set for the current default kernel.

sysctl
""""""

Sysctl parameters to be set are defined in the *kernel_config_sysctl* 
variable. An example would be:

.. code-block:: yaml

  kernel_config_sysctl:
    kernel.panic: absent
    vm.swappiness: 5
    ...

It is optionally possible to prevent sysctl reload by 
setting variable *kernel_config_sysctl_reload* to **false**. 

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* ep_kernel_parameters

Optional inventory vars:

**hostvars[inventory_hostname]**

* kernel_config_sysctl
* kernel_config_sysctl_reload
* kernel_config_parameters

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
