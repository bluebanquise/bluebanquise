# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

## The stack

**BlueBanquise** is an **Ansible** based stack, designed to deploy and manage large group of hosts.

Main target is High Performance Computing, but stack is generic and can adapt to any kind of cluster architecture (University or Enterprise network, render farm, etc).

Currently supported OS are:

* RedHat/Centos 7.6 (Full)
* RedHat 8.0 (Partial, in dev)
* Ubuntu 18.04 (Partial, in dev)
* OpenSuse Leap 15.1 (Partial, in dev)

Debian 9 and 10 are dropped for now because too much issues with the netboot part.

Ansible **>= 2.8.2 is mandatory** for BlueBanquise to run properly.

BlueBanquise is part of the **Algoric** Project from the [**Fabrique du Loch**](https://www.lafabriqueduloch.org/fr/accueil/) FabLab.

![BlueBanquise Logo](resources/pictures/FabriqueDuLochAlgoric_logo_large.svg)

BlueBanquise is a revamping of the old stack Banquise, based on Salt.

## Thanks

Special thanks to [CINES](https://www.cines.fr/en/) who provided Algoric team with hardware.
