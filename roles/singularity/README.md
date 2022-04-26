# Singularity

## Description

Install and configure Singularity or SingularityPRO.

## Pre-requisites

### RPMs of Singularity

Note: RPM is not directly available on Singularity GitHub.
RHEL8 build instructions (example done on management1, but can be done on
another RHEL8 server** anywhere)

```
  dnf groupinstall -y 'Development Tools'
  dnf install openssl-devel libuuid-devel libseccomp-devel wget squashfs-tools cryptsetup golang createrepo
  rpmbuild -tb singularity-3.6.3.tar.gz
  mkdir /var/www/html/repositories/centos/8/x86_64/singularity
  cp /root/rpmbuild/RPMS/x86_64/singularity-3.6.3-1.el8.x86_64.rpm /var/www/html/repositories/centos/8/x86_64/singularity/.
  cd /var/www/html/repositories/centos/8/x86_64/singularity && createrepo .
```

or

### RPMs of SingularityPRO

Note: Sylabs is **NOT** providing a public repository for its RPMs, but is
sending a private repository URL once the software has been bought.
You must first manually download the RPMs using the link provided in the email,
and put them on the server before executing this playbook.

In all cases, it would be also necessary to run the `repositories_client` role
in order to correctly setup the built or downloaded RPMs.

## Usage

Playbook example:

```yaml
  ---
  - name: repositories client
    hosts: "mg_managements,mg_computes"
    roles:
      - role: repositories_client
        vars:
          repositories:
            - singularity

  - name: addons roles to run everywhere
    hosts: "mg_computes"
    roles:
      - role: singularity
```

## ChangeLog

* 1.0.1: Update package name to singularity-ce. strus38
* 1.0.0: Initial version. strus38
