# GPU

## Description

This role install GPU related drivers and tools.

Role currently only supports RHEL distributions. If you need other distributions, please notify me via a feature request.

## Instructions

To specify gpu vendor to setup, simply set `gpu_vendor` variable to target vendor. Currently,
variable supports the following vendors:

* nvidia

Refer to each vendor section bellow for detailed setup.

### Nvidia

Role will deploy Nvidia drivers and optionally Cuda.
Procedure is different for each distribution.

To use this role, you need to have downloaded Nvidia packages and add them
to your local repositories (see bellow). Beware not to destroy groups inside Nvidia repositories.
You can download drivers at https://www.nvidia.com/Download/index.aspx?lang=en-us

By default, Cuda is not installed by the role. To enable Cuda installation, set
`nvidia_install_cuda` to true. This assumes that Cuda has been downloaded and added to repositories.
You can download Nvidia toolkit at https://developer.nvidia.com/cuda-downloads.

**BEWARE**: ensure the toolkit used and the driver in repositories match and are compatible.
When downloading driver, on main Nvidia website, linked Cuda version should be mentioned.

#### RHEL

We will assume here RHEL version is 8, but procedure is the same for RHEL 7 or RHEL 9.
Please adapt commands to your needs, this is a main and non strict guideline.

Note that you need EPEL repositories to be enabled on your system.
If your system is air-gapped, then you need at least `dkms` package from EPEL to be available in a repository.

Download the driver for related RHEL distribution on main website.
You should get a huge rpm (around 500Mb).
This rpm should not be installed directly, but extracted.

Upload it into your home on repository server.

Create a working directory, move rpm inside, and extract it:

```
mkdir nvidia_tmp
cd nvidia_tmp
mv $HOME/nvidia-driver-local-repo-rhel8-515.65.01-1.0-1.x86_64.rpm .
rpm2cpio nvidia-driver-local-repo-rhel8-515.65.01-1.0-1.x86_64.rpm | cpio -idmv
```

Now, grab the repository, and push it into your repositories http server folder. For example:

```
cp -a var/nvidia-driver-local-repo-rhel8-515.65.01/ /var/www/html/repositories/redhat/8/x86_64/nvidia
```

**IMPORTANT**: note that we are using Nvidia repository and repodatas without modifying them.
Do not `createrepo` on it or you will lose Nvidia's groups.

Now, simply register this new repository into inventory:

```yaml
bb_repositories:
  - name: nvidia
    # baseurl: http://repository_server_ip/repositories/redhat/8/x84_64/nvidia/
```

Note that baseurl will be automatically generated if inventory is fully populated. If not, uncomment and force url manually.

You can also force Nvidia GPG key check, but this forces you to set URL manually:

```yaml
bb_repositories:
  - name: nvidia
    # baseurl: http://repository_server_ip/repositories/redhat/8/x84_64/nvidia/
    gpgcheck: true
    gpgkey: http://repository_server_ip/repositories/redhat/8/x84_64/nvidia/0149E63F.pub
```

Set then `gpu_vendor` variable to `nvidia` inside inventory for target group of hosts, and apply playbook after
having applied first `repositories_client` role to ensure this new repository has been added on nodes.

## Changelog

* 1.0.1: Simple bugfix on task calling. Lucas Santos <lucassouzasantos@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
