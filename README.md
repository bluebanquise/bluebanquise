# BlueBanquise
![BlueBanquise Logo](resources/pictures/BlueBanquise_logo_large.svg)

<p align="center">
  Web site: <a href="https://bluebanquise.com"><b>https://bluebanquise.com</b></a>
</p>

## What is BlueBanquise

**BlueBanquise** is a coherent **Ansible** roles collection, designed to deploy and manage large group of hosts (clusters of nodes).

Main target is High Performance Computing (HPC), but the BlueBanquise stack is generic and can adapt to any kind of architecture (university or enterprise infrastructures, render farm, etc.).

BlueBanquise is part of the **Algoric** Project from the [**Fabrique du Loch**](https://www.lafabriqueduloch.org/fr/accueil/) FabLab.

![BlueBanquise Logo](resources/pictures/FabriqueDuLochAlgoric_logo_large.svg)

It is a revamping of the old stack [Banquise](https://github.com/oxedions/banquise), based on Salt.

## Documentation and files

The stack documentation is available on the BlueBanquise main website, in [documentation subfolder](https://bluebanquise.com/documentation/).

The stack repositories are available in the [repositories subfolder](https://bluebanquise.com/repository/).

## The name

You may wonder where this name comes from:

* [BlueBanquise](https://en.wikipedia.org/wiki/File:Blue_iceberg_in_the_Ilulissat_icefjord.jpg)
* [Blue Iceberg](https://en.wikipedia.org/wiki/Blue_iceberg)

## Supported software environment

Currently supported OS are:

* Fully supported:
  * RedHat/Centos 7
  * RedHat/Centos 8

* In development:
  * OpenSuse Leap 15.1

* To be included if demand:
  * Ubuntu
  * Debian

Ansible >= 2.9.13 is mandatory for BlueBanquise to run properly.

**[OpenHPC](https://openhpc.community/downloads/)** scientific packages and OpenHPC slurm job scheduler are compatible with the stack.

## Thanks

Special thanks:

* to [CINES](https://www.cines.fr/en/) who provided Algoric team with hardware to develop this stack.
* to [@remyd1](https://github.com/remyd1) for his help on [Banquise](https://github.com/oxedions/banquise) original stack.
* to [@bouriquet](https://github.com/bouriquet) for his active help on the stack.
* to [@btravouillon](https://github.com/btravouillon) for his active help on the stack.
