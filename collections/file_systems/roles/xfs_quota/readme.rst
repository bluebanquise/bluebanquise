Xfs_quota
----------

Description
^^^^^^^^^^^

Used to set default user and group disk quotas on xfs disk used by server.

There are 3 types of quotas:
- user
- group
- proiject not implemented

This is defined at the mount point in this case we are only using user and group.

This role provides simply provides an interface to `**xfs_quota** Ansible module <https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html>`_


- How to define variables

To define the variables, enter the folder of the node in question in 
"inventory/group_vars/equipment_type*", and use the examples below

Type of variables

type  - user , group  
mount - mount point
soft  - minimum value for quota
hard  - maximum value for quota
quota_filesystem - Filesystems for default rule of users
or groups that are not specified

- First task - Set defaults for user quotas

If the variables below are not defined in the inventory, 
these values will be the defaults of all filesystems defined in the variable
"quota_filesystems_default"

user_quotas_default_soft: 5G
user_quotas_default_hard: 6G
group_quotas_default_soft: 5G
group_quotas_default_hard: 6G


- Second task - Set defaults for group quotas
If the variables below are not defined in the inventory, these values
will be the defaults of all filesystems defined in the variable 
"quota_filesystem"

user_quotas_default_soft: 5G
user_quotas_default_hard: 6G
group_quotas_default_soft: 5G
group_quotas_default_hard: 6G


- Trird task - Set specific quotas for users or groups

Third task defines specific users and groups with their required mount points and 
dimension values.


.. code-block:: yaml
  quota_filesystem:
   -name: FS1
    mountpoint: XXXXXX

   -name: FS2
    mountpoint: XXXXXX
    
  quotas_spec:
   - type: user
     name: nobody
     mountpoint: XXXXXX
     bsoft:5G
     hard:6G
  
  - type: group
    name: nobody
    mountpoint: YYYYYY
    soft: 5G
    hard: 6G



 See `**xfs_quota** Ansible module page <https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html>`_
 for the full list of available parameters.

