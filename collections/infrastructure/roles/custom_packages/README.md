# Custom Packages

## Description

This Role simply allows to install custom packages on the system that 
are not provided to other bluebanquise roles.
That can be usefull to keep all the customizations relating OS packages
synced with BlueBanquise so you dont need to have extra steps in 
configuring nodes.

## Instructions

This role is very simple and works based on ansible groups.
I recomend you to have on single file on the "all" group ( $HOME/bluebanquise/inventory/group_vars/all/addons/custom_packages.yml)
to manage all the custom packages in the system, as the role will already filter the instalation by groups
and normally will be more visible to have this on a single file

Example of "custom_packages.yml" file:

```yaml
custom_packages:
  mg_computes:
    - openmpi
  mg_logins:
    - vim
    - '@Development Tools'
  equipment_typeGPU:
    - htop
```

## Changelog

* 1.0.1: Remove braces on item. Abatcha Olloh <abatchaolloh@outlook.fr>
* 1.0.0: Role creation. Lucas Santos <lucassouzasantos@gmail.com>
