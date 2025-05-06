# ClusterShel

## Description

This role optionally installs clustershell and setup groups for clustershell (based on Ansible inventory groups provided).
It can be used in combinaison with other BlueBanquise stack tools, like `bluebanquise-bootset`.

## Instructions

By default, role will not install Clustershell, since Clustershell is already a base 
requirement for the BlueBanquise stack. However, if for any reasons you wish the role to install it,
set either variables `clustershell_install_from_pip` or `clustershell_install_from_package` to true.

`clustershell_install_from_pip` will uses pip to install Clustershell, while `clustershell_install_from_package` 
will rely on system native packages manager to install it.

Once role has been deployed, check groups using:

```
nodeset -LL
```

Note:
If you are using the Python virtual environment, the return of the command may not be correct.
You can use the `clustershell_prefix_path` variable to copy the configuration file to the right place.
Default value is empty.

## To be done

Tree execution mode is missing.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.4.0: Unnecessary leading comma in Clustershell template. Leo Magdanello <lmagdanello40@gmail.com>
* 1.3.0: Add optional variable clustershell_prefix_path. Pierre Gay <pierre.gay@u-bordeaux.fr>, Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>
* 1.2.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Prevent dummy user to be included. Documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Fixed bad template. Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com> 
