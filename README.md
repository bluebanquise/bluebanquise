# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

---
Devs infos:

:green_heart: The main branch is now considered stable.

:green_heart: Current core version: 3.2.2 .

:green_heart: ansible-core 2.19 is now supported.

:yellow_heart: documentation v3 is currently written, might take few weeks to complete.

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

### 1. Bootstrap the stack

First step is to use the bootstrap script that will create the bluebanquise user on your system.
Make sure first you have both sudo and curl installed on the system.

```
sudo bash <(curl -s https://raw.githubusercontent.com/bluebanquise/bluebanquise/refs/heads/master/bootstrap/online_bootstrap.sh)
```

Read the warning message, and accept if you agree with it.

Once bootstrap is done, you can login as bluebanquise user:

```
sudo su - bluebanquise
```

Note that the ANSIBLE_CONFIG variable is set to `/var/lib/bluebanquise/bluebanquise/ansible.cfg` automatically, and a python virtual environment is auto activated and contains latest Ansible version available for your local system.

BlueBanquise Ansible's collections are also already installed for this bluebanquise user.

### 2. Use example inventory

An example inventory can be found inside this repository at resources/examples/simple_cluster. You can use that as a base, and use documentation at https://bluebanquise.com/documentation to tune it to your needs.

### 3. Create playbooks

You can invoke BlueBanquise roles using full name:

```
---
- name: managements playbook
  hosts: "fn_management"
  roles:
    - role: bluebanquise.infrastructure.dhcp_server
      tags: dhcp_server
    - role: bluebanquise.infrastructure.hosts_file
      tags: hosts_file
```

If you are not running Ansible as root, remember to pass the `-b` (`--become`) argument to ansible-playbook command.

### 4. Read documentation

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
