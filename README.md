# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

---
Devs infos:

:yellow_heart: The main branch is now considered unstable as a new major version is under development. Please use a release tag for production.

:yellow_heart: Current core version: 3.4.0, under development.

:green_heart: ansible-core 2.19 is now supported.

:yellow_heart: documentation v3 is currently written, doing my best.

---

## What is BlueBanquise

**BlueBanquise** is group of coherent **Ansible** roles and tools, designed to provision and manage <u>low level infrastructure</u> of large group of hosts (clusters of nodes).

The BlueBanquise collection is generic and can adapt to any kind of architecture (High Performance Computing clusters, university or enterprise infrastructures, Blender render farm, K8S cluster, etc.).
A specific focus is made on scalability for very large clusters.

The infrastructure collection should be compatible with most target Linux distributions (RHEL 9, RHEL 10, Debian 13, OpenSuse Leap 15, Ubuntu 24.04). However, please note that some roles do not support all these distributions (support is added on demand).

## License

BlueBanquise repository is under **MIT license**.

:star: The BlueBanquise project is a **100% open source project, not managed by a company, and will stay MIT license**. :star:

## Donate

If you use and like BlueBanquise, please consider donating to the **UNICEF** (https://www.unicef.org/).

![UNICEF Logo](resources/pictures/UNICEF_Logo.png)

I have a decent job, I don't need money, but they do.
In the 21th century, it is a shame not all children live in peace.

## AI

I am using AI time to time to help me maintain and develop BlueBanquise, especially to detect bugs and for the user cli tools. Reason is simple: keeping up to date a stack that covers around multiple versions of 4 different Linux distributions is way too much for a single person.
Note however that I read all changes proposed by AI, and I do not commit something I don't understand.

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
|                         | RHEL (and clones)             | 9, 10              | x86_64, aarch64  | √                                                           |
| Debian                  |                               |                    |                  |                                                             |
|                         | Ubuntu                        | 24.04              | x86_64, arm64    | √. Diskless not supported for now.                          |
|                         | Debian                        | 13                 | x86_64, arm64    | √. Diskless not supported for now.                          |
| Suse                    |                               |                    |                  |                                                             |
|                         | Leap                          | 15.7               | x86_64, arm64    | √. Diskless not supported for now.                          |

ansible-core >= 2.16 is mandatory for BlueBanquise to run properly (it might work with earlier versions, but not tested).

Please note that:

* EL 7 and 8 are now considered best effort only.
* Ubuntu 18.04, 20.04 and 22.04 are now considered best effort only.
* Debian 11 and 12 are now considered best effort only.
* RHEL 8 and OpenSuse Leap 15 need an ansible-core==2.16, 2.17+ is not compatible.

## The project

It is a revamping of the old stack [Banquise](https://github.com/oxedions/banquise), based on Salt.

## The name

You may wonder where this name comes from:

* [BlueBanquise](https://en.wikipedia.org/wiki/File:Blue_iceberg_in_the_Ilulissat_icefjord.jpg)
* [Blue Iceberg](https://en.wikipedia.org/wiki/Blue_iceberg)
