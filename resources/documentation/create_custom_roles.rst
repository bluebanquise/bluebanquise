Creating Custom Role
====================

Working Environment
-------------------

Write your own Ansible roles in **/etc/bluebanquise/roles/customs/** path.
The other paths are reserved for BlueBanquise, Atos and SMC roles.

Initialize your Environment
---------------------------

.. code-block:: shell

 cd /etc/bluebanquise/roles/customs/
 ansible-galaxy init my_custom_role
 - Role my_custom_role was created successfully
 
 tree
 .
 ├── defaults
 │   └── main.yml
 ├── files
 ├── handlers
 │   └── main.yml
 ├── meta
 │   └── main.yml
 ├── README.md
 ├── tasks
 │   └── main.yml
 ├── templates
 ├── tests
 │   ├── inventory
 │   └── test.yml
 └── vars
     └── main.yml
 
 8 directories, 8 files


**Description:**

By default Ansible will look in each directory within a role for a main.yml file for relevant content (also main.yaml and main):

- defaults/main.yml: default variables for the role. These variables have the lowest priority of any variables available, and can be easily overridden by any other variable, including inventory variables.
- files/main.yml: files that the role deploys.
- handlers/main.yml: handlers, which may be used within or outside this role.
- meta/main.yml: metadata for the role, including role dependencies.
- README.md: A brief description of the role.
- tasks/main.yml: the main list of tasks that the role executes.
- templates/main.yml: templates that the role deploys.
- tests/test.yml: automatic test description file.
- vars/main.yml: other variables for the role.

Writing Custom Role
-------------------

