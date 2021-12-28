# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

## What is BlueBanquise

**BlueBanquise** is a coherent **Ansible** roles collection, designed to deploy and manage large group of hosts (clusters of nodes).

The BlueBanquise stack is generic and can adapt to any kind of architecture (High Performance Computing clusters, university or enterprise infrastructures, Blender render farm, K8S cluster, etc.).

The stack is split over two repositories:

* :globe_with_meridians: **[Core](https://github.com/bluebanquise/bluebanquise):** the CORE of the stack, focused on providing roles and tools to deploy hosts and configure vital services. CORE is generic to any kind of cluster.

* :globe_with_meridians: **[Community](https://github.com/bluebanquise/community):** COMMUNITY roles and tools provides additional production level features **on top of CORE** to specialize cluster.

## Resources

### Documentation

The stack documentation is available on the BlueBanquise website, in [documentation subfolder](https://bluebanquise.com/documentation/).

Note that each role (CORE or COMMUNITY) embeds its own readme, with detailed
usage description.

### Packages

The stack packages are available in the [repositories subfolder](https://bluebanquise.com/repository/releases/).

## Supported software environment

The stack aims at supporting a maximum range of hardware, CPU architectures, and Linux distributions.

Currently supported distributions are:

| Operating System family | Operating System distribution | Tested versions    | Architectures    | Notes                                                       |
| ----------------------- | ----------------------------- | ------------------ | ---------------- | ----------------------------------------------------------- |
| Red Hat                 |                               |                    |                  |                                                             |
|                         | RHEL                          | 7, 8               | x86_64, aarch64  | √                                                           |
|                         | Rocky Linux                   | 8                  | x86_64, aarch64  | √                                                           |
|                         | CentOS                        | 7, 8               | x86_64, aarch64  | √                                                           |
|                         | CentOS Stream                 | 8                  | x86_64, aarch64  | √                                                           |
|                         | Oracle Linux                  | 8                  | x86_64, aarch64  | √                                                           |
|                         | Cloud Linux                   | 8                  | x86_64, aarch64  | √                                                           |
|                         | Alma Linux                    | 8                  | x86_64, aarch64  | √                                                           |
| Debian                  |                               |                    |                  |                                                             |
|                         | Ubuntu                        | 20.04              | x86_64, aarch64  | √. Diskless not supported for now.                          |
|                         | Debian                        |                    |                  | Targeted for future release                                 |
| Suse                    |                               |                    |                  |                                                             |
|                         | SLES                          |                    |                  | Targeted for future release                                 |
|                         | OpenSuse Leap                 |                    |                  | Targeted for future release                                 |

Ansible >= 2.9.13 is mandatory for BlueBanquise to run properly.

**[OpenHPC](https://openhpc.community/downloads/)** scientific packages and OpenHPC slurm job scheduler are compatible with the stack.

## Algoric project

BlueBanquise is part of the **Algoric** Project from the [**Fabrique du Loch**](https://www.lafabriqueduloch.org/fr/accueil/) FabLab.

![BlueBanquise Logo](resources/pictures/FabriqueDuLochAlgoric_logo_large.svg)

It is a revamping of the old stack [Banquise](https://github.com/oxedions/banquise), based on Salt.

## The name

You may wonder where this name comes from:

* [BlueBanquise](https://en.wikipedia.org/wiki/File:Blue_iceberg_in_the_Ilulissat_icefjord.jpg)
* [Blue Iceberg](https://en.wikipedia.org/wiki/Blue_iceberg)

## Thanks

Special thanks:

* to [CINES](https://www.cines.fr/en/) who provided Algoric team with hardware to develop this stack.
* to [@remyd1](https://github.com/remyd1) for his help on [Banquise](https://github.com/oxedions/banquise) original stack.
* to [@bouriquet](https://github.com/bouriquet) for his active help on the stack.
* to [@btravouillon](https://github.com/btravouillon) for his active help on the stack.
