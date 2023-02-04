# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

## What is BlueBanquise

**BlueBanquise** is group of coherent **Ansible** collections and tools, designed to deploy and manage large group of hosts (clusters of nodes).

The BlueBanquise collections are generic and can adapt to any kind of architecture (High Performance Computing clusters, university or enterprise infrastructures, Blender render farm, K8S cluster, etc.).
A specific focus is made on scalability for very large clusters.

When "stacked" together, collections and tools form the **BlueBanquise stack**.

## Collections

The following collections are available:

* :globe_with_meridians: **[Infrastructure](https://github.com/bluebanquise/bluebanquise/collections/infrastructure):** the core of the stack, focused on providing roles and tools to deploy hosts and configure vital services.

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
|                         | RHEL                          | 7, 8, 9               | x86_64, aarch64  | √                                                           |
|                         | Rocky Linux                   | 8, 9                  | x86_64, aarch64  | √                                                           |
|                         | CentOS                        | 7, 8               | x86_64, aarch64  | √                                                           |
|                         | CentOS Stream                 | 8                  | x86_64, aarch64  | √                                                           |
|                         | Alma Linux                    | 8, 9                  | x86_64, aarch64  | √                                                           |
| Debian                  |                               |                    |                  |                                                             |
|                         | Ubuntu                        | 20.04, 22.04              | x86_64, arm64  | √. Diskless not supported for now.                          |
|                         | Debian                        | 11                   |  x86_64, arm64                | √. Diskless not supported for now.  |
| Suse                    |                               |                    |                  |                                                             |
|                         | SLES                          | 15               | x86_64, aarch64  | √. Diskless not supported for now.                                                           |
|                         | OpenSuse Leap                 | 15               | x86_64, aarch64  | √. Diskless not supported for now.          |

Ansible >= 4.10.0 is mandatory for BlueBanquise to run properly.

**[OpenHPC](https://openhpc.community/downloads/)** scientific packages are compatible with the stack.

## Algoric project

BlueBanquise is part of the [**Algoric**](https://algoric.org/) project from the [**Fabrique du Loch**](https://www.lafabriqueduloch.org/fr/accueil/) FabLab, located in Brittany - France.

![BlueBanquise Logo](resources/pictures/FabriqueDuLochAlgoric_logo_large.svg)

It is a revamping of the old stack [Banquise](https://github.com/oxedions/banquise), based on Salt.

## The name

You may wonder where this name comes from:

* [BlueBanquise](https://en.wikipedia.org/wiki/File:Blue_iceberg_in_the_Ilulissat_icefjord.jpg)
* [Blue Iceberg](https://en.wikipedia.org/wiki/Blue_iceberg)
