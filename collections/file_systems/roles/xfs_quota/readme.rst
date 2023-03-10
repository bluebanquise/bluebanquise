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



Instructions
^^^^^^^^^^^^
Set mountpoint for user and group default values in quota_filesystem

Set specific values for user and groups outside the default scope in quota_spec



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

