===========
Quick start
===========

This quick start guide aims to install BlueBanquise and deploy a small cluster composed of 2 nodes (1 management and 1 non management), based on AlmaLinux 9.

Install BlueBanquise
====================

Make sure the system possesses curl command, then bootstrap bluebanquise using the provided online installer:

.. code-block:: text

  sudo source <(curl -s https://raw.githubusercontent.com/bluebanquise/bluebanquise/refs/heads/master/bootstrap/online_bootstrap.sh)

Get example inventory
=====================

Now that bluebanquise has been deployed, login as bluebanquise user, and grab the example inventory:

.. code-block:: text

  sudo su - bluebanquise
  cp -a bluebanquise/resources/examples/quick_start /var/lib/bluebanquise/inventory

Now tune the mac addresses and NIC names of nodes according to your current setup.

Deploy configuration on management
==================================

Setup PXE for second node
=========================

Provision second node
=====================




We will assume here you already have a recent Ansible setup and configured. If you are new to Ansible, you can use the [provided generic tutorial](http://bluebanquise.com/tutorials/sysadmin_ansible/).

If you are aiming clients hosts with an old native Python version (RHEL 8 or OpenSuse Leap 15), be sure to cap your ansible-core pip package version to 2.16 . 2.17 and more are no more compatible with Python 3.6.

### 1. Core variables and Jinja2 extensions

In order to use BlueBanquise collections, you need the core variables, that contain the logic (BlueBanquise relies on a centralized logic to easily impact all roles at once).

To install core variables, you can either:

* Copy file [bb_core.yml](resources/bb_core.yml) into your inventory at `group_vars/all/` level
* Or invoke the vars plugin at ansible-playbook execution, using `ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.infrastructure.core`
* Or add it into your `ansible.cfg` file (see example at [ansible.cfg](./ansible.cfg)) by adding `vars_plugins_enabled  = ansible.builtin.host_group_vars,bluebanquise.infrastructure.core`

While first solution is simpler, second solution is preferred as it allows to use the galaxy update mechanism to ensure your core logic is always up to date (bug fixes mainly).

In both cases, you need to enable some Jinja2 extensions at run time. To do so, either:

* Add it into your `ansible.cfg` file (see example at [ansible.cfg](./ansible.cfg)) by adding `jinja2_extensions = jinja2.ext.loopcontrols,jinja2.ext.do`
* Or invoke the extensions at ansible-playbook execution, using `ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do`

Note that not all roles need this core logic, and that all logic variables are prefixed by `j2_`.

### 2. Install collections

To install BlueBanquise collection, you can use the ansible-galaxy command:

```
ansible-galaxy collection install git+https://github.com/bluebanquise/bluebanquise.git#/collections/infrastructure,master -vvv --upgrade
```

### 3. Create inventory

To create your inventory, you can use the provided [datamodel](resources/data_model.md), and roles embed READMEs (for example, for pxe_stack role, you can rely on [README.md](collections/infrastructure/roles/pxe_stack/README.md), etc.).

### 4. Create playbooks

You can invoke BlueBanquise roles using full name:

```
---
- name: managements playbook
  hosts: "fn_management"
  roles:
    - role: bluebanquise.infrastructure.dhcp_server
      tags: dhcp_server
    - role: bluebanquise.infrastructure.pxe_stack
      tags: pxe_stack
```

If you are not running Ansible as root, remember to pass the `-b` (`--become`) argument to ansible-playbook command.

### 5. Read documentation

It is advised to read the documentation at https://bluebanquise.com/documentation/ to understand stack basic concepts.