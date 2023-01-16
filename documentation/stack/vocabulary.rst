==========
Vocabulary
==========

Some key terms are important in **BlueBanquise**. Most of them are described here.

Ansible vocabulary
==================

Inventory
---------

An Ansible inventory is a file or a folder that contains data to be parsed by Ansible.
An inventory contains the list of hosts to be addressed, and their associated data.

You can use multiple inventories to define multiple states of the cluster,
stack them at runtime if needed, etc. Also, since inventories are
text based, it can be interesting to version them with git.

In remaining of the documentation, we will assume a single inventory for the whole cluster,
and all inventory path will be ``~/inventory/``, but you can store it anywhere.

Host
----

An **Ansible managed host** (also often referred as a **node**) is a remote host managed
by Ansible. An **Ansible managed host** can be a physical server, but also a VM, a container or
something else.

.. image:: images/hosts_example.svg
   :align: center


Hosts are defined by default in ``~/inventory/cluster/`` inventory folder.

Please do a difference between an **Ansible managed host**, and a **simple host**.
All equipment that can have an ip address on the network are considered "simple host",
but only those with an **ssh** + **python** capability and on which we will use Ansible
to deploy a configuration are considered "Ansible managed host".

Group
-----

An Ansible **group** is a logical aggregation of Ansible managed hosts.
For example, system administrator can define a group "database_servers" that
would contain nodes "database1" and "database2".

**Groups** allow Ansible to provide dedicated **variables** to group's member nodes or
execute tasks on a set of nodes.

Note: a node can be part of multiple groups.

Variables
---------

Variables in Ansible follow the YAML structure.

A variable is like in any programming language: a variable name (key), and a data
related (value).

.. raw:: html

   <br>
   <div class="tip_card">                
   <div class="tip_card_img_container"><img src="../_static/img_avatar.png" style="width:100px; border-radius: 5px 0 0 5px; float: left;" /></div>
   <div class="tip_card_title_container"><b>Tip from the penguin:</b></div>
   <div class="tip_card_content_container"><p>Ansible supports 2 input format: INI and YAML. We will focus on YAML, but consider INI as a good candidate for simple cluster.</p></div>
   </div>
   <br>

Multiple kind of variables exist in Ansible:

Simple
^^^^^^

A simple variable is defined this way:

.. code-block:: yaml

  my_variable_1: hello!
  my_variable_2: 7777

In Jinja2, the language used in Ansible templates,
variables will be accessible directly this way:

.. code-block:: text

  {{ my_variable_1 }}

Output will be:

.. code-block:: text

  hello!

List
^^^^

A list is like an array, and can be iterated over. It is important to note that
a list is an ordered element.

.. code-block:: yaml

  my_names_list:
    - bob
    - alice
    - henry

In Jinja2, variables in a list can be iterated over, or a specific value of the
list can be used (like an array):

.. code-block:: text

  {% for i in my_names_list %}
  {{ i }}
  {% endfor %}
  {{ my_names_list[0] }}

Note that index starts at 0.

Output will be:

.. code-block:: text

  bob
  alice
  henry
  bob

Note also that to check if a list is empty,
it is possible to check the list itself:

.. code-block:: text

  {% if my_names_list %}
  the list is not empty
  {% else %}
  the list is empty
  {% endif %}

Dictionary
^^^^^^^^^^^

A dictionary (also sometime called an hash),
is simply a pack of other variables, organized as a tree, and
defined under it (some kind of variables tree):

.. code-block:: yaml

  my_dictionarry_1:
    my_variable_1: hello!
    my_variable_2: 7777
    my_sub_part:
      color: yellow
      font: verdana
    my_names_list:
      - bob
      - alice
      - henry

It is important to note that a dictionary cannot be considered as an
ordered element.

In Jinja2, dictionary can be access two ways:

.. code-block:: text

  {% for i in my_dictionarry_1.my_names_list %}
  {{ i }}
  {% endfor %}
  {% for i in my_dictionarry_1['my_names_list'] %}
  {{ i }}
  {% endfor %}

  {{ my_dictionarry_1.my_names_list[0] }}
  {{ my_dictionarry_1['my_names_list'][0] }}


Output will be:

.. code-block:: text

  bob
  alice
  henry
  bob
  alice
  henry

  bob
  bob


To learn Jinja2 basics, please check the Ansible training at BEN_BEN

j2 Variables
^^^^^^^^^^^^

These are **BlueBanquise** specific variables.
All variables with name starting by **j2_** are j2 variables.

Most of these variables are used for the internal purpose of the stack.

These variables are here to simplify tasks and templates writing, and centralize
main logic of the stack.
To clarify your mind, you can consider that these variables contain Jinja2 code
as a string, that will be interpreted by Ansible during tasks/templates
execution.

Remember that in any case, if these variables are not providing the expected
value, you can use Ansible variables precedence mechanism to force your values.

Last point, for developers, these j2 variables should be considered as a way to
keep compatibility with roles, while upgrading the logic of the stack. Do not
hesitate to use them in roles, to ensure long term compatibility.

----------

Inventory, roles, and playbooks
-------------------------------

Inventory
^^^^^^^^^

As stated before, the Ansible inventory is the directory that contains Ansible variables and hosts
definitions.

Inventory is the **DATA**. In **BlueBanquise**, default path is ``~/inventory``.

.. note::
  You can have multiple inventories, and switch between them using ``-i`` parameter
  when using Ansible commands. You can also stack them with multiple ``-i``.

Roles
^^^^^

An Ansible role is a list of tasks to do to achieve a purpose.
For example, there will be a role called ``dhcp_server``, that contains tasks to
install, configure and start the dhcp server.

In **BlueBanquise**, roles are imported from collections.
You can add your own custom roles by editing the ``ansible.cfg`` file and
add your custom folders.

Roles are the **AUTOMATION LOGIC**.

Playbooks
^^^^^^^^^

An Ansible playbook is simply a list of roles to apply on a specific host or
group of hosts. It is a yaml file.

You can store your playbook files anywhere.

Playbooks are your **LIST OF ROLES TO APPLY on your hosts/targets**.

.. raw:: html

   <br>
   <div class="tip_card">                
   <div class="tip_card_img_container"><img src="../_static/img_avatar.png" style="width:100px; border-radius: 5px 0 0 5px; float: left;" /></div>
   <div class="tip_card_title_container"><b>Tip from the penguin:</b></div>
   <div class="tip_card_content_container"><p>Inventories, roles, and playbooks, are all text based. For production environment, strongly consider versioning them using git.</p></div>
   </div>
   <br>

----------

Variables precedence
--------------------

We are reaching the **very important** part of the stack.

If you do not know Ansible, PLEASE take 30 min to follow the small tutorial at BEN_BEN

Ansible has an internal mechanism called **variables precedence**.
Not using it prevents to unlock the stack full potential.

Simply put: you can define the same variables (same key name) multiple times in the inventory, and
using this mechanism, some definitions will have priority above others,
depending of their position and the target nodes.

When a variable is defined in a yml file, the position of the file in the
Ansible inventory structure matters and is important.

For example, a variable defined in ``~/inventory/group_vars/all/``
will have less precedence than a variable defined in
``~/inventory/cluster``, and so this last one will win if called.

The full list of available variables precedence is provided in Ansible
documentation:
`variable precedence list <https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable>`_

This feature is key to the stack and key for system administrator to manipulate
the **BlueBanquise** stack the way he/she wants, and *force* automatic
values if desired.

For example, values can be set by default, and then redefined for some groups of
hosts without changing the default for all others.
Or it can be used to simply fix a dynamic j2 variable to the desired value in
hosts definitions if dynamic value is not the one expected (you can even
redefine the whole logic of the stack without editing the stack code). Etc.

Inventory can be seen as a giant pizza, in 3D then flatten.

* *Paste* is the variable in ``~/inventory/group_vars/all``
* Then *large ingredients* comes from ``~/inventory/group_vars/equipment_myequipment``
* Then *small ingredients* above are the ``~/inventory/cluster/nodes/``
* And *pepper and tomatoes* (last layer) is the extra-vars at call.

.. image:: images/pizza_example.svg

I like pizza...

Refer to the Ansible tutorial of this documentation if you do not know how to use Ansible,
to learn this mechanism by practice. BEN_BEN

Replace
-------

Ansible and BlueBanquise default hash_behaviour is *replace* (which is Ansible's default one).

If using *replace*, when a dictionary is impacted by the variable’s precedence
mechanism, Ansible overwrite the **full dictionary** if a variable has a higher
precedence somewhere.

Jinja2
------

Jinja2 is the templating language used by Ansible to render templates in roles.
It is heavily used in the stack, and learning Jinja2 will often be needed to
create custom roles.
(But Jinja2 is simple if you are use to code or especially script with bash and python).

Full documentation is available in a "single page":
`Jinja2 template designer <https://jinja.palletsprojects.com/en/2.10.x/templates/>`_

Stack vocabulary
================

Icebergs
--------

Icebergs are logical (and often physical) isolation of ethernet management
networks. Most of the time, icebergs are used to:

* Spread load over multiple managements servers (for very large clusters). Icebergs are also often called "islands" in these cases.
* Secure cluster by dividing specific usages, to prevent compromised system to access all the network.

One Iceberg is composed of one or multiple managements servers, **in charge of
the same pool of nodes**.

**BlueBanquise** support many kinds of configurations, but most common are:

One iceberg configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

|

.. image:: images/one_iceberg.svg

|

For simple systems (small/medium HPC cluster, small enterprise network,
university IT practical session room, etc.), one iceberg scenario is the
standard. One or multiple management will reach the same ethernet administration
networks, and federate the same pool of nodes.

.. image:: images/clusters/single_iceberg_2_single_column.svg
   :align: center

|

Multiple icebergs configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|

.. image:: images/multiple_icebergs.svg

|

For advanced systems, (large HPC clusters needing load spreading with unified
network, enterprise network, etc.), multiple icebergs scenario can be required.
**BlueBanquise** allows multiple levels of icebergs, for complex needs.

Manipulating order of network_interfaces defined for each host allows to create
a unified network so all nodes from all icebergs can communicate through this
network (most of the time an Interconnect network).

.. image:: images/clusters/multiple_icebergs.png
   :align: center

|

Equipment profiles
------------------

In **BlueBanquise**, nodes are often part of a group starting with
prefix **equipment_**. These groups are called *equipment profiles*.

They are used to provide to hosts of this group the **equipment_profile**
parameters (vender, server model, hardware embed, hosts operating system parameters, kernel parameters,
partitioning, etc.), and other variables if needed like dedicated
authentication parameters. These variables are prefixed with **ep_**.

.. image:: images/inventory/ep_hard.svg
   :align: center

These are key groups of the stack.

**It is important** to note that equipment_profiles variables (**ep_**)
**must not** be used at an upper level than group_vars in variables precedence.
**It can, but you must NOT**, due to special usage of them.

For now, just keep in mind these variables exist. These will be discussed later.

-------------

You can now follow the next part, depending of your needs:

* Proceed to quick start to deploy a very basic cluster.
* Proceed with a standard full cluster deployment.
