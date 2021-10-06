# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

## What is BlueBanquise

**BlueBanquise** is a coherent **Ansible** roles collection, designed to deploy and manage large group of hosts (clusters of nodes).

While main target is High Performance Computing (HPC), the BlueBanquise stack is generic and can adapt to any kind of architecture (university or enterprise infrastructures, render farm, etc.).

The stack is split over multiple repositories:

* :globe_with_meridians: **[Core](https://github.com/bluebanquise/bluebanquise):** the CORE of the stack, provides roles and tools to deploy and configure hosts.

* :globe_with_meridians: **[Community](https://github.com/bluebanquise/community):** COMMUNITY roles and tools, provides additional features on top of CORE. The release cycle of COMMUNITY is different than CORE.

* :globe_with_meridians: **[Tools](https://github.com/bluebanquise/tools):** Tools repository contains sources of stack tools.

* :globe_with_meridians: **[Infrastructure](https://github.com/bluebanquise/infrastructure):** Infrastructure repository contains needed script and files to build packages.

## Resources

### Documentation

The stack documentation is available on the BlueBanquise website, in [documentation subfolder](https://bluebanquise.com/documentation/).

Note that each role (CORE or COMMUNITY) embeds its own readme, with detailed
usage description.

### Packages

The stack packages are available in the [repositories subfolder](https://bluebanquise.com/repository/).

## Supported software environment

| Operating System family | Operating System distribution | Tested versions    | Notes                                                       |
| ----------------------- | ----------------------------- | ------------------ | ----------------------------------------------------------- |
| Red Hat                 |                               |                    |                                                             |
|                         | RHEL                          | 7, 8               | √                                                           |
|                         | CentOS                        | 7, 8               | √                                                           |
|                         | CentOS Stream                 | 8                  | √                                                           |
|                         | Oracle Linux                  | 8                  | √                                                           |
|                         | Cloud Linux                   | 8                  | Base iso not enough, need to bind to external repositories. |
|                         | Alma Linux                    | 8                  | √                                                           |
|                         | Rocky Linux                   | 8                  | √                                                           |
| Suse                    |                               |                    |                                                             |
|                         | SLES                          | NA                 | Targeted for future release                                 |
|                         | OpenSuse Leap                 | NA                 | Targeted for future release                                 |
| Debian                  |                               |                    |                                                             |
|                         | Ubuntu                        | NA                 | Targeted for future release                                 |
|                         | Debian                        | NA                 | Targeted for future release                                 |

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
