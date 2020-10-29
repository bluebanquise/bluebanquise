System State
------------

Description
^^^^^^^^^^^

This role simply generate a file /etc/system_state/main.yml that 
contains context of last execution of the role.

This file can be used as a validation (checksum, diff, etc) file.

..warning::
  This role assumes all roles used in the playbook follow the 
  **role_name**_role_version vars standard of BlueBanquise.

Instructions
^^^^^^^^^^^^

Simply put this role **AT THE END** of the roles list in your playbook.
If all roles were executed without errors, then system_state will generate the file 
that validate last state executed.

Optional inventory vars:

**hostvars[inventory_hostname]**

* system_state_ansible_version
* system_state_ansible_python_version
* system_state_role_names
* system_state_ansible_inventory_sources
* system_state_ansible_run_tags
* system_state_ansible_skip_tags
* system_state_role_versions

Output
^^^^^^

Files generated:

* /etc/system_state/main.yml

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
