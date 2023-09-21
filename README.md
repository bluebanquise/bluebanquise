# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

:loudspeaker: The main branch is under active dev for now. Consider using a stable branch for production. :loudspeaker:

## What is BlueBanquise

**BlueBanquise** is group of coherent **Ansible** collections and tools, designed to deploy and manage large group of hosts (clusters of nodes).

The BlueBanquise collections are generic and can adapt to any kind of architecture (High Performance Computing clusters, university or enterprise infrastructures, Blender render farm, K8S cluster, etc.).
A specific focus is made on scalability for very large clusters.

When "stacked" together, collections and tools are called **BlueBanquise stack**.

## Collections

The following collections are available. **Please note that for now, only infrastructure collection of BlueBanquise 2.X version is considered stable**.

* :globe_with_meridians: **[Infrastructure](https://github.com/bluebanquise/bluebanquise/collections/infrastructure):** the core of the stack, focused on providing roles and tools to deploy hosts and configure vital services.
* :globe_with_meridians: **[hardware](https://github.com/bluebanquise/bluebanquise/collections/hardware):** specific hardware support roles (GPU, interconnect, etc.).
* :globe_with_meridians: **[file system](https://github.com/bluebanquise/bluebanquise/collections/file_systems):** support for local or network FS roles.
* :globe_with_meridians: **[hpc](https://github.com/bluebanquise/bluebanquise/collections/hpc):** High Performance Computing related roles.
* :globe_with_meridians: **[containers](https://github.com/bluebanquise/bluebanquise/collections/containers):** containers related roles.
* :globe_with_meridians: **[high availability](https://github.com/bluebanquise/bluebanquise/collections/high_availability):** HA and load balancing related roles.
* :globe_with_meridians: **[logging](https://github.com/bluebanquise/bluebanquise/collections/logging):** system logging related roles (different from monitoring).
* :globe_with_meridians: **[monitoring](https://github.com/bluebanquise/bluebanquise/collections/monitoring):** cluster monitoring related roles.
* :globe_with_meridians: **[security](https://github.com/bluebanquise/bluebanquise/collections/security):** system security related roles.

Infrastructure collection should be compatible with all target Linux distributions (RHEL 8, RHEL 9, Debian 11, Debian 12, OpenSuse Leap 15, Ubuntu 20.04, Ubuntu 22.04). Other collections do not support all these distributions (support is added on demand).

## Resources

### Documentation

The stack documentation is available on the BlueBanquise website, in [documentation subfolder](https://bluebanquise.com/documentation/). Please note that this documentation is deprecated, and a new documentation for BlueBanquise 2.X will be provided soon.

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
|                         | Debian                        | 11, 12                   |  x86_64, arm64                | √. Diskless not supported for now.  |
| Suse                    |                               |                    |                  |                                                             |
|                         | SLES                          | 15               | x86_64, aarch64  | √. Diskless not supported for now.                                                           |
|                         | OpenSuse Leap                 | 15               | x86_64, aarch64  | √. Diskless not supported for now.          |

Ansible >= 4.10.0 is mandatory for BlueBanquise to run properly.

Please note that EL 7 systems (Centos 7, RHEL 7, etc.) is now considered best effort only.

**[OpenHPC](https://openhpc.community/downloads/)** scientific packages are compatible with the stack.

## Algoric project

BlueBanquise is part of the [**Algoric**](https://algoric.org/) project from the [**Fabrique du Loch**](https://www.lafabriqueduloch.org/fr/accueil/) FabLab, located in Brittany - France.

![BlueBanquise Logo](resources/pictures/FabriqueDuLochAlgoric_logo_large.svg)

It is a revamping of the old stack [Banquise](https://github.com/oxedions/banquise), based on Salt.

The BlueBanquise project is a 100% open source project, not managed by a company, and will stay MIT license.

## The name

You may wonder where this name comes from:

* [BlueBanquise](https://en.wikipedia.org/wiki/File:Blue_iceberg_in_the_Ilulissat_icefjord.jpg)
* [Blue Iceberg](https://en.wikipedia.org/wiki/Blue_iceberg)
