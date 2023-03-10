Xfs_quota
----------

Description
^^^^^^^^^^^

Used to set default user and group disk quotas on xfs disk used by server.


**There are 3 types of quotas:**

- user
- group
- *project Not implemented*




This role provides simply provides an interface to `**xfs_quota** Ansible module <https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html>`_


**How to define variables**

To define the variables, enter the folder of the node in question in "inventory/group_vars/equipment_type*", and use the examples below




.. code-block:: yaml

   quota_filesystem:
    -name: FS1
     mountpoint: XXXXXX

    -name: FS2
     mountpoint: XXXXXX

   quotas_spec:
    - type: user
      name: nobody 
      mount: /exposts/nfs
      soft: 5G
      hard: 6G
    
    - type: group
      name: nobody
      mount: /exports/nfs
      soft: 5G
      hard: 6G



See `**xfs_quota** Ansible module page <https://docs.ansible.com/ansible/latest/collections/community/general/xfs_quota_module.html>`_ for the full list of available parameters.

