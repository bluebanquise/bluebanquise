Xfs_quota
------

Description
^^^^^^^^^^^

Used to set default user and group disk quotas on xfs disk used by server.


**There are 3 types of quotas:**

- user
- group
- *project Not implemented*




This role provides simply an interface to `**xfs_quota** Ansible module <https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html>`_

**Observation**
^^^^^^^^^^^^^^^

For this role to work, the filesystem mount configurations must have the options uquota, gquota, pquota .

Example 

.. code-block:: text

  /dev/xvdb1 /xfs xfs rw,quota,gquota,pquota 0 0

Instructions
^^^^^^^^^^^^
Set mountpoint for user and group default values in quota_filesystem

Set specific values for user and groups outside the default scope in quota_spec



.. code-block:: yaml

   xfs_quota:
    - type: user
      name: nobody 
      mountpoint: /exports/nfs
      bsoft: 5G
      bhard: 6G
    
    - type: group
      name: nobody
      mountpoint: /exports/nfs
      bsoft: 5G
      bhard: 6G


See `**xfs_quota** Ansible module page <https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html>`_ for the full list of available parameters.

Changelog
^^^^^^^^^
* 1.0.0: Role Creation. Alisson Zuza <alisson.zuza1987@gmail.com>
