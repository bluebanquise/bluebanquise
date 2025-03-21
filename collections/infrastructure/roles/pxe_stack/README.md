# PXE Stack

## Description

This role provides the whole PXE stack needed to deploy computers over the network (assuming coupled with a dhcp server).
This role is one of the major role of the BlueBanquise project.

## Features

* Deploy diskfull servers
* Provision diskless servers
* Start tools via PXE
  * memtest (x86_64 only)
  * clonezilla (x86_64 only)
  * alpine live

## Data Model

This role relies on [data model](https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md):
* Section 1 (Networks)
* Section 2 (Hosts definition)
* Section 3.1 (Function Groups)
* Section 3.2 (Hardware Groups)

## Global instructions

This role will deploy all the needed files, binaries, and scripts to deploy
remote hosts using PXE (or even USB and CD boot to trigger PXE on non PXE able systems).

The role takes place just after the dhcp in the PXE deployment, and will
configure all the iPXE chain needed after dhcp provided hosts with next-server
ip address and filename to use.

Note: if using another dhcp server role than the BlueBanquise one, ensure dhcp server target filename is (assuming x86_64) `x86/standard_snponly_ipxe.efi`, or if using a custom iPXE, that it chains to `http://yournextserverip/pxe/convergence.ipxe`.

### Role files location

Files installed by the role are:

* PXE boot files are located in `{{ pxe_stack_htdocs_path }}/pxe/`, with path depending of the operating system.
   * `bin/` directory contains some needed bin files, typically grub2 files for EFI boot.
   * `equipments/` directory contains equipments related files, i.e. ipxe file with group variables, and os configuration files (kickstart, preseed, autoyast).
   * `nodes/` directory contains hosts dedicated files, i.e. ipxe file with hosts dedicated variables.
   * `osdeploy/` directory contains static files, with patterns to boot each kind of supported distributions.
* Basic configuration files are located in /etc/bluebanquise/bootset.
   * `nodes_parameters.yml` contains all nodes PXE needed parameters.
   * `pxe_parameters.yml` contains needed values for scripts to adapt to **current pxe server host** (these parameters do not apply to PXE booted hosts !!).
* Scripts are located in /usr/bin/.

Administrator is also in charge or providing needed OS images for diskfull deployment into the `{{ pxe_stack_htdocs_path }}/pxe/netboots/` folder as detailed bellow.

### Diskfull OS images location

In order to deploy diskfull servers, the role need administrator to provide OS images manually. Procedure depends of each OS.

All these steps have to be done on the PXE server. You can mix OS distributions and architectures (deploy an Ubuntu 22.04 arm64 from an x86_64 RHEL 9 server).
Just be carefull of path, as on Suse servers, path is `/srv/www/htdocs` and not `/var/www/html`, adapt to your needs or deploy the role first so it creates pxe folders for you.

Path targeted by the role configuration files is the following: `http://{next-server}/pxe/netboots/<distribution_name>/<distribution_version or distribution_major_version>/<CPU arch>/`

#### RHEL like

Download DVD standalone iso (or equivalent).
Example for AlmaLinux 9: `https://repo.almalinux.org/almalinux/9/isos/x86_64/AlmaLinux-9-latest-x86_64-dvd.iso`

Create then dedicated folder and mount or copy iso content inside this folder:

```
sudo mkdir -p /var/www/html/pxe/netboots/redhat/9/x86_64/iso
sudo mount /var/lib/bluebanquise/AlmaLinux-9-latest-x86_64-dvd.iso /var/www/html/pxe/netboots/redhat/9/x86_64/iso
```

Only iso content is needed here.

#### Ubuntu

Download Live server iso.
Example for Ubuntu 22.04: `https://releases.ubuntu.com/22.04/ubuntu-22.04.1-live-server-amd64.iso`
Important note: I saw some issues with more recent releases of Ubuntu 22.04. If you encounter issues, please use the 22.04.1 iso version as provided above.

Create then dedicated folder, mv iso, rename it (remove subversion number) and mount it:

```
sudo mkdir -p /var/www/html/pxe/netboots/ubuntu/22.04/x86_64/iso
sudo mv /var/lib/bluebanquise/ubuntu-22.04.1-live-server-amd64.iso /var/www/html/pxe/netboots/ubuntu/22.04/x86_64/ubuntu-22.04-live-server-amd64.iso
sudo mount /var/www/html/pxe/netboots/ubuntu/22.04/x86_64/ubuntu-22.04-live-server-amd64.iso /var/www/html/pxe/netboots/ubuntu/22.04/x86_64/iso
```

Both iso and iso content are needed here.

#### Debian

Download netboot file.
Example for Debian 12: `https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/netboot/netboot.tar.gz`

Create then dedicated folder, extract netboot, and copy kernel and initramfs into it:

```
sudo mkdir -p /var/www/html/pxe/netboots/debian/12/x86_64/
tar xvzf netboot.tar.gz
sudo cp debian-installer/amd64/initrd.gz /var/www/html/pxe/netboots/debian/12/x86_64/
sudo cp debian-installer/amd64/linux /var/www/html/pxe/netboots/debian/12/x86_64/
```

Debian installation relies on external repositories to deploy (it was the same for Ubuntu 18.04 and bellow versions), and so no ISO is needed, only netboot.

#### Suse

Download DVD iso.
Example for OpenSuse Leap 15.4: `https://mirror.its.dal.ca/opensuse/distribution/leap/15.4/iso/openSUSE-Leap-15.4-DVD-x86_64-Build243.2-Media.iso`

Create then dedicated folder, and mount or copy DVD content into it:

```
sudo mkdir -p /var/www/html/pxe/netboots/opensuse/15/x86_64/iso
sudo mount /var/lib/bluebanquise/openSUSE-Leap-15.4-DVD-x86_64-Build243.2-Media.iso /var/www/html/pxe/netboots/opensuse/15/x86_64/iso
```

### Inventory configuration

This role will rely on multiple parts of the inventory, and is probably the most "invasive" role of the whole collection.

* equipment parameters are used for each equipment group. All
  boot configuration is made relying on it (operating system, cpu architecture,
  console, kernel parameters, etc.). It is recommended to ensure coherency of
  the equipment files.
* authentication parameters are used to provide admin password and default ssh
  authorized key.
* (optional) hosts **network_interfaces** dedicated variables, to be able to force static
  ip address at kernel boot.

Configuration can be made either as pxe_stack variables level, for a simple cluster, or using equipment groups, for a more advanced cluster.

#### Ultra simple configuration (homogeneous cluster)

It is possible to skip equipment groups creation and only rely on the `all` group.
In that case, simply precedence the role embeded default variables, that will apply to all hosts that are not in an equipment group.
In your `inventory/group_vars/all`, create file `pxe_stack.yml` with the following content:

```yaml
pxe_stack_hw_equipment_type: server  # Servers are always added to PXE
pxe_stack_os_operating_system:
  distribution: ubuntu
  distribution_version: 22.04        # Minor version is not mandatory but usefull for Ubuntu (22 == 22.04 or 22.10?)
  distribution_major_version: 22

pxe_stack_hw_console:                # If using a remote server with a serial console, set it here
pxe_stack_os_kernel_parameters:      # If specific parameters are needed. I recommend to add least 'nomodeset' if server have an attached GPU
pxe_stack_hw_kernel_parameters:      # If you need to specify it as hw level instead of os level (for inventory readbility)

pxe_stack_os_keyboard_layout: us     # us, fr, etc.
pxe_stack_os_system_language: en_US.UTF-8  # You should not update this if you want to google issues...
pxe_stack_time_zone: Europe/Brussels       # Ensure time zone set here is coherent for your whole cluster

pxe_stack_enable_root: false               # Disable root by default, and create a sudo user instead
pxe_stack_sudo_user: bluebanquise          # Name of the sudo user
pxe_stack_sudo_user_home: /var/lib/bluebanquise    # $HOME of the sudo user. Avoid /home/XXXX to prevent later issues.
pxe_stack_sudo_is_passwordless: true       # Set sudo user as passwordless sudoer

pxe_stack_os_admin_ssh_keys:
  - XXXXXXXXXXXXXXX                        # Add here your server(s) !! PUBLIC !! ssh key(s)

pxe_stack_os_access_control: enforcing     # If SELinux or AppArmor (RHEL / Ubuntu only) should be let activated
pxe_stack_os_firewall: true                # If firewall (RHEL only for now) should be let activated

# WARNING! If nothing is set for partitioning,
# automatic partitioning will be activated.
pxe_stack_os_partitioning:                 # Set partitioning. Use raw OS format: kickstart for RHEL, preseed for Debian, etc.
                                           # Leave empty for automated partitioning

pxe_stack_os_pxe_images_root:              # Specify a custom images root for PXE other than default http://${next-server}/pxe/netboots/${eq-distribution}/${eq-distribution-version}/${eq-architecture}/
pxe_stack_os_pxe_repository_root:          # Specify a custom os base repository root for PXE other than default http://${next-server}/repositories/${eq-repositories-environment}/${eq-distribution}/${eq-distribution-version}/${eq-architecture}/
```

#### Equipments groups

If cluster have multiple different equipments, it is then mandatory to use hardware and os groups, to allow the role to generate virtual equipment groups.

A specific Ansible group, prefixed by `hw_` have to be created for each kind of hardware equipment present in the cluster. An hardware group can be seen as a storage for the following variables:

* Hardware related variables (kernel parameters, partitioning, iPXE specific tunings, console, etc.)

A specific Ansible group, prefixed by `os_` have to be created for each kind of operating system installation settings present in the cluster. An os group can be seen as a storage for the following variables:

* OS related variables (OS version to be used, enable firewall, ssh keys to be deployed, sudo user, etc.)

To be taken into account by this role, an host MUST be in one hardware group and one os group at the same time.
However, an host CANNOT be in 2 hardware or os groups at the same time. Create as many groups as necessary to respect this rule.

Lets take as an example a cluster with 2 kind of servers, one kind based on Ubuntu 22.04 with GPUs (hosts c1 to c10) and another one based on RHEL 9 for CPU only (hosts c11 to c100), and both based on the same server hardware (ASUS_G9).

This will mean 2 virtual equipment profiles :

* `hw_ASUS_G9_with_os_ubuntu_22.04_GPU`
* `hw_ASUS_G9_with_os_rhel9`

Create/append to groups file, at `inventory/cluster/groups/hw` with the following content:

```INI
[hw_ASUS_G9]
c[1:100]
```

Then create/append to groups file, at `inventory/cluster/groups/os` with the following content:

```INI
[os_ubuntu_22.04_GPU]
c1
c2
c3
c4
c5
c6
c7
c8
c9
c10

[os_rhel9]
c[11:100]
```

Then create groups dedicated folders:

```
mkdir inventory/group_vars/hw_ASUS_G9 -p
mkdir inventory/group_vars/os_ubuntu_22.04_GPU -p
mkdir inventory/group_vars/os_rhel9 -p
```

You can store any variables related to these groups in these folders.

Populate now harwdare variables for the hardware group.
Create file `inventory/group_vars/hw_ASUS_G9/fw.yml` with the following content:

```yaml
hw_equipment_type: server
hw_console: console=tty0 console=ttyS1,115200
```

Populate now os variables for the os groups.
Create file `inventory/group_vars/os_ubuntu_22.04_GPU/os.yml` with the following content:

```yaml
os_operating_system:
  distribution: ubuntu
  distribution_version: 22.04
  distribution_major_version: 22

os_kernel_parameters: nomodeset

os_keyboard_layout: us
os_system_language: en_US.UTF-8

os_admin_ssh_keys:
  - XXXXXXXXXXXXXXX # Public ssh keys to deploy

os_access_control: disabled
os_firewall: false

os_target_disk: /dev/sda
os_partitioning: # Leave empty for auto partitioning, that relies on os_target_disk if exist, or auto choose disk if not
```

Then create file `inventory/group_vars/os_rhel9/os.yml` with the following content:

```yaml
os_operating_system:
  distribution: redhat
  distribution_major_version: 9

os_kernel_parameters:

os_keyboard_layout: us
os_system_language: en_US.UTF-8

os_admin_ssh_keys:
  - XXXXXXXXXXXXXXX # Public ssh keys to deploy

os_access_control: disabled
os_firewall: false

os_partitioning: |
  clearpart --all --initlabel
  autopart --type=plain --fstype=ext4
```

And apply the role. If you need to set timezone, create file `inventory/group_vars/all/cluster_global.yml` and add the following content inside it:

```yaml
bb_time_zone: Europe/Brussels
```

Since it is a global cluster setting, time zone is not defined at equipment level.

#### Tuned deployment iso paths

It is possible to tune isos path used to deploy OS (using for example a public repository, etc.).

Some variables are available for that:

* Optional `os_pxe_images_root` defined at os groups level that precedence optional `pxe_stack_os_pxe_images_root` defined at group_vars/all level. If both not defined, default is `http://${next-server}/pxe/netboots/${eq-distribution}/${eq-distribution-version}/${eq-architecture}/`.
* Optional `os_pxe_images_root_iso` defined at os groups level that precedence optional `pxe_stack_os_pxe_images_root_iso` defined at group_vars/all level. If both not defined, default is `iso`.

#### Raw content

You can add raw content to auto install files using the `os_autoinstall_raw_content`.
Please note that this is RAW. So you HAVE TO adapt the content to the target distribution.

* For RHEL, this is Kickstart syntax (bottom of the kickstart file).
* For Debian, this is preseed syntax (bottom of the preseed file).
* For Ubuntu, this is curtin/cloud-config syntax (already placed under `autoinstall` and auto indented by 2 space).
* For SUSE, this is autoyast syntax (inside `<profile>...</profile>`).

It is also possible to fully replace autoinstallation file, by setting the `os_autoinstall_raw_file` value.
If set, this multi lines string will **FULLY** replace the content of the BlueBanquise generated autoinstallation file.
Of course, it is expected that user will provide syntax matching target os (kickstart, preseed, autoyast, or cloudinit/curtin).

#### Proxy during PXE

It is possible to set an http proxy server during PXE.
2 main variables are available:

* `os_pxe_repository_proxy`
* `os_pxe_proxy`

Please always include the `http://` part of the url.
Note that in most cases, you can also include user and password if exist (http://user:password@proxy.example.com:3128 for example).

Note however that due to the way all auto installations are operating, behavior is not always the same. I did my best to propose working solutions.

* For Ubuntu, `os_pxe_repository_proxy` will be set to `proxy` key of *user-data* file and so used to reach apt repositories (refer to https://ubuntu.com/server/docs/install/autoinstall-reference). `os_pxe_proxy` will be set as kernel parameters `http_proxy={{os_pxe_proxy}} https_proxy={{os_pxe_proxy}}`.
* For Debian, `os_pxe_repository_proxy` will be written to `d-i mirror/http/proxy` key of preseed file, and so will apply to reach installation packages repository. `os_pxe_proxy` will be passed as kernel arguments : `http_proxy={{os_pxe_proxy}} https_proxy={{os_pxe_proxy}}` and so should be exported as environment variables during the whole process.
* For RHEL, `os_pxe_proxy` will be passed to `inst.proxy` kernel parameter. However, documentation is not clear about impacted elements (refer to https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html-single/performing_a_standard_rhel_9_installation/index). Since `os_pxe_proxy` cannot be passed as standard kernel arguments on RHEL (init filters this), this specific kernel parameter couple (http_proxy and https_proxy) is not available on RHEL systems.
* For SUSE, `os_pxe_repository_proxy` will be set to `<proxy>...</proxy>` key of autoyast file (refer to https://doc.opensuse.org/projects/autoyast/#Configuration-Network-Proxy), while `os_pxe_proxy` will be set to kernel parameters as `proxy={{os_pxe_proxy}}` (refer to https://en.opensuse.org/SDB:Linuxrc#p_proxy).

If some of these settings do not match your needs or are not working as expected, please open an issue.

#### External netboot images or/and core repository during PXE

It is possible to pull netboots and core repositories from an external or custom source using `os_pxe_images_root` and `os_pxe_repository_root` variables.
The path need to be a full http url, and may contains iPXE variables.

For example:

```yaml
os_pxe_images_root: http://10.10.0.1/RHEL9_iso/
os_pxe_repository_root: http://${next-server}/rhel_core_repo/9/
```

#### Additional packages during autoinstall

It is possible to set a list of packages to be installed during the automated installation.

To do so, simply define the `os_autoinstall_packages` list the following way, adapting the list of packages to your needs:

```yaml
os_autoinstall_packages:
  - curl
  - wget
  - vim
```

Of course, it is expected the packages you ask in the list are available in the repositories exposed to the auto-installer.

### bluebanquise-bootset usage

Once the role is deployed, and hosts gathered into `/etc/bluebanquise/bootset/nodes_parameters.yml`, the **bluebanquise-bootset** tool can be used to manipulate remote hosts PXE boot. By default, 3 states can be defined for each host:

* osdeploy: the remote host will deploy/redeploy its operating system, using inventory equipment parameters of its equipment profile group.
* disk: the remote host will boot on disk. This parameter is automatically set after a successful **osdeploy**.
* diskless: the remote host will boot using a diskless mechanism. This diskless boot is generic, and is handled by an optional external role.

Again, consider that if you set an host to osdeploy, and that it succeed its deployment, stack will automatically set the host into disk boot for next boot, to avoid infinite reinstallation loop (this is done using a CGI script set along apache http server).

To get bluebanquise-bootset help, use:

```
bluebanquise-bootset -h
```

To ask an host to deploy/redeploy its operating system, use:

```
bluebanquise-bootset -n c001 -b osdeploy
```

With c001 the target host to be redeployed.

To set this host to boot on disk, use:

```
bluebanquise-bootset -n c001 -b disk
```

It is also possible to work on a range of host, using nodeset formatting:

```
bootset-bootset -n c001,c002,c[010-020],login1 -b disk
```

If some inventory parameters related to the host have been updated recently, it may be required to force files regeneration instead of simply modifying them. To do so, use:

```
bootset-bootset -n c001 -b osdeploy -f update
```

Also, on some "difficult" networks, system administrator may require to force static ip at boot. This can be achieved using:

```
bootset-bootset -n c001 -b osdeploy -f network
```

Or in combination with update, using comma separated:

```
bootset-bootset -n c001 -b osdeploy -f update,network
```

The tool is relatively verbose, and should provide all needed information on the fly on what it is doing.

Last part, regarding diskless. An image name need to be provided:

```
bootset-bootset -n c001 -b diskless -i myimage
```

Diskless part is detailed later in this README.

### iPXE chain

PXE part of the **BlueBanquise** stack relies heavily on iPXE, and its chain mechanism. This chain has multiple purposes:

* Most important, it is verbose, and can be manually manipulated or followed (watching http server logs).
* It is flexible, and can adapt to nearly any configuration (disk boot, os deployment, diskless, ...).
* It can operate on all hardware, from server to laptop. It can even be started from USB or CD image for non PXE able systems.

Some steps may seems weird or unnecessary, but are here on purpose: verbosity and debug, as PXE part is always the trickiest.

Some vocabulary: in the following document, **chain** or **chaining** refers to the iPXE mechanism that download and execute a new file, after the current one.

Also, all files root is assumed `/var/www/html/pxe` on the next-server (the server on which this pxe_stack role has been deployed).

The whole process can be resumed in one detailed schema:

![ipxe_chain](images/iPXE_chain.png)

To be macroscopic:

* The remote host boot over PXE, in EFI/legacy-bios, using its own PXE/iPXE rom.
* The dhcp deployed by BlueBanquise (or your own) will provide the host with the **BlueBanquise** iPXE rom. This iPXE rom contains an EMBED script that will display the logo, get an ip from the dhcp server, show some information, and chain to file *convergence.ipxe*.
* *convergence.ipxe* will simply get the current architecture. This operation cannot be done into the EMBED script has it needs some logic, that could bug. Sys admin need to easily debug this without the need to rebuild iPXE roms. Then iPXE chain to *nodes/${hostname}.ipxe* with *hostname* the hostname provided by the dhcp server.
* *nodes/${hostname}.ipxe* will define all host dedicated parameters, and also what host should do: boot on disk, deploy os, or boot in diskless. Then iPXE chain to *equipments/${equipment-profile}.ipxe*, with *equipment-profile* a variable defined in the current file.
* *equipments/${equipment-profile}.ipxe* contains the host equipment profile group parameters, like operating system, console, kernel parameters, etc. Then iPXE chain to *menu.ipxe*.
* *menu.ipxe* will display a basic menu on screen, with default set to what node is expected to do (this was gathered in *nodes/${hostname}.ipxe*). Timeout is 10s by default before host execute the expected action. Then, iPXE chain to:
   * *osdeploy/${eq-distribution}_${eq-distribution-major-version}.ipxe* if host needs to deploy/redeploy its operating system. These osdeploy files are dynamic, and adapt to parameters gathered in host dedicated file and host equipment file.
   * *diskless/images/${diskless-image}/boot.ipxe* if host needs to boot in diskless.
   * *sanboot --no-describe --drive 0x80* if host is legacy/bios/pcbios based. This is a simple command that boot on disk.
   * *bin/${arch}/grub2_efi_autofind.img* if host is EFI based. This grub2 image will look for a disk with a know operating system, and boot on it.

In case of an OS deployment, if this deployment succeed, in the post install script section, remote host will ask, using a curl command on its side and an CGI python script on server side (*/var/www/cgi-bin/bootswitch.cgi*), to boot next to disk. This CGI python script will simply edit *node/${hostname}.ipxe* file and change its default boot to **bootdisk**.

All files are manually editable. Also, note that an unregistered host (so no hostnames provided by the dhcp) will try to load *nodes/.ipxe* file. By default, this file will simply provide an iPXE shell, but system administrator can tune this file to specific purposes.

To follow the deployment process, simply tail -f logs of http server, and see the whole process occurring.

### Diskless

To enable diskless, simply set variable `pxe_stack_enable_diskless` to *true* and deploy the role.
All diskless is then managed by the **bluebanquise-diskless** tool.

#### Introduction and general concept

bluebanquise-diskless tool is made to manage diskless images life cycles, from creation to production and maintenance.

Workflow is the following, assuming user wishes to boot a pool of nodes with the same live image:

* Step 1: user import a bootstrap image (read only image).
* Step 2: user generates a new reference image from a bootstrap image (read write image).
* Step 3: user tune the reference image, using NFS diskless on a single node of the target pool, or using chroot into local image folder.
* Step 4: user generates a new live image from a reference image (read only image).
* Step 5: user can now boot all nodes of the pool with the live image.

Each step is explained in the following part.

#### Step 1: user import a bootstrap image

A bootstrap image is a ready to boot image, that can be bare minimal, or fully customized system.
It is a tar.gz file of an image chroot, that contains at its root a metadata.yaml file with vital information of the image.
A bootstrap image contains at least:

- Bootable chroot of the target system.
- The kernel and initramfs needed to boot.
- Needed packages to rebuild an updated kernel with diskless modules.
- A packages manager (dnf, apt, zypper, etc).
- A network daemon (NetworkManager, systemd-networkd, etc).
- The openssh server (sshd), enabled at boot.

It is then up to packager to add additional elements into image.

BlueBanquise project provides basic bootstrap images at https://bluebanquise.com/diskless

Once imported, bootstrap images are stored by default into `/var/lib/bluebanquise/diskless/bootstrap_images/` folder.

Bootstrap images are used as source to create new reference images (also known as golden images).

#### Step 2: generate a reference image

A reference image is a read write image, that will be tuned by user to create desired final images.
This means for example:

* Install new updated kernels in image.
* Install packages, drivers, etc.
* Setup configuration files.
* Setup mounting points.
* Etc.

bluebanquise-diskless tool simply extracts content of a bootstrap image and create the bootable/chrootable folder of new reference image into `" + tool_parameters['nfs_path'] + "/image_name` folder.
A dedicated folder into `/var/www/html/pxe/diskless` directory is also created, and contains metadata and minimal needed to boot reference image via NFS if needed.

#### Step 3: tune a reference image

**WARNING**: it is very important to understand 2 key concepts here:

1. A reference image is going to be later converted into a live image, which will be booted by all nodes of a pool.
This means image must NOT be identified to a specific node. Do not set static ip nor static hostname in a reference image.
If using BlueBanquise roles, this can be avoided skipping "identify" tag when using ansible-playbook command.
2. A reference image, once converted to live, can be downloaded by standard users, making its content readable by everyone.
This means image must NOT contain any sensitive data, like private keys, private certificates, clear passwords, etc.
If using BlueBanquise roles, this can be avoided skipping "secret" tag when using ansible-playbook command.

Once generated, there are 2 ways to tune a reference image. I personally recommend using NFS diskless to install packages, kernel, and drivers.
A full running system mounted over NFS might be slow, but it will successfully install packages and drivers/kernel modules, and load them to ensure everything works as expected.
Note that it is also a hard requirement if CPU architecture of image is not the same than current system.
Chroot method should only be used to do quick modifications, as many packages’ scripts will fail under chroot, leading to unexpected issues later in production.

##### Using NFS diskless

An entry in tool allows to link a reference image to a specific node of the target pool, and generate a temporary password to be able to login once booted.
Assuming for example that target nodes pool is c[001-100], then user should request tool to link image to node c001.
Then use bluebanquise-bootset to request this node to boot over diskless on this image:

```
bluebanquise-bootset -b diskless -i my_reference_image -n c001
```

Then boot c001 node. Once booted, you should be able to login via ssh using provided password at link step.
You can now deploy an ssh key on remote node, and start using ansible-playbook or any other commands to tune it.
Remember to skip "identify" and "secret" tags:

```
ansible-playbook --become --skip-tags identify,secret /path/to/playbook.yml
```

##### Using chroot

You can also directly chroot into image using:

```
sudo chroot /nfs/diskless/my_reference_image
```

Remember that this is only possible if image CPU architecture is the same than current host.
You can also directly edit files into `/nfs/diskless/my_reference_image` folder for quick changes.

##### Update kernel

It might be needed to update image kernel. Again, I recommend to do that on an NFS booted image.

Once new kernel has been installed, a manual step is required to ensure it will load at next boot, as diskless images do not use grub2 to configure next kernel boot.

Use bluebanquise-diskless tool and select **Update a reference image default kernel** entry.
Select your image, and tool will display available kernels for this image. Simply choose your new kernel.

Now, reboot the node, and check it has booted on the new kernel.

Note on this process, for advanced users: bootstrap images contain specific file (`/etc/dracut.conf.d/bluebanquise for RHEL images`) that forces diskless modules to be installed in new initramfs during kernel update process.

#### Step 4: generate a new live image from a reference image

Once reference image is ready, and user ensured all kernel modules are properly running, reference image can be used as source for final live image.

**WARNING**: be sure to power off NFS diskless node linked on the reference image before using image to generate the live version.

A live image is loaded via http by all nodes of the target pool at boot, and stored in ram memory. Then, an overlay FS is configured over image to allow live **non reboot persistent** system modifications.

Use the bluebanquise-diskless tool dedicated entry to generate the new live image.

Once image is generated, use bluebanquise-bootset tool to request all nodes of the pool to boot from this live image:

```
bluebanquise-bootset -b diskless -i my_live_image -n c[001-100]
```

#### Step 5: boot all nodes of the pool

You can now boot all nodes. Note that depending of network capabilities, this process can take some time.
You can monitor live image downloads by watching apache server logs:

On RHEL/Suse like systems:

```
sudo tail -f /var/log/httpd/*
```

On Debian/Ubuntu like systems:

```
sudo tail -f /var/log/apache2/*
```

Once all nodes are booted, you need to finalize their configuration, by setting up node dedicated settings and secrets.
If using BlueBanquise roles, simply apply playbook with missing tags:

```
ansible-playbook --become --tags identify,secret /path/to/playbook.yml
```

#### Debug and errors

##### Package fail to install in NFS diskless

Some sensitive system packages might refuse to install while in NFS due to NFS cap limitations.

For example, on RHEL 9, shadow-utils rpm will fail to upgrade:

```
[bluebanquise@c001 ~]$ dnf update -y
...
warning: /etc/shadow created as /etc/shadow.rpmnew

  Running scriptlet: setup-2.13.7-9.el9.noarch                                                                                70/193
  Upgrading        : shadow-utils-2:4.9-6.el9.x86_64                                                                          71/193
Error unpacking rpm package shadow-utils-2:4.9-6.el9.x86_64
error: unpacking of archive failed on file /usr/bin/newgidmap;64944fc1: cpio: cap_set_file
error: shadow-utils-2:4.9-6.el9.x86_64: install failed
[bluebanquise@c001 ~]$
```

It is possible to see that this even fail with nfs 4.2 mount:

```
[bluebanquise@c001 ~]$ nfsstat -m
/ from 10.10.0.1:/nfs/diskless/my_image
 Flags: rw,relatime,vers=4.2,rsize=1048576,wsize=1048576,namlen=255,hard,proto=tcp,timeo=600,retrans=2,sec=sys,clientaddr=10.10.0.8,local_lock=none,addr=10.10.0.1
[bluebanquise@c001 ~]$
```

Solution is to install the failing package using chroot method on NFS server:

```
bluebanquise@mgt1:/$ sudo chroot /nfs/diskless/my_image
bash-5.1# dnf update
Failed to set locale, defaulting to C.UTF-8
Dependencies resolved.
================================================================ Package          Arch       Version           Repository  Size
================================================================Upgrading:
 shadow-utils     x86_64     2:4.9-6.el9       baseos     1.1 M

Transaction Summary
================================================================Upgrade  1 Package

Total download size: 1.1 M
Is this ok [y/N]: y
Downloading Packages:
shadow-utils-4.9-6.el9.x86_64.r 5.6 MB/s | 1.1 MB     00:00
----------------------------------------------------------------Total                           3.2 MB/s | 1.1 MB     00:00
Running transaction check
Transaction check succeeded.
Running transaction test
Transaction test succeeded.
Running transaction
  Preparing        :                                        1/1
  Upgrading        : shadow-utils-2:4.9-6.el9.x86_64        1/2
  Cleanup          : shadow-utils-2:4.9-5.el9.x86_64        2/2
  Running scriptlet: shadow-utils-2:4.9-5.el9.x86_64        2/2
  Verifying        : shadow-utils-2:4.9-6.el9.x86_64        1/2
  Verifying        : shadow-utils-2:4.9-5.el9.x86_64        2/2

Upgraded:
  shadow-utils-2:4.9-6.el9.x86_64

Complete!
bash-5.1#
```

##### Cleaning folders

The tool has been made with a sys admin philosophy. I tried to avoid any complex steps, and in case of crash, the tool will not cleanup the files, so you can investigate and retry failed command.
This however could lead to issues, so in case of crash, remember to check the following folders for remaining zombie files to be cleaned:

* /var/lib/bluebanquise/diskless/bootstrap_images/
* /var/lib/bluebanquise/diskless/bootstrap_images/tmp/
* /var/www/html/pxe/diskless/
* /nfs/diskless/

### Other tools

The role by default will install other tools, useful for system admininstrator:

* CloneZilla Live
* Alpine Live
* Memtest

You can disable their installation using the following variables:

```yaml
pxe_stack_enable_clonezilla: true
pxe_stack_enable_alpine: true
pxe_stack_enable_memtest: true
```

### Sudo user

You can configure the target sudo user by setting these variables:

```yaml
pxe_stack_enable_root: false
pxe_stack_sudo_user: bluebanquise
pxe_stack_sudo_user_home: /var/lib/bluebanquise
pxe_stack_sudo_user_uid: 477
pxe_stack_sudo_user_gid: 477
```

Note that using an home folder into /home for the bluebanquise sudo user can be dangerous as /home is often mounted on a cluster, and so would colide with local bluebanquise user home.

## Changelog

* 1.18.4: Fix Formatting for Kernel Parameters in iPXE Template. Leo Magdanello <lmagdanello40@gmail.com>
* 1.18.3: Fix dublicated PermitRootLogin in RH sshd_config. Thiago Cardozo <boubee.thiago@gmail.com>
* 1.18.2: Fix opensuse leap autoyast. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.18.1: Fix ubuntu 24.04 support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.18.0: Add ubuntu 24.04 support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.17.3: Revert part of 1.17.2 adds, since not stable. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.17.2: Fix python version for old systems. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.17.1: Fix global logic. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.17.0: Allow advanced custom iso paths. <jp.mazzilli@gmail.com> and <benoit.leveugle@gmail.com>
* 1.16.5: Several fixes to bluebanquise-diskless (version 2.0.7). Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.16.4: Ensure bluebanquise-bootset is run as root/sudo. <patrick.begou@univ-grenoble-alpes.fr>
* 1.16.3: Fix bug in kickstart (reported by jpm38). Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.16.2: Fix owner and group for bluebanquise .ssh directory. <patrick.begou@univ-grenoble-alpes.fr>
* 1.16.1: Fix proxy settings. Bug reported by @erkrali. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.16.0: Allow to pull netboot and core repo from a custom URL. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.15.0: diskless.yml task must be optional <jp.mazzilli@gmail.com>
* 1.14.0: Set default value for images-root <jp.mazzilli@gmail.com>
* 1.13.0: Add packages during autoinstall support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.12.1: Fix missing clonezilla directory. Abatcha Olloh <abatchaolloh@outlook.fr>
* 1.12.0: Add raw content and proxies. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.11.1: Fix kernel upgrade option in bluebanquise-diskless. Giacomo Mc Evoy <gino.mcevoy@gmail.com>
* 1.11.0: Add ability to select target disk with auto partitioning. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.10.0: Add ability to set sudo user uid and gid. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.5: Switch RHEL from atftp to native tftp-server (fix from @sgaosdgr). Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.4: Fix bad variable name for console. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.3: Improve code by preventing possible crashes. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.2: Fix missing service for nfsv3 in RHEL firewall. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.1: Fix introduced bug in autoyast. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.9.0: Adapt to hw os split. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.8.5: replace hard-coded string 'equipment_' with adequate var. #sla31
* 1.8.4: Improve documentation. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.8.3: Allow all distributions to erase default repositories. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.8.2: RedHat missing rpm. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.8.1: Update to BB 2.0 format again. Alexandra Darrieutort <alexandra.darrieurtort@u-bordeaux.fr>, Pierre Gay <pierre.gay@u-bordeaux.fr>
* 1.8.0: Update to BB 2.0 format. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.7.0: Add force main NIC and fix gateway. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.4: Improve idempotency of role pxe_stack. #sla31
* 1.6.3: Prevent crash when empty ep group. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.6.2: Added pxe_stack_opensuse_preserve_sources_list variable to handle activation of online repos in autoyast files. Neil Munday <neil@mundayweb.com>
* 1.6.1: Updated to work with both SLES and OpenSUSE and install sudo package if sudo use is enabled. Neil Munday <neil@mundayweb.com>
* 1.6.0: Allow to choose between root or sudo user. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.5.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.1: Extend bootset support for custom htdocs path. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.4.0: Added OpenSuSE support. Neil Munday <neil@mundayweb.com>
* 1.3.7: Allow manipulating sources list in autoinstall on Ubuntu. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.6: Fix missing efi check in auto install files. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.5: Fix missing tftp path for Ubuntu. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.4: Fix missing efi bootorder management for Ubuntu. johnnykeats <johnny.keats@outlook.com>
* 1.3.3: Add bootset as package. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.2: Prevent unsorted ranges. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.1: Adapt role to handle multiple distributions. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.3.0: Add Ubuntu support. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.2.0: Add compatibility for multiple OS distributions (RedHat like). Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.7: Update configuration files path, to prevent issues with multiple icebergs. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.6: Add ability to install other tftp server than atftp. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.5: Update role to match $basearch, add status feat to bootset. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.4: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.1.3: Clean. johnnykeats <johnny.keats@outlook.com>
* 1.1.2: Add support of major distribution version. Bruno <devel@travouillon.fr>
* 1.1.1: bootset.py refactoring. Adrien Ribeiro <adrien.ribeiro@atos.net>
* 1.1.0: Rewamped the whole role. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Add Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
