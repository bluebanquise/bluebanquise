# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

---
Devs infos:

:green_heart: The main branch is now considered stable.

:green_heart: Current core version: 3.2.1

:red_heart: ansible-core 2.19 is not currently compatible, stack is limited to 2.18.10, work in progress to solve this issue.

---

## What is BlueBanquise

**BlueBanquise** is group of coherent **Ansible** roles and tools, designed to deploy and manage large group of hosts (clusters of nodes).

The BlueBanquise collection is generic and can adapt to any kind of architecture (High Performance Computing clusters, university or enterprise infrastructures, Blender render farm, K8S cluster, etc.).
A specific focus is made on scalability for very large clusters.

When "stacked" together, roles and tools are called the **BlueBanquise stack**.

The infrastructure collection should be compatible with most target Linux distributions (RHEL 8, RHEL 9, Debian 11, Debian 12, OpenSuse Leap 15, Ubuntu 20.04, Ubuntu 22.04, Ubuntu 24.04). However, please note that some non core roles do not support all these distributions (support is added on demand).

## License

BlueBanquise repository is under **MIT license**, except Bluebanquise documentation which is under **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License**.

## Donate

If you use and like BlueBanquise, please consider donating to the **UNICEF** (https://www.unicef.org/).

![UNICEF Logo](resources/pictures/UNICEF_Logo.png)

I have a decent job, I don't need money, but they do.
In the 21th century, it is a shame not all children live in peace.

## Quickstart

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

## Resources

### Documentation

The stack documentation is available on the BlueBanquise website, in [documentation subfolder](https://bluebanquise.com/documentation/).

Note that each role embeds its own README, with detailed usage description.

### Packages

The stack packages are available in the [repositories subfolder](https://bluebanquise.com/repository/releases/).

## Supported software environment

The stack aims at supporting a maximum range of hardware, CPU architectures, and Linux distributions.

Currently tested and supported distributions (other derivative could work) are:

| Operating System family | Operating System distribution | Tested versions    | Architectures    | Notes                                                       |
| ----------------------- | ----------------------------- | ------------------ | ---------------- | ----------------------------------------------------------- |
| Red Hat                 |                               |                    |                  |                                                             |
|                         | RHEL                          | 8, 9               | x86_64, aarch64  | √                                                           |
|                         | Rocky Linux                   | 8, 9               | x86_64, aarch64  | √                                                           |
|                         | CentOS                        | 8                  | x86_64, aarch64  | √                                                           |
|                         | CentOS Stream                 | 8                  | x86_64, aarch64  | √                                                           |
|                         | Alma Linux                    | 8, 9               | x86_64, aarch64  | √                                                           |
| Debian                  |                               |                    |                  |                                                             |
|                         | Ubuntu                        | 20.04, 22.04, 24.04              | x86_64, arm64  | √. Diskless not supported for now.                          |
|                         | Debian                        | 11, 12             |  x86_64, arm64                | √. Diskless not supported for now.  |
| Suse                    |                               |                    |                  |                                                             |
|                         | SLES                          | 15.6                 | x86_64, aarch64  | √. Diskless not supported for now.                                                           |
|                         | OpenSuse Leap                 | 15.6                 | x86_64, aarch64  | √. Diskless not supported for now.          |

ansible-core >= 2.16 is mandatory for BlueBanquise to run properly (it might work with earlier versions, but not tested).

Please note that:

* EL 7 systems (Centos 7, RHEL 7, etc.) is now considered best effort only as system is past EOL.
* Ubuntu 18.04 and Suse 12 are no more supported (too old, I miss the time to support them).
* RHEL 8 and OpenSuse Leap 15 need an ansible-core==2.16, 2.17+ is not compatible.

## The project

It is a revamping of the old stack [Banquise](https://github.com/oxedions/banquise), based on Salt.

:seedling: The BlueBanquise project is a **100% open source project, not managed by a company, and will stay MIT license**. :seedling:

## The name

You may wonder where this name comes from:

* [BlueBanquise](https://en.wikipedia.org/wiki/File:Blue_iceberg_in_the_Ilulissat_icefjord.jpg)
* [Blue Iceberg](https://en.wikipedia.org/wiki/Blue_iceberg)
