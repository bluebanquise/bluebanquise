# Nvidia

## Description

This role install Nvidia drivers and optionally Cuda.

To use this role, you need to have downloaded Nvidia packages and add them
to your local repositories.
You can download drivers at https://www.nvidia.com/Download/index.aspx?lang=en-us

## Instructions

By default, Cuda is not installed by the role. To enable Cuda installation, set
`nvidia_install_cuda` to true.

## Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
