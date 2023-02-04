# Generic Packages Services Folders and Files

<p align="center"><img src="https://raw.githubusercontent.com/bluebanquise/community/main/roles/generic_psf/generic_psf_logo.svg"></p>

## Owner

@johnnykeats

## Description

The role simply installs listed packages, create requested folders,
render requested files, and start listed services.

## Instructions

To install requested packages, use variable **generic_psf_packages** defined
as a list of packages:

```yaml
  generic_psf_packages:
    - Lmod
    - gcc
    - gcc-c++
```

To create folders, use variable **generic_psf_folders** defined
as a list of folders with needed/optional parameters:

```yaml
  generic_psf_folders:
    - path: /etc/custom
      owner: root # Optional, default root if not set
      group: root # Optional, default root if not set
      mode: 0755 # Optional, default 0755 if not set
```

To render requested files, use variable **generic_psf_files** defined
as a list of files with content and needed/optional parameters:

```yaml
  generic_psf_files:
    - path: /etc/custom/customfile.conf
      content: |
        This is the content
        of the multilines
        custom file.
      owner: root # Optional, default root if not set
      group: root # Optional, default root if not set
      mode: 0644 # Optional, default 0655 if not set
```

To start requested services, use variable **generic_psf_services** defined
as a list of services:

```yaml
  generic_psf_services:
    - service1
    - service2
```

## Changelog

* 1.0.0: Role creation. johnnykeats <johnny.keats@outlook.com>
