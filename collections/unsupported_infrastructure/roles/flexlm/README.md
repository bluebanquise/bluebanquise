# Flexlm

|      OS      | Version | Supported |
|:-------------|:--------|:---------:|
| Ubuntu       |   20.04 |    yes    |
| Ubuntu       |   22.04 |    no     |
| RHEL         |       7 |    yes    |
| RHEL         |       8 |    yes    |
| RHEL         |       9 |    no     |
| OpenSuseLeap |      15 |    no     |
| Debian       |      11 |    yes    |

## Overview

A role to manage Flexlm daemon and license files.

This role will :
* Create a specific user to launch daemon.
* Set up a systemd service (flexlm-item.name).
* Copy vendor daemon binaries to the host if source is specified.
* Copy license file to the host if source is specified.
* Create a symlink (/usr/tmp) to /tmp to avoid error (Ubuntu/Debian).
* Create a symlinks to ld-linux libraries (Ubuntu/Debian).

This role is validated on:
* RHEL / CentOS 7 & 8
* Debian Buster
* Ubuntu 18.04 & 20.04

## Role Variables

* **flexlm_required_packages** : List of required packages requested as 'flexlm' dependencies [default : `[]`]
* **flexlm_deploy_state** : The desired state this role should achieve. [default : `present`].
* **flexlm_user_name** : Username used to launch `lmgrd` [default : `flexlm`].
* **flexlm_service_unit_content** : Template used to generate the previous file [default : `etc/systemd/system/flexlm.service.j2`].
* **flexlm_licenses** : Lists to manage vendor daemon and license files [default : `[]`].

## Example Playbook

* Manage Flexlm to provide Intel (without binaries) :

``` yaml
- hosts: intel-lm
  roles:
    - role: flexlm
      flexlm_licenses:
        - name: intel
          description: 'flexlm license Manager for Intel'
          bin_path: '/opt/intel/bin'
          lic_path: '/opt/intel/etc/license.lic'
          lmgrd_path: '/opt/intel/bin/lmgrd'
```

* Manage Flexlm to provide Matlab License and vendor daemon binaries :

```yaml
- hosts: matlab-lm
  roles:
    - role: flexlm
      flexlm_licenses:
        - name: matlab
          description: 'flexlm license Manager for Matlab'
          bin_path: '/opt/matlab/bin'
          bin_src: '{{ inventory_dir + "/../resources/service/matlab-lm/bin/" }}'
          lic_path: '/opt/matlab/etc/license.lic'
          lic_src: '{{ inventory_dir + "/../resources/host/matlab-lm.domain/etc/license.lic" }}'
          lmgrd_path: '/opt/matlab/bin/lmgrd'
```

## Known Issues

* If a value of one license change in **flexlm_licenses** var, all services will be restarted.

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.0.3: Fix grammar. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Fix few packages names. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Update all module to full path. Matthieu Isoard
* 1.0.0: Initial support. Matthieu Isoard
