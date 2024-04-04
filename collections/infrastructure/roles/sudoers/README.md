# Sudoers

## Description

This role allows to set sudoers users or groups. It edits */etc/sudoers* file by
adding content at the end.

## Instructions

Set needed sudoers using a list:

```yaml
sudoers:
  # Set 'manu' user as sudoer with passwordless rights
  - name: manu
    privilege: ALL=(ALL) NOPASSWD:ALL
  # Set 'techs' group users as sudier with passwordless rights
  - name: "%techs"
    privilege: ALL=(ALL) NOPASSWD:ALL
```

It is also possible to use dedicated files to store users, using `file_name` key:

```yaml
sudoers:
  # Set 'manu' user as sudoer with passwordless rights
  - name: manu
    file_name: "/etc/sudoers.d/mau"
    privilege: ALL=(ALL) NOPASSWD:ALL
  # Set 'techs' group users as sudier with passwordless rights
  - name: "%techs"
    file_name: "/etc/sudoers.d/techs"
    privilege: ALL=(ALL) NOPASSWD:ALL
  - name: greenwood
    privilege: ALL=(ALL) NOPASSWD:ALL
```

Note that only a single name (aka a single user or a list of comma separated users) can be set by file. It would be possible to bypass this limit by pre-calculating a fact in the role task. Please open a Feature request on github if needed.

## Changelog

* 1.2.1: Fix bug when using list of sudo users as a single name. Code provided by @sgaosdgr. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Allow to create dedicated files for some users. Code from @sgaosdgr. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Updated role to install sudo package. Neil Munday <neil@mundayweb.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
