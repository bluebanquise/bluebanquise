# sosreport

## Description

This role installs the sos CLI & support script used to gather cluster information for support purpose: bluebanquise-sosreport

## Instruction

See the step by step example bellow.

Some variables may be tweaked if necessary:

```
$ cat defaults/main.yml
sosreport_binary_path: /usr/local/bin
sosreport_binary_name: bluebanquise-sosreport
sosreport_output_path: /tmp/bluebanquise-sosreport
sosreport_tempfile_path: /tmp
```

**Warning** The script is gathering information on all servers (management, login and computes).

```
$ cat playbooks/sosreport.yml
- name: Install and configure sosreport
  hosts: "mg_managements"
  roles:
    - name: sosreport

$ ansible-playbook playbooks/sosreport.yml

$ bluebanquise-sosreport
Package manager: dnf
=== Checking script dependencies
=== Checking node dependencies
=== Gathering all nodes sos reports...

sos-collector (version 4.3)
...
Beginning collection of sosreports from 22 nodes, collecting a maximum of 4 concurrently
mgmt1  : Generating sos report...
compute1002 : Generating sos report...
compute10025 : Generating sos report...
compute10006 : Generating sos report...
...
/tmp/bluebanquise-sosreport/sos_error_logs.txt
/tmp/bluebanquise-sosreport/sos-collector-2023-01-30-svfbp.tar.xz

######################################################################
##
## INFO - Please MANUALLY delete temporary report files: /tmp/sosreport
## Please send the /var/logs/bluebanquise-sosreport/bluebanquise-sosreport-2023-01-30.tgz file to Support team
## with the SHA1: 0262e1d8304ad4023c268c39e6b9213ce4de2fce  /var/logs/bluebanquise-sosreport/bluebanquise-sosreport-2023-01-30.tgz
##
######################################################################
```

## Changelog

* 1.0.0: Role creation. Strus38 <indigoping4cgmi@gmail.com>
