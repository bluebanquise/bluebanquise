# Flexlm

## Overview

A role to manage Flexlm daemon and licence files.

This role will :
* Create a specific user to launch daemon.
* Set up a systemd service (flexlm-item.name).
* Copy vendor daemon binaries to the host if source is specified.
* Copy licence file to the host if source is specified.
* Create a symlink (/usr/tmp) to /tmp to avoid error (Ubuntu/Debian).
* Create a symlinks to ld-linux librairies (Ubuntu/Debian).

This role is validated on:
* RHEL / CentOS 7 & 8
* Debian Buster
* Ubuntu 18.04 & 20.04

## Role Variables

* **flexlm_required_packages** : List of required packages requested as 'flexlm' dependencies [default : `[]`]
* **flexlm_deploy_state** : The desired state this role should achieve. [default : `present`].
* **flexlm_user_name** : Username used to launch `lmgrd` [default : `flexlm`].
* **flexlm_service_unit_content** : Template used to generate the previous file [default : `etc/systemd/system/flexlm.service.j2`].
* **flexlm_licences** : Lists to manage vendor daemon and licence files [default : `[]`].

## Example Playbook

* Manage Flexlm to provide Intel (without binaries) :

``` yaml
- hosts: intel-lm
  roles:
    - role: flexlm
      flexlm_licences:
        - name: intel
          description: 'flexlm Licence Manager for Intel'
          bin_path: '/opt/intel/bin'
          lic_path: '/opt/intel/etc/licence.lic'
          lmgrd_path: '/opt/intel/bin/lmgrd'
```

* Manage Flexlm to provide Matlab Licence and vendor daemon binaries :

```yaml
- hosts: matlab-lm
  roles:
    - role: flexlm
      flexlm_licences:
        - name: matlab
          description: 'flexlm Licence Manager for Matlab'
          bin_path: '/opt/matlab/bin'
          bin_src: '{{ inventory_dir + "/../resources/service/matlab-lm/bin/" }}'
          lic_path: '/opt/matlab/etc/licence.lic'
          lic_src: '{{ inventory_dir + "/../resources/host/matlab-lm.domain/etc/licence.lic" }}'
          lmgrd_path: '/opt/matlab/bin/lmgrd'
```

## Known Issues

* If a value of one licence change in **flexlm_licences** var, all services will be restarted.

## Changelog

* 1.0.1: Update all module to full path. Matthieu Isoard
* 1.0.0: Initial support. Matthieu Isoard
