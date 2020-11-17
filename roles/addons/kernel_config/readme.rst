kernel_config
-------------

Description
^^^^^^^^^^^

This role apply/update kernel parameters and sysctl parameters.

Instructions
^^^^^^^^^^^^

kernel parameters
"""""""""""""""""

The role uses the *ep_kernel_parameters* as source. 

sysctl
""""""

Sysctl parameters to be set are defined in the *ep_sysctl* 
variable. As it is an *ep_* variable, it should only be 
set for each equipment profiles, and not set at hostvars 
level.

An example would be:

.. code-block:: yaml

  ep_sysctl:
    kernel.panic: absent
    vm.swappiness: 5
    ...

It is optionally possible to prevent sysctl reload by 
setting variable *kernel_config_sysctl_reload* to **false**. 

Input
^^^^^

Optional inventory vars:

**hostvars[inventory_hostname]**

* ep_kernel_parameters
* kernel_config_sysctl_reload

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
