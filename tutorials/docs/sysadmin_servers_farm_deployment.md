# Servers farm deployment

This tutorial tries to teach how to install manually a basic **servers farm**, also called a **cluster**.

This tutorial will focus on simplicity, lightness and good practices.
All software used are very common and when facing an error, a quick look on the
web will most of the time solves the issue.

If you face any issues with this tutorial, do not hesitate to open an issue on the BlueBanquise github.

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>This tutorial is based on EL 9 OS (RHEL 9, RockyLinux 9, AlmaLinux 9, etc).
Most of this page is portable on other distributions.
In annexes, I will detail how to deploy via PXE the other common distributions.</p>
    </div>
</div> -->

This tutorial is based on EL 9 OS (RHEL 9, RockyLinux 9, AlmaLinux 9, etc) and on Ubuntu 24.04.
Most of this page is portable on other distributions. An HPC cluster can run on any kind of Linux distribution. Just make sure that the hardware you have is compatible (mostly GPU and interconnect if present, check vendor provides drivers).
In annexes, I will detail how to deploy via PXE the other common distributions.

## Hardware requirements

The following hardware is needed to perform this training:

**Minimal configuration to do the training:**
Laptop/workstation with 8Go RAM and 40Go disk. VT-x instructions MUST be activated in the BIOS. VMs will be used.
Note that with this configuration, you will need to tweak ram allocated to each VM after each PXE, but this is feasible.

**Recommended configuration to do the training:**
Laptop/workstation with 16go or more, and 100Go disk. VT-x instructions MUST be activated in the BIOS. VMs will be used.

**Best configuration to do the training:**
A real cluster, with real physical servers. \o/

## Useful commands

General commands:

* Load a kernel module : `modprobe mymodule -v`
* Unload a kernel module : `modprobe -r mymodule`
* List loaded kernel modules : `lsmod`
* Check listening processes and port used : `netstat -aut`
* Get hardware information (use –help for more details) : `inxi` or `dmidecode`
* Check network configuration : `ip add`
* Open a screen : `screen -S sphen`
* List screens : `screen -ls`
* Join a screen : `screen -x sphen`
* Detach a screen : use `Ctrl+a+d` on keyboard
* Change keyboard language in current terminal : `loadkeys fr` (azerty), `loadkeys us` (qwerty)
* Remount / when in read only (often in recovery mode) : `mount -o remount,rw /`
* Apply a patch on a file : `patch myfile.txt < mypatch.txt`
* Do a patch from original and modified file : `diff -Naur original.txt modified.txt`
* Get EFI boot order from os: `efibootmgr`
* Change EFI boot order from os: `efibootmgr -o XXXX,YYYY,ZZZZ,...`

IPMI commands for remote control (old hardware):

* Boot choice, very useful for very slow to boot systems (`bios` can be replaced with `pxe` or `cdrom` or `disk`) : `ipmitool -I lanplus -H bmc5 -U user -P password chassis bootdev bios`
* Make boot persistent : `ipmitool -I lanplus -H bmc5 -U user -P password chassis bootdev disk options=persistent`. Note: remember that UEFI systems can dynamically change boot order.
* Control power (`reset` can be replaced with `soft` or `cycle` or `off` or `on` or `status`) : `ipmitool -I lanplus -H bmc5 -U user -P password chassis power reset`
* Activate remote console (use `Enter`, then `&` then `.` to exit) : `ipmitool -H bmc5 -U user -P password -I lanplus -e \& sol activate`

More: [IPMI tool how to](https://support.pivotal.io/hc/en-us/articles/206396927-How-to-work-on-IPMI-and-IPMITOOL)

Note: when using sol activate, if keyboard does not work, try using the same command into a screen, this may solve the issue (strangely...).

RedFish commands for remote control (new hardware):

```
SERVER="my-server"
USER="ADMIN"
PASS="ADMIN"

# ON
curl -si -u $USER:$PASS -k -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"Action": "Reset", "ResetType": "On"}' https://$SERVER/redfish/v1/Systems/1/Actions/ComputerSystem.Reset

#OFF
curl -si -u $USER:$PASS -k -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"Action": "Reset", "ResetType": "ForceOff"}' https://$SERVER/redfish/v1/Systems/1/Actions/ComputerSystem.Reset

# Other methods available:
curl -si -u $USER:$PASS -k -XGET https://$SERVER/redfish/v1/Systems/1/

    "Actions": {
        "#ComputerSystem.Reset": {
            "target": "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset",
            "ResetType@Redfish.AllowableValues": [
                "On",
                "ForceOff",
                "GracefulShutdown",
                "GracefulRestart",
                "ForceRestart",
                "Nmi",
                "ForceOn"
            ]
```
(from https://gist.github.com/flaviotorres/6e09c16d46ca2a79b131650c6b8c4e7f)

Redfish console can be obtained via ssh. See https://docs.nvidia.com/networking/display/bluefieldbmcv2310/serial+over+lan+(sol) for more details.

Clush usage (if clustershell has been installed on system):

* To do a command on all nodes : `clush -bw node1,node[4-5] "hostname"`
* To copy a file on all nodes : `clush -w node1,node[4-5] --copy /root/slurm.conf --dest=/etc/slurm/slurm.conf`
* To replace a string in a file of all nodes : `clush -bw compute1[34-67] 'sed -i "s/10.0.0.1/nfsserver/g" /etc/fstab'`

## Vocabulary

### Basic concepts

Few words on vocabulary used:

* To avoid confusion around "server" word, which can be used for software or hardware, we will keep this convention in this tutorial:
   * a **node** or an **host** refers to a physical or virtual machine with an operating system on it.
   * a **server** refer to a software daemon listening on the network (most of the time via a services mechanism like systemd).
* A **NIC** is a network interface controller (the thing you plug the Ethernet cable in ツ).
   * Note that on some systems, a NIC can be shared between server mother board and server BMC. See that as a bridge, which involve some specific things. Tip: when debugging PXE, try to avoid this kind of configuration, and use a BMC dedicated link if available. When using a shared NIC, link often goes down during PXE process, which means losing remote console during the important part of the PXE process.
* The **system administrator**, or sysadmin, will be you, the person in charge of managing the cluster. It is often refered as the "root" or the "sudo" user.
* Pets and Cattles
  * A pet node is a key node, that you MUST keep healthy and that is considered difficult to reinstall.
  * A cattle node, is a "trashable" node, that you consider non vital to production and that is considered easy to reinstall.

![Pets and cattle](images/servers_farm_deployment/sysadmin.jpg)

(Original black and white image from Roger Rössing, otothek_df_roe-neg_0006125_016_Sch%C3%A4fer_vor_seiner_Schafherde_auf_einer_Wiese_im_Harz.jpg)

An cluster can be seen like a sheep flock. The admin sys (shepherd), the management node (shepherd dog), and the worker nodes (sheep). This leads to two types of nodes, like cloud computing: pets (shepherd dog) and cattle (sheep). While the safety of your pets must be absolute for good production, losing cattle is common and considered normal. In HPC (High Performance Computing) for example, most of the time, management node, file system (io) nodes, etc, are considered as pets. On the other hand, compute nodes and login nodes are considered cattle. Same philosophy apply for file systems: some must be safe, others can be faster but “losable”, and users have to understand it and take precautions (backup data).

### Basic words

An cluster is an aggregate of physical compute nodes dedicated to perform tasks, hosts resources, or execute intensive calculations.
On some clusters, like HPC clusters, users will be able to login through ssh on dedicated nodes (called login nodes),
upload their code and data, then compile their code, and launch jobs (calculations) on the cluster.

To maintain the cluster synchronized and to provide features, multiple **services** are running on management node.

Most of the time, a cluster is composed of:

* An **administration node** or **management node** (pet), whose purpose is to host all core resources of the cluster.
* **IO nodes** (pet), whose purpose is to provide storage for users. Basic storage is based on NFS, and advanced storage (optional) on parallel file systems (POSIX or object based).
* **Login nodes** (cattle), whose purpose is to be the place where users or admin can interact with the cluster. On an HPC cluster, this is where users login via ssh and interact with the job scheduler, and manage their code and data.
* **Compute nodes** or **worker nodes** (cattle), whose purpose is to provide CPU/GPU resources.

A node is the name given to a server inside a cluster. Nodes are most of the time equipped with a **BMC**
for Baseboard Management Controller, which is kind of a small server connected on the server motherboard and allow manipulating the server remotely (power on, power off, boot order, status, console, etc.). Legacy BMCs are using IPMI protocal to communicate with, while new generation BMC are using http REST API (RedFish API). Unfortunately, many BMC are also using proprietary APIs. Note that standard BMCs also embed a small webserver, to be able to interact with via a web browser.

Sometime, servers are **racked** into a **chassis** that can embed an **CMC** for Chassis Management Controller. Servers and chassis can be
**racked** into a rack that can embed an **RMC** for Rack Management Controller.

On the **operating system** (OS), a **service** is a software daemon managed by **systemd**. For example, the DHCP server service is in charge of attributing nodes IP addresses on the network depending of their MAC address (each network interface has its own MAC). Another example, the job scheduler, is also used as a service. Etc.

Management node, called here `odin`, is the node hosting most of vital services of the cluster.

On some expensive clusters, **Interconnect** network, often based on the **InfiniBand** technology (IB), is used in parallel of the Ethernet network (Eth). Interconnect is mainly used for calculations (transfer data between process of running codes) and is used to export the fast file systems, exported by the IO nodes. InfiniBand has much lower latency and much higher bandwidth than legacy Ethernet network.

### Understanding services

As said above, management node host multiple basic services needed to run the cluster:

* The **repository** server: based on http protocol, it provides packages (rpm) to all nodes of the cluster. Service is `httpd` (Apache/Apache2 on some OS).
* The **tftp** server: based on tftp protocol, it provides PXE very basic files to initialize boot sequence on the remote servers. There are distribution embed tftp servers, but after years of IT, I just use `atftp`. I found it to be the most performant and comaptible server. Note that recent servers do not need a tftp server and can directly boot over http (we keep tftp here for compatibility).
* The **dhcp** server: provides ip for all nodes and BMC on the network. Ip are attributed using MAC addresses of network interfaces. Service is `dhcpd` (ISC DHCP).
* The **dns** server: provides link between ip and hostname, and the opposite. Service is `named` (bind9).
* The **time** server: provides a single and synchronized clock for all equipment of the cluster. More important than it seems. Service is `chronyd` (Chrony).
* The **pxe stack**: represent the aggregate of the repository server, the tftp server, the dhcp server, the dns server and the time server. Used to deploy OS on nodes on the cluster using the network.
* The **nfs** server: export simple storage spaces and allows nodes to mount these exported spaces locally (/home, /opt, etc. ). Service is `nfs-server`.
* The **LDAP** server: provides centralized users authentication for all nodes. This is optional for some clusters. Service is `slapd` (OpenLDAP), or you can also use `glauth` for simpler usage.
* The **job scheduler** server (if specializing cluster to HPC): manage computational resources, and spread jobs from users on the cluster. Service is `slurmctld` (Slurm).
* The **monitoring/reporting** server: monitor the cluster to provide metrics, and raise alerts in case of issues. Service is `prometheus` (Prometheus) for metrics, and you will also need a tool for errors/issues detections. While Prometheus could be used, it is not made for that. `icinga2` seems to be one of the best tool currently.

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>Small tip: never neglect monitoring, especially during cluster deployment. An healty cluster makes an happy admin, able to play strategy games while the cluster is purring...</p>
    </div>
</div> -->

Small tip: never neglect monitoring, especially during cluster deployment. An healty cluster makes an happy admin, able to play strategy games while the cluster is purring...

## Cluster description

### Architecture

The cluster structure for this training will be as follows:

![Cluster architecture](images/servers_farm_deployment/cluster_schema.svg)

On the hardware side:

* One master node called `odin`.
* One storage node called `thor`, based one NFS, will be deployed, for /home and /software.
* One external/internal node called `heimdall` for users to login or/and to act as a gateway.
* Multiple compute nodes, called `valkyries` will then be deployed on the fly via PXE.

This architecture is similar to HPC clusters, but is very generic. A web farm would replace the login node by a gateway or a load balancer, a Blender rendering farm would just skip the login node, etc.

### Network

Network information:

The whole cluster will use a single subnet `10.10.0.0/16`.
IP used will be (nic name to be set depending of your hardware, use `ip a` command to obtain your nic names, which can be ethX, enoX, enX, enpX, enp0sX, etc.):

* odin: 10.10.0.1 (nic: enp0s3)
* thor : 10.10.1.1 (nic: enp0s3)
* heimdall: 10.10.2.1 (nic: enp0s3), 192.168.1.77 (nic: enp0s8) for users access
* valkyrieX: 10.10.3.X (nic: enp0s3)

Domain name will be `cluster.local`.

Note: if you plan to test this tutorial in Virtualbox, 10.10.X.X range may
already been taken by Virtualbox NAT. In this case, use another subnet like 10.77.X.X.

### Final notes before we start

All nodes will be installed with a minimal install AlmaLinux 9 or Ubuntu 24.04. Needed other packages 
will be created on the fly from sources.

* To simplify this tutorial, firewall will be deactivated. You can reactivate it later.
* We will keep SELinux enforced on RHEL 9 systems. When facing permission denied, try setting SELinux into permissive mode to check if that's the reason, or check selinux logs. I know SELinux can be difficult to deal with, but keeping it enforced also forces you to avoid unexpected dangerous things.
* If you get `Pane is dead` error during pxe install, most of the time increase RAM to minimum 1200 Mo or more and it should be ok. Ubuntu deployment needs 6Gb ram to succeed, but you can lower VM ram after deployment to 1Gb or even less for non management nodes (512 Mb).
* You can edit files using `vim` which is a powerful tool, but if you feel more comfortable with, use `nano` (`nano myfile.txt`, then edit file, then use `Ctrl+O` to save, and `Ctrl+X` to exit). There is a very nice tutorial online for Vim, investing in it worth it on the long term.
* Keep cool, and take fresh air when its not working as expected.

## Management node installation

This part describes how to manually install `odin` management node basic services, needed to deploy and install the other servers.

Install first system with AlmaLinux DVD image or Ubuntu 24.04 live server (using an USB stick), and choose minimal install as package selection (Or server with GUI if you prefer. However, more packages installed means less security and less performance). Remember to ask for OpenSSH server installation on Ubuntu installer.

Partition schema should be the following, without LVM but standard partitions:

*	/boot 2Go ext4
*	swap 4Go
*	/ remaining space ext4

Note: you can learn how to use LVMs later.

Be extremely careful with time zone choice. This parameter is more important than it seems as time zone will be set in the kickstart file later, and MUST be the same than the one chosen here when installing `odin`. If you don’t know which one to use, choose Europe/Brussels, the same one chose in the examples of this document.
After install and reboot, disable firewall:

**If RHEL system:**

```
systemctl disable firewalld
systemctl stop firewalld
```

**If Ubuntu system**, nothing to do, UFW is not installed by default.

Now change hostname to `odin` (need to login again to see changes):

```
hostnamectl set-hostname odin.cluster.local
```

To start most services, we need the main NIC to be up and ready with an ip.
We will use **NetworkManager** to handle network. `nmcli` is the command to interact with NetworkManager.

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>Note about NetworkManager: some say its bad, some say its good. It depends of admin tastes. Use it if you feel confortable with it, or use systemd-networkd if you prefer. Best idea to me is to use what is default on the system: NetworkManager on RHEL like distributions and Suse, systemd-networkd on Ubuntu and Debian.</p>
    </div>
</div> -->

Note about NetworkManager: some say its bad, some say its good. It depends of admin tastes. Use it if you feel confortable with it, or use systemd-networkd if you prefer. Remember that some advanced hardware like Infiniband would prefer NetworkManager for some specific features.

**If RHEL system**, NetworkManager is already installer.

**If Ubuntu system**, install NetworkManager, configure netplan, and disable systemd-networkd and reboot:

```
apt update && apt install NetworkManager
cp -v /etc/netplan/01-netcfg.yaml /root/ # This is a backup
cat << EOF > /etc/netplan/01-netcfg.yaml
# This file describes the network interfaces available on your system
# For more information, see netplan(5).
# Set and change netplan renderer to NetworkManager GUI tool 
network:
  version: 2
  renderer: NetworkManager
EOF
netplan apply
systemctl disable systemd-networkd
reboot -h now
```

Assuming main NIC name is `enp0s3`, to set `10.10.0.1/16` IP and subnet on it, use the following commands:

```
nmcli con mod enp0s3 ipv4.addresses 10.10.0.1/16
nmcli con mod enp0s3 ipv4.method manual
nmcli con up enp0s3
```

You can at any time get all NIC parameters using:

```
nmcli con show enp0s3
```

Then ensure interface is up with correct ip using:

```
ip a
```

You should see your NICs with `enp0s3` having ip `10.10.0.1` with `/16` prefix.

Time to setup basic repositories.

Note: to setup more settings with nmcli, in case of needs:

If NetworkManager gave a generic name to your interface (like Wired Connection 1, or equivalent), to rename the interface, assuming here our interface name is "Wired connection 2" but should be enp0s3 because we want to keep hardware related naming convention:

```
nmcli connection modify "Wired connection 2" connection.id "enp0s3"
```

If you want to set a gateway:

```
nmcli con mod enp0s8 ipv4.gateway 192.168.20.1
```

If you want to set DNS:

```
nmcli con mod enp0s8 ipv4.dns "8.8.8.8 8.8.4.4"
```

### Configure management as a gateway

We need to configure the management node as a gateway for other nodes, so that clients can use it to reach the web.
To do so, we are going to use firewalld, and setup masquerading.

**If RHEL system**:

```
dnf install firewalld
```

**If Ubuntu system**:

```
apt update
apt install firewalld
```

Also on Ubuntu, make sure ugw is disabled:

```
ufw disable
```

Then for both OS, enable and start the firewall.

```
systemctl enable firewalld
systemctl start firewalld
```

Now enable ipv4 forwarding on management node:

```
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/95-IPv4-forwarding.conf
sysctl -p /etc/sysctl.d/95-IPv4-forwarding.conf
```

Then make sure ssh is allowed in external zone, to keep connectivity:

```
firewall-cmd --add-service=ssh --zone=external --permanent
```

We are now going to link our network interfaces to zones of the firewall. We will use 2 zones, an external one, which is considered unsafe but connected to the web somehow, and a trusted zone, which is our internal cluster.

```
firewall-cmd --change-interface=enp0s8 --zone=external --permanent
firewall-cmd --change-interface=enp0s3 --zone=trusted --permanent
```

Now enable masquerade on external zone.

```
firewall-cmd --zone=external --add-masquerade --permanent
```

Finally, restart firewalld to ensure all configuration is persistent:

```
systemctl restart firewalld
```

From now, our management node acts as a gateway for all other clients on the cluster network.

### Setup basic repositories

For RHEL system, we are going to setup a core OS repository, and a custom repository, while for Ubuntu we will prepare the needed material for PXE and a custom repository too.

#### RHEL

Backup and clean first default AlmaLinux repositories:

```
cp -a /etc/yum.repos.d/ /root/
rm -f /etc/yum.repos.d/*
```

The local repository allows the main server and other servers to install automatically rpm with correct dependencies without having to access web repository. All needed rpm are available in the AlmaLinux DVD.

Next step depends if you are using a Virtual Machine or a real server.

3 ways to do:

1. If you are using a real server, upload the AlmaLinux DVD in /root folder and mount it in /mnt (or mount it directly from CDROM):

```
mount /root/AlmaLinux-9-x86_64-Everything.iso /mnt
```

Copy full iso (will be needed later for PXE), and use the database already on the DVD:

```
mkdir -p /var/www/html/repositories/AlmaLinux/9/x86_64/os/
cp -a /mnt/* /var/www/html/repositories/AlmaLinux/9/x86_64/os/
restorecon -r /var/www/html/
```

2. Or you can also simply mount the iso directly in the good folder:

```
mkdir -p /var/www/html/repositories/AlmaLinux/9/x86_64/os/
mount /root/AlmaLinux-9-x86_64-Everything.iso /var/www/html/repositories/AlmaLinux/9/x86_64/os/
restorecon -r /var/www/html/
```

3. If you are using a Virtual Machine, simply create the folder and mount the ISO that you should have added into the virtual CDROM drive:

```
mkdir -p /var/www/html/repositories/AlmaLinux/9/x86_64/os/
mount /dev/cdrom /var/www/html/repositories/AlmaLinux/9/x86_64/os/
restorecon -r /var/www/html/
```

Now, indicate the server the repository position (here local disk). To do so, edit the file `/etc/yum.repos.d/os.repo` and add:

```
[BaseOS]
name=BaseOS
baseurl=file:///var/www/html/repositories/AlmaLinux/9/x86_64/os/BaseOS
gpgcheck=0
enabled=1

[AppStream]
name=AppStream
baseurl=file:///var/www/html/repositories/AlmaLinux/9/x86_64/os/AppStream
gpgcheck=0
enabled=1
```

Note: BaseOS provides basic rpms and tools, while AppStream provides different versions of very specific softwares (you can ask for a specific version of Apache http server for example).

OS repositories are split between BaseOS and AppStream. Using this file, we will reach both.

Finally, install and start the `httpd` service, to allow other servers using this repository through `http`.

```
dnf install httpd -y
systemctl enable httpd
systemctl start httpd
```

The repository server is up, and listening. We can now use it to reach repositories, as any other servers on the cluster network will.

Edit `/etc/yum.repos.d/os.repo` and update to:

```
[BaseOS]
name=BaseOS
baseurl=http://10.10.0.1/repositories/AlmaLinux/9/x86_64/os/BaseOS
gpgcheck=0
enabled=1

[AppStream]
name=AppStream
baseurl=http://10.10.0.1/repositories/AlmaLinux/9/x86_64/os/AppStream
gpgcheck=0
enabled=1
```

Ensure it works, by installing for example `wget`:

```
dnf clean all
dnf repolist
dnf install wget
```

##### Ubuntu

Create a repository folder, where we will upload our live server iso, for future PXE deployment. The iso will be needed in 2 format: plain iso, and extracted into a folder.

```
mkdir -p /var/www/html/repositories/Ubuntu/24.04/x86_64/extra/
```

#### Custom repositorie (both RHEL and Ubuntu)

##### RHEL 

We will need to add extra packages as not all is contained in the AlmaLinux 9 DVD.
Create extra repository folder:

```
mkdir -p /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
restorecon -r /var/www/html/
```

We now need to create a new repository here using the dedicated command. This will be for now an empty repository.
We must install this command first:

```
dnf install -y createrepo
createrepo /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
restorecon -r /var/www/html/
```

Then create dedicated repository file `/etc/yum.repos.d/extra.repo` with the following content:

```
[Extra]
name=Extra
baseurl=http://10.10.0.1/repositories/AlmaLinux/9/x86_64/extra
gpgcheck=0
enabled=1
```

Make sure http server is installed and launched:

```
dnf install httpd -y
systemctl enable httpd
systemctl start httpd
```

##### Ubuntu

We need this extra repository for our tftp server, but other packages you might need will also fit here.

Create dedicated folder:

```
mkdir -p /var/www/html/repositories/Ubuntu/24.04/x86_64/extra/
```

Now install needed packages:

```
apt-get install -y dpkg-dev reprepro
```

Now create an empty repository, we will add packages later.
Note that the includedeb command will fail, due to missing deb packages. This is expected for now.

```
cd /var/www/html/repositories/Ubuntu/24.04/x86_64/extra/
mkdir conf -p; \
    echo "Origin: BlueBanquise" > conf/distributions; \
    echo "Label: bluebanquise" >> conf/distributions; \
    echo "Codename: noble" >> conf/distributions; \
    echo "Suite: stable" >> conf/distributions; \
    echo "Architectures: amd64" >> conf/distributions; \
    echo "Components: main" >> conf/distributions;
reprepro -b /var/www/html/repositories/Ubuntu/24.04/x86_64/extra/ includedeb noble *.deb
```

Make sure http server is installed and launched:

```
apt install apache2 -y
systemctl enable apache2
systemctl start apache2
```

### DHCP server

The DHCP server is used to assign ip addresses and hostnames to other nodes. It is the first server seen by a new node booting in PXE for installation. In this configuration, it is assumed MAC addresses of nodes are known.

Install the dhcp server package:

**If RHEL system**

```
dnf install dhcp-server
```

**If Ubuntu system**

```
apt install isc-dhcp-server
```

Do not start it now, configure it first.
The configuration file is `/etc/dhcp/dhcpd.conf`.
It should be like the following, replacing MAC address here by the ones of the current cluster. It is possible to tune global values.
Unknown nodes/BMC will be given a temporary ip on the 10.0.254.x range if dhcp server do not know their MAC address.

```
 authoritative;

 option client-arch code 93 = unsigned integer 16;
 if exists client-arch {
   if option client-arch = 00:00 {
     filename "undionly.kpxe";
   } elsif option client-arch = 00:07 {
     filename "snponly.efi";
   } elsif option client-arch = 00:08 {
     filename "snponly.efi";
   } elsif option client-arch = 00:09 {
     filename "snponly.efi";
   }
 }

 subnet 10.10.0.0 netmask 255.255.0.0 {
 range 10.10.254.0 10.10.254.254; # range where unknown servers will be
 option domain-name "cluster.local";
 option domain-name-servers 10.10.0.1; # dns server ip
 option broadcast-address 10.10.255.255;
 default-lease-time 600;
 max-lease-time 7200;

 next-server 10.10.0.1; #  pxe server ip

# List of nodes

host thor {
 hardware ethernet 08:00:27:18:68:BC;
 fixed-address 10.10.1.1;
 option host-name "thor";
}

host heimdall {
 hardware ethernet 08:00:27:18:58:BC;
 fixed-address 10.10.2.1;
 option host-name "heimdall";
}

host valkyrie01 {
 hardware ethernet 08:00:27:18:67:BC;
 fixed-address 10.10.3.1;
 option host-name "valkyrie01";
}

host valkyrie02 {
 hardware ethernet 08:00:27:18:68:BC;
 fixed-address 10.10.3.2;
 option host-name "valkyrie02";
}

}
```

Note: also add your server's BMC if any.

Finally, start and enable the dhcp service:

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>&#x26A0; WARNING &#x26A0;: only enable the DHCP service if you are on an isolated network, as in opposite to the other services, it may disturb the network if another DHCP is on this network.</p>
    </div>
</div> -->

&#x26A0; WARNING &#x26A0;: only enable the DHCP service if you are on an isolated network, as in opposite to the other services, it may disturb the network if another DHCP is on this network.

**If RHEL system**

```
systemctl enable dhcpd
systemctl start dhcpd
```

**If Ubuntu system**

```
systemctl enable isc-dhcp-server
systemctl start isc-dhcp-server
```

Note: if needed, you can search for nodes in `10.10.254.0-10.10.254.254` range using the following `nmap` command (install it using `dnf install nmap`):

```
nmap 10.10.254.0-254
```

This is useful to check after a cluster installation that no equipment connected on the network was forgotten in the process, since registered nodes in the DHCP should not be in this range.

You can watch dhcp server logs using:

**If RHEL system**

```
journalctl -a -u dhcpd -f
```

**If Ubuntu system**

```
journalctl -a -u isc-dhcp-server -f
```

This is very useful to monitor dhcp server logs during other nodes PXE and deployment.

### DNS server

DNS server provides on the network ip/hostname relation to all hosts:

* ip for corresponding hostname
* hostname for corresponding ip

The configuration is similar but enough different between RHEL and Ubuntu to have dedicated sections for each.

#### RHEL

Install dns server package:

```
dnf install bind
```

Configuration includes 3 files: main configuration file, forward file, and reverse file. (You can separate files into more if you wish, not needed here).

Main configuration file is `/etc/named.conf` for RedHat, and should be as follow (we are creating an recursive DNS for our cluster, refer to Bind9 documentation for more details):

```
options {
	listen-on port 53 { 127.0.0.1; 10.10.0.1;};
	listen-on-v6 port 53 { ::1; };
	directory 	"/var/named";
	dump-file 	"/var/named/data/cache_dump.db";
	statistics-file "/var/named/data/named_stats.txt";
	memstatistics-file "/var/named/data/named_mem_stats.txt";
	allow-query     { localhost; 10.10.0.0/16;};

  recursion yes;

  forwarders {
    8.8.8.8;
    8.8.4.4;
  };

	dnssec-enable no;
	dnssec-validation no;
	dnssec-lookaside auto;

	/* Path to ISC DLV key */
	bindkeys-file "/etc/named.iscdlv.key";

	managed-keys-directory "/var/named/dynamic";

	pid-file "/run/named/named.pid";
	session-keyfile "/run/named/session.key";
};

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

zone "." IN {
	type hint;
	file "named.ca";
};

zone"cluster.local" IN {
type master;
file "forward";
allow-update { none; };
};
zone"10.10.in-addr.arpa" IN {
type master;
file "reverse";
allow-update { none; };
};

include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";
```

Note that the `10.10.in-addr.arpa` is related to first part of our range of ip. If cluster was using for example `172.16.x.x` ip range, then it would have been `16.172.in-addr.arpa`.

What contains our names and ip are the two last zone parts. They refer to two files: `forward` and `reverse`. These files are located in `/var/named/`.

First one is `/var/named/forward` with the following content:

```
$TTL 86400
@   IN  SOA     odin.cluster.local. root.cluster.local. (
        2011071001  ;Serial
        3600        ;Refresh
        1800        ;Retry
        604800      ;Expire
        86400       ;Minimum TTL
)
@       IN  NS          odin.cluster.local.
@       IN  A           10.10.0.1

odin               IN  A   10.10.0.1
thor               IN  A   10.10.1.1
heimdall           IN  A   10.10.2.1

valkyrie01         IN  A   10.10.3.1
valkyrie02         IN  A   10.10.3.2
```

Second one is `/var/named/reverse`:

```
$TTL 86400
@   IN  SOA     odin.cluster.local. root.cluster.local. (
        2011071001  ;Serial
        3600        ;Refresh
        1800        ;Retry
        604800      ;Expire
        86400       ;Minimum TTL
)
@       IN  NS          odin.cluster.local.
@       IN  PTR         cluster.local.

odin      IN  A   10.10.0.1

1.0        IN  PTR         odin.cluster.local.
1.1        IN  PTR         thor.cluster.local.
1.2        IN  PTR         heimdall.cluster.local.

1.3        IN  PTR         valkyrie01.cluster.local.
2.3        IN  PTR         valkyrie02.cluster.local.
```

Set rights on files:

```
chgrp named -R /var/named
chown -v root:named /etc/named.conf
restorecon -rv /var/named
restorecon -v /etc/named.conf
```

And start service:

```
systemctl enable named
systemctl start named
```

#### Ubuntu


Install dns server package:

```
apt install bind9
```

Configuration includes multiple files: main configuration files, forward file, and reverse file. (You can separate files into more if you wish, not needed here).

Create first needed folder if they do not exist:

```
mkdir -p /var/cache/bind/data
mkdir -p /var/cache/bind/dynamic
chown -R bind:bind /var/cache/bind
```

Main configuration file is `/etc/bind/named.conf` for Ubuntu, and should be as follow (we are creating an recursive DNS for our cluster, refer to Bind9 documentation for more details).

```
## This is the primary configuration file for the BIND DNS server named.

include "/etc/bind/named.conf.options";
include "/etc/bind/named.conf.local";
include "/etc/bind/named.conf.default-zones";
```

Now create/edit file /etc/bind/named.conf.options to have it this way:

```
options {
  listen-on port 53 {
    127.0.0.1;
    10.10.0.1;
  };

  listen-on-v6 port 53 { ::1; };
  directory     "/var/cache/bind";
  dump-file     "/var/cache/bind/data/cache_dump.db";
  statistics-file "/var/cache/bind/data/named_stats.txt";
  memstatistics-file "/var/cache/bind/data/named_mem_stats.txt";

  allow-query {
    localhost;
    10.10.0.0/16;
  };

  recursion yes;

  forwarders {
    8.8.8.8;
    8.8.4.4;
  };

  dnssec-validation False;

  managed-keys-directory "/var/cache/bind/dynamic";

  pid-file "/run/named/named.pid";
  session-keyfile "/run/named/session.key";

};

logging {
  channel default_debug {
    file "/var/cache/bind/data/named.log";
    severity dynamic;
  };

};
```

Now create file /etc/bind/named.conf.local with the following content:

```
## Local server zones

include "/etc/bind/zones.rfc1918";

## Forward zones

zone "cluster.local" IN {
  type master;
  file "/etc/bind/forward.zone";
  allow-update { none; };
};

## Reverse zones

zone "10.10.in-addr.arpa" IN {
   type master;
   file "/etc/bind/10.10.rr.zone";
   allow-update { none; };
};
```

Note that the `10.10.in-addr.arpa` is related to first part of our range of ip. If cluster was using for example `172.16.x.x` ip range, then it would have been `16.172.in-addr.arpa`.

What contains our names and ip are the two last zone parts. They refer to two files: `forward.zone` (forward) and `/etc/bind/10.10.rr.zone` (reverse). These files are located in `/etc/bind/` too.

First one is `/etc/bind/forward.zone` with the following content:

```
$TTL 86400
@   IN  SOA     odin.cluster.local. root.cluster.local. (
        2011071001  ;Serial
        3600        ;Refresh
        1800        ;Retry
        604800      ;Expire
        86400       ;Minimum TTL
)
@       IN  NS          odin.cluster.local.
@       IN  A           10.10.0.1

odin               IN  A   10.10.0.1
thor               IN  A   10.10.1.1
heimdall           IN  A   10.10.2.1

valkyrie01         IN  A   10.10.3.1
valkyrie02         IN  A   10.10.3.2
```

Second one is `/etc/bind/10.10.rr.zone`:

```
$TTL 86400
@   IN  SOA     odin.cluster.local. root.cluster.local. (
        2011071001  ;Serial
        3600        ;Refresh
        1800        ;Retry
        604800      ;Expire
        86400       ;Minimum TTL
)
@       IN  NS          odin.cluster.local.
@       IN  PTR         cluster.local.

odin      IN  A   10.10.0.1

1.0        IN  PTR         odin.cluster.local.
1.1        IN  PTR         thor.cluster.local.
1.2        IN  PTR         heimdall.cluster.local.

1.3        IN  PTR         valkyrie01.cluster.local.
2.3        IN  PTR         valkyrie02.cluster.local.
```

Finally, start service:

```
systemctl enable bind9
systemctl start bind9
```

#### Clients

The server is up and running. We need to setup client part, even on our `odin`
management node.

The old way was to edit the `/etc/resolv.conf`. However, when using NetworkManager or systemd-netword, this is bad idea and we should update DNS directly in these tools.

```
nmcli con mod enp0s8 ipv4.dns "10.10.0.1"
```

You can check NIC configuration using:

```
nmlci con show enp0s8
```

DNS is now ready. You can try to ping `odin` and see if it works.
Stop DNS service and try again to see it does not resolve ip anymore.

### Hosts file

An alternative or in complement to DNS, most system administrators setup an hosts file.

The hosts file allows to resolve locally which ip belongs to which hostname if written inside. For small clusters, it can fully replace the DNS.
On large cluster, most system administrators write inside at least key or critical hostnames and ip and uses a DNS.

Lets create our hosts file. Edit `/etc/hosts` file and have it match the following:

```
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

10.10.0.1   odin
10.10.1.1   thor
10.10.2.1   heimdall
10.10.3.1   valkyrie01
10.10.3.2   valkyrie02
```

You can now try to stop DNS server and check that now, even with the DNS stopped, we can resolve and ping `odin`.

### Time server

The time server provides date and time to ensure all nodes/servers are synchronized. This is VERY important, as many authentication tools (munge, ldap, etc.) will not work if cluster is not clock synchronized. If something fail to authenticate, one of the first debug move is to check clock are synchronized.

Install needed packages:

**If RHEL system**

```
dnf install chrony
```

**If Ubuntu system**

```
apt install chrony tzdata
```

Configuration file is `/etc/chrony.conf` for RHEL or `/etc/chrony/chrony.conf` for Ubuntu, for both client or/and server configuration, as chrony can act as both client and server at the same time (see time synchronisation as a chain).

We will configure it to allow the local network to query time from this server.
Also, because this is a poor clock source, we use a stratum 12 (the bigger the stratum number, the badder time source is). This is purely virtual here, but idea is: if a client can reach multiple time servers, then it will sync with the higest stratum one available.

The file content should be as bellow:

```
# Define local clock as a bad clock
local stratum 12

# Allow queries from the main network
allow 10.10.0.0/16

# Record the rate at which the system clock gains/losses time.
driftfile /var/lib/chrony/drift

# Allow the system clock to be stepped in the first three updates
# if its offset is larger than 1 second.
makestep 1.0 3

# Enable kernel synchronization of the real-time clock (RTC).
rtcsync

# Specify directory for log files.
logdir /var/log/chrony
```

Then start and enable service:

```
systemctl restart chronyd
systemctl enable chronyd
```

### PXE stack

PXE, for Preboot Execution Environment, is a mechanism that allows remote hosts to boot from the network and deploy operating system using configuration and packages from the management node.

It is now time to setup the PXE stack, which is composed of the dhcp server, the http server, the tftp server, the dns server, and the time server.

The http server will distribute the minimal kernel and initramfs for remote Linux booting, the kickstart autoinstall file for remote hosts to know how they should be installed, and the repositories for packages distribution. Some very basic files will be provided using tftp as this is the most compatible PXE protocol.

Note that the AlmaLinux or Ubuntu already embed a very basic tftp server. But it cannot handle a huge cluster load, are not super verbose, and I could discover that they are not always compatible with some very specific hardware. This is why here we are going to replace it by the atftp server.

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>PXE is the most tricky part, as you will face all possible issues: hardware issues, bad cabling, firewalls, Vlans issues, stupid BIOS or BMCs, etc. Always try with a very simple network (flat, no vlans, no firewalls), and ensure you can deploy OS before complexify and secure the cluster and the network.</p>
    </div>
</div> -->

PXE is the most tricky part, as you will face all possible issues: hardware issues, bad cabling, firewalls, Vlans issues, stupid BIOS or BMCs, etc. Always try with a very simple network (flat, no vlans, no firewalls), and ensure you can deploy OS before complexify and secure the cluster and the network.

#### Build atftp

**If RHEL system**

```
dnf install gcc automake autoconf make wget
```

**If Ubuntu system**

```
apt install gcc automake autoconf make wget alien
```

Then grab sources and remove original spec file:

```
wget https://freefr.dl.sourceforge.net/project/atftp/atftp-0.8.0.tar.gz
tar xvzf atftp-0.8.0.tar.gz
cd atftp-0.8.0
rm -f redhat/atftp.spec
```

Now create a custom service file, that contains the verbose flag, and allows a lot of threads. Create file `atftpd.service` with the following content:

```
[Unit]
Description=ATFTP daemon with verbosity
After=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/atftpd --daemon --user tftp --no-multicast --maxthread 100 --group tftp /var/lib/tftpboot --verbose

[Install]
WantedBy=multi-user.target

```

Now create a custom spec file, that rename the tool bluebanquise-atftp, so it does not conflict with distribution repositories. Create file `atftp.spec` with the following content:

```
%define is_debian_ubuntu %(grep -i -E "debian|ubuntu" /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)

Name: bluebanquise-atftp
Summary: Advanced Trivial File Transfer Protocol (ATFTP) - TFTP server
Group: System Environment/Daemons
Version: 0.8.0
Release: 1
License: GPL
Vendor: Linux Networx Inc.
Source: https://freefr.dl.sourceforge.net/project/atftp/atftp.tar.gz
Buildroot: /var/tmp/atftp-buildroot
Packager: Benoit Leveugle <benoit.leveugle@gmail.com>

Obsoletes: atftp

%description
Multithreaded TFTP server implementing all options (option extension and
multicast) as specified in RFC1350, RFC2090, RFC2347, RFC2348 and RFC2349.
Atftpd also support multicast protocol knowed as mtftp, defined in the PXE
specification. The server supports being started from inetd(8) as well as
a deamon using init scripts.


%package client
Summary: Advanced Trivial File Transfer Protocol (ATFTP) - TFTP client
Group: Applications/Internet


%description client
Advanced Trivial File Transfer Protocol client program for requesting
files using the TFTP protocol.


%prep
%setup


%build
%configure
make


%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != '/' ] && rm -rf $RPM_BUILD_ROOT
%makeinstall
mkdir -p ${RPM_BUILD_ROOT}/usr/lib/systemd/system/
cp atftpd.service ${RPM_BUILD_ROOT}/usr/lib/systemd/system/atftpd.service
chmod 644 ${RPM_BUILD_ROOT}/usr/lib/systemd/system/atftpd.service


%files
%{_mandir}/man8/*
%{_sbindir}/atftpd
%{_sbindir}/in.tftpd
/usr/lib/systemd/system/atftpd.service


%files client
%{_mandir}/man1/*
%{_bindir}/atftp


%preun


%post
useradd --system -d /var/lib/tftpboot tftp || true
%if %is_debian_ubuntu
usermod -a -G tftp www-data || true
%else
usermod -a -G tftp apache || true
%endif

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != '/' ] && rm -rf $RPM_BUILD_ROOT


%changelog
* Wed Dec 01 2021 Benoit Leveugle <benoit.leveugle@gmail.com>
- Adapt to bluebanquise
* Tue Jan 07 2003 Thayne Harbaugh <thayne@plug.org>
- put client in sub-rpm

```

Now generate the configure file for later build:

```
./autogen.sh
```

Finaly, exit this folder and rename folder, compress it, then build package:

```
cd ../
mv atftp-0.8.0 bluebanquise-atftp-0.8.0
tar cvzf atftp.tar.gz bluebanquise-atftp-0.8.0
rpmbuild -ta atftp.tar.gz --target=x86_64 --define "_software_version 0.8.0" --define "_lto_cflags %{nil}"
```

Now we need to add this package to our custom repository.

##### Ubuntu

Go into a temporary folder, convert the rpm to deb package using alien tool, and inject it into the local repository:

```
cd /tmp
alien --to-deb --scripts /root/rpmbuild/RPMS/x86_64/bluebanquise-atftp-*
reprepro -b /var/www/html/repositories/Ubuntu/24.04/x86_64/extra/ includedeb noble *.deb
```

And add the repository to the system sources:

```
cat << EOF > /etc/apt/sources.list.d/extra.sources
Types: deb
URIs: http://10.10.0.1/repositories/Ubuntu/24.04/x86_64/extra/
Suites: noble
Components: main
Trusted: yes
EOF
```

Now, using apt install our new package, and start the service:

```
apt update
apt install bluebanquise-atftp
systemctl start atftpd
systemctl enable atftpd
```

##### RHEL

Move into the repository folder, and copy built rpm into the folder, then use createrepo command to generate the repository or update it:

```
cd /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
cp /root/rpmbuild/RPMS/x86_64/bluebanquise-atftp-*.rpm .
createrepo /var/www/html/repositories/AlmaLinux/9/x86_64/extra/
restorecon -r /var/www/html/
```

You can now install the package using dnf command, as we already registered this repo earlier.

```
dnf install bluebanquise-atftp
```

#### iPXE custom rom

We then need ipxe files. We could use native syslinux or shim.efi files, but this is just not flexible enough for new generation clusters.
We will build our own ipxe roms, and include our own init script.

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>Small tip: ipxe allows you to build raw roms (the ones we will use in this tutorial), but also iso or usb image that contains the rom. This is VERY (VERY!!!!) useful when you need to boot a stupidely made node with a weird BIOS or some network cards that does not boot over PXE.</p>
    </div>
</div> -->

Small tip: ipxe allows you to build raw roms (the ones we will use in this tutorial), but also iso or usb image that contains the rom. This is VERY (VERY!!!!) useful when you need to boot a stupidely made node with a weird BIOS or some network cards that does not boot over PXE.

Lets install few packages first.

**If RHEL system**

```
dnf groupinstall "Development tools" -y
dnf install xz-devel -y
```

**If Ubuntu system**

```
apt install gcc git liblzma-dev -y
```

Now, lets grab latest ipxe version from git.
Clone the ipxe repository into `/root/ipxe`:

```
mkdir /root/ipxe
cd /root/ipxe
git clone https://github.com/ipxe/ipxe.git .
```

Lets create our ipxe script, that will display a nice ascii art, so we can see it loading, and that will target the file we want.
To create something simple, lets target the file `http://${next-server}/boot.ipxe` at boot.

Create file `/root/ipxe/src/our_script.ipxe` with the following content:

```
#!ipxe

echo
echo . . . . . . . *. . . . .*. . . *. . . . .*
echo . . . . . ***. . . . . **********. . . . . ***
echo . . . .*****. . . . . .**********. . . . . .*****
echo . . .*******. . . . . .**********. . . . . .*******
echo . .**********. . . . .************. . . . .**********
echo . ****************************************************
echo .******************************************************
echo ********************************************************
echo ********************************************************
echo ********************************************************
echo .******************************************************
echo . ********. . . ************************. . . ********
echo . .*******. . . .*. . .*********. . . *. . . .*******
echo . . .******. . . . . . .*******. . . . . . . ******
echo . . . .*****. . . . . . .*****. . . . . . . *****
echo . . . . . ***. . . . . . .***. . . . . . . ***
echo . . . . . . **. . . . . . .*. . . . . . . **
echo

sleep 4

ifconf --configurator dhcp || shell

echo
echo +---------------- System information ----------------+
echo |
echo | hostname:     ${hostname}
echo | platform:     ${platform}
echo | mac:          ${net0/mac}
echo | ip:           ${net0.dhcp/ip:ipv4}
echo | netmask:      ${net0.dhcp/netmask:ipv4}
echo | dhcp-server:  ${net0.dhcp/dhcp-server:ipv4}
echo | gateway:      ${net0.dhcp/gateway:ipv4}
echo | dns-server:   ${net0.dhcp/dns:ipv4}
echo | domain:       ${net0.dhcp/domain:string}
echo | next-server:  ${net0.dhcp/next-server:ipv4}
echo | user-class:   ${user-class:string}
echo |
echo +----------------------------------------------------+
echo

sleep 4

chain http://${next-server}/boot.ipxe || shell
```

Simply put, this script will display a nice ascii art, then sleep 4s, then
request dhcp server for all information (ip, hostname, next-server, etc.),
then display some of the information obtained, then sleep 4s, then chain load to
file `http://${next-server}/boot.ipxe` with `${next-server}` obtained from the DHCP server.
The `|| shell` means: if chaining fail, launch a shell so that sys admin can debug.

Then enter the src directory, enable few useful features of iPXE, and build the needed files:

```
cd src
sed -i 's/.*DOWNLOAD_PROTO_HTTPS.*/#define DOWNLOAD_PROTO_HTTPS/' config/general.h
sed -i 's/.*PING_CMD.*/#define PING_CMD/' config/general.h
sed -i 's/.*CONSOLE_CMD.*/#define CONSOLE_CMD/' config/general.h
sed -i 's/.*CONSOLE_FRAMEBUFFER.*/#define CONSOLE_FRAMEBUFFER/' config/console.h
sed -i 's/.*IMAGE_ZLIB.*/#define IMAGE_ZLIB/' config/general.h
sed -i 's/.*IMAGE_GZIP.*/#define IMAGE_GZIP/' config/general.h
sed -i 's/.*DIGEST_CMD.*/#define DIGEST_CMD/' config/general.h
sed -i 's/.*REBOOT_CMD.*/#define REBOOT_CMD/' config/general.h
sed -i 's/.*POWEROFF_CMD.*/#define POWEROFF_CMD/' config/general.h
make -j 4 bin-x86_64-efi/ipxe.efi EMBED=our_script.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin-x86_64-efi/snponly.efi EMBED=our_script.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin/undionly.kpxe EMBED=our_script.ipxe DEBUG=intel,dhcp,vesafb
```

Important note: we built here 3 roms. 2 for EFI systems, 1 for legacy systems.
The default EFI one is ipxe.efi. But experience has proven that the snponly.ipxe rom is nearly all the time compatible with hardware, so we will use that one here.

And finally copy these files into the `/var/lib/tftpboot/` folder so that tftp server
can provide them to the nodes booting.

```
mkdir -p /var/lib/tftpboot/
cp bin-x86_64-efi/ipxe.efi /var/lib/tftpboot/
cp bin-x86_64-efi/snponly.efi /var/lib/tftpboot/
cp bin/undionly.kpxe /var/lib/tftpboot/
```

#### iPXE chain

Now we will create file `/var/www/html/boot.ipxe` that will be targeted by each node booting.
There are multiple strategy here. We could simply add basic boot information in this file and consider it done.
But we would quickly face an issue: how to handle different parameters per nodes? Maybe one kind of node need a specific console or kernel parameter that the others do not need.

To solve that, we will simply create a folder `/var/www/html/nodes/` and create one file per node inside.
Then we will ask in the `boot.ipxe` file that each node booting load its own file, related to its hostname provided by the DHCP.

Tip: we will then be able to use file links to create one file per group of nodes if needed.

Create folder:

```
mkdir /var/www/html/nodes/
mkdir /var/www/html/nodes_groups/
```

And create `/var/www/html/boot.ipxe` file with the following content:

```
#!ipxe
echo Chaining to node dedicated file
chain http://${next-server}/nodes/${hostname}.ipxe || shell
```

Last step for the iPXE chain is to create a file for our group of node, and link
our node to this group (for example, a compute node group could need different parameters than a group of storages nodes, etc). We will use as example here a "storage" group. Note that the content of the file depends on the OS, so it is different between RHEL and Ubuntu.

##### RHEL

Create file `/var/www/html/nodes_groups/group_storage.ipxe` with the following content:

```
#!ipxe

echo Booting OS
echo Group profile: storage

echo +----------------------------------------------------+
echo |
echo | Loading kernel

kernel http://${next-server}/repositories/AlmaLinux/9/x86_64/os/images/pxeboot/vmlinuz initrd=initrd.img inst.stage2=http://${next-server}/repositories/AlmaLinux/9/x86_64/os/ inst.repo=http://${next-server}/repositories/AlmaLinux/9/x86_64/os/BaseOS/ inst.ks=http://${next-server}/nodes_groups/group_storage.kickstart.cfg

echo | Loading initial ramdisk ...

initrd http://${next-server}/repositories/AlmaLinux/9/x86_64/os/images/pxeboot/initrd.img

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
```

##### Ubuntu

```
#!ipxe

echo Booting OS
echo Group profile: storage

echo +----------------------------------------------------+
echo |
echo | Loading kernel

kernel http://${next-server}/repositories/Ubuntu/24.04/x86_64/iso/casper/vmlinuz initrd=initrd root=/dev/ram0 ramdisk_size=1500000 ip=dhcp url=http://${next-server}/repositories/Ubuntu/24.04/x86_64/ubuntu-24.04-live-server-amd64.iso autoinstall ds=nocloud-net;s=http://${next-server}/nodes_groups/group_storage.cloud-init/ cloud-config-url=http://${next-server}/nodes_groups/group_storage.cloud-init/user-data

echo | Loading initial ramdisk ...

initrd http://${next-server}/repositories/Ubuntu/24.04/x86_64/iso/casper/initrd

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
```




Now that our group file is created, link the node `thor` to this group:

```
cd /var/www/html/nodes/
ln -s ../nodes_groups/group_storage.ipxe thor.ipxe
```

Note: it is important that link are relative: you have to cd into nodes directory,
and create the link from here with a relative path.

To summarize, chain will be the following: `DHCP -> {undionly.kpxe|snponly.efi} -> boot.ipxe -> thor.ipxe (group_storage.ipxe)` .

We now need to provide the auto-installation files. Structure is different between RHEL and Ubuntu.

#### Auto installation files

##### RHEL -> Kickstart

We now need to provide a kickstart file.

The kickstart file will provide auto-installation features: what should be installed, how, etc.
We will create one kickstart file per group of nodes.

To create the kickstart file, we need an ssh public key from our `odin` management
node. Create it, without passphrase:

```
ssh-keygen -N "" -t Ed25519
```

And get the content of the public key file `/root/.ssh/id_ed25519.pub`, we will use it just bellow to generate the
kickstart file. For example, content of mine is:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqpyyh44Hz3gvhISaIE9yJ/ao8fBLNo7qwPJcYjQdIl root@odin.cluster.local
```

Now we need an sha512 password hash. Generate one using the following command:

```
python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'
```

And keep it somewhere (for example, `$6$7zvrwimYcypA8JWc$5GWYVF7zrI5eorsPN8IUT1n/Gmjpkic7h2cCbFVxbkqJeG0/kmJsYw6EN9oX3NQ34duwW7qAmOI13Y/0v5oHn.` is for `root` as password, which is not secure but ok for training purpose), we will use it just bellow to generate the kickstart file.

Then, create the kickstart file `/var/www/html/nodes_groups/group_storage.kickstart.cfg`
dedicated to storage group, with the following minimal content:

```
##### General settings

# Do not use GUI
text

# Run the Setup Agent on first boot
firstboot --enable

# System keyboard layout
keyboard --vckeymap=us --xlayouts=us

# System language
lang en_US.UTF-8

# System timezone
timezone Europe/Brussels --isUtc

# Reboot after installation
reboot

##### Authentication settings

# Root password (sha512)
rootpw --iscrypted $6$7zvrwimYcypA8JWc$5GWYVF7zrI5eorsPN8IUT1n/Gmjpkic7h2cCbFVxbkqJeG0/kmJsYw6EN9oX3NQ34duwW7qAmOI13Y/0v5oHn.


##### Network

# Network settings
network --bootproto=dhcp --ipv6=auto --activate
network --hostname=localhost.localdomain

##### Security

# SELinux
selinux --enforcing

# Firwalld
firewall --disabled

##### Partitionning

# Bootloader configuration
bootloader --append="" --location=mbr

# Partitioning
clearpart --all --initlabel
autopart --type=plain --fstype=ext4 --nohome

##### Packages

%packages
@core
%end

# Main post, ssh keys
%post --interpreter /bin/bash --log /root/main_post-install.log

# Add ssh keys from ssh_keys list
mkdir /root/.ssh
cat << xxEOFxx >> /root/.ssh/authorized_keys
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqpyyh44Hz3gvhISaIE9yJ/ao8fBLNo7qwPJcYjQdIl root@odin.cluster.local
xxEOFxx
# Ensure SELinux configuration is ok
restorecon -R -v /root/.ssh

%end
```

Notes:

* The ssh public key here will allow us to ssh on the remote hosts without having to provide a password.
* We install only the absolute minimal operating system. It is strongly recommended to do the minimal amount of tasks during a kickstart as it is way simpler to debug things installing once system is running.
* Important note: the time zone parameter is very important. Choose here the same than the one choose when installing the OS of `odin`. If you don’t know the one used, it can be found using: `ll /etc/localtime`
* Ensure also your keyboard type is correct.
* For compatibility purpose, this kickstart example does not specify which hard drive disk to use, but only locate first one and use it. Tune it later according to your needs.

Now, ensure all services are started:

```
systemctl start httpd
systemctl enable httpd
systemctl start atftpd
systemctl enable atftpd
```

We can proceed with the boot of `thor` node, and then the other nodes.

##### Ubuntu -> Cloud Init

We now need to provide a user-data file, based on cloud-init.

This file will provide auto-installation features: what should be installed, how, etc.
We will create one user-data file per group of nodes.

To create the user-data file, we need an ssh public key from our `odin` management
node. Create it, without passphrase:

```
ssh-keygen -N "" -t Ed25519
```

And get the content of the public key file `/root/.ssh/id_ed25519.pub`, we will use it just bellow to generate the
kickstart file. For example, content of mine is:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqpyyh44Hz3gvhISaIE9yJ/ao8fBLNo7qwPJcYjQdIl root@odin.cluster.local
```

Now we need an sha512 password hash. Generate one using the following command:

```
python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'
```

And keep it somewhere (for example, `$6$7zvrwimYcypA8JWc$5GWYVF7zrI5eorsPN8IUT1n/Gmjpkic7h2cCbFVxbkqJeG0/kmJsYw6EN9oX3NQ34duwW7qAmOI13Y/0v5oHn.` is for `root` as password, which is not secure but ok for training purpose), we will use it just bellow to generate the user-data file.

Now create a dedicated folder for our group:

```
mkdir -p /var/www/html/nodes_groups/group_storage.cloud-init/
```

We already prepared the iso and the iso content before.

Now create autoinstall file at `/var/www/html/nodes_groups/group_storage.cloud-init/user-data`

```yaml
#cloud-config
autoinstall:
  version: 1
  apt:
    geoip: false
    preserve_sources_list: true
  keyboard: {layout: us, toggle: null, variant: ''}
  locale: en_US.UTF-8
  user-data:
    users:
      - name: bluebanquise
        homedir: /home/bluebanquise
        ssh_authorized_keys:
          - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqpyyh44Hz3gvhISaIE9yJ/ao8fBLNo7qwPJcYjQdIl root@odin.cluster.local
        sudo: 'ALL=(ALL:ALL) NOPASSWD:ALL'
        groups: sudo
        shell: /bin/bash
        passwd: $6$7zvrwimYcypA8JWc$5GWYVF7zrI5eorsPN8IUT1n/Gmjpkic7h2cCbFVxbkqJeG0/kmJsYw6EN9oX3NQ34duwW7qAmOI13Y/0v5oHn.
    disable_root: true
  ssh:
    install-server: true
    allow-pw: true
```

Now create needed empty file at `/var/www/html/nodes_groups/group_storage.cloud-init/meta-data` (don't ask me why, but its mandatory):

```
touch /var/www/html/nodes_groups/group_storage.cloud-init/meta-data
```

Few notes:

* The Ubuntu installer needs a lot of ram to operate, since it downloads and extract iso into memory. Ensure at least 6 Gb ram.
* If anything happen wrong, installer automatically fallback to interactive installation mode. You will have to change shell and investigate into installer logs to find issue. This is not always easy as installer logs huge.
* If serial console is wrong, installer will fallback on interactive installation mode.
* If installer hang without errors, let it some time. Some steps try some connection and wait for timeout before continuing.

Other notes:
* The ssh public key here will allow us to ssh on the remote hosts without having to provide a password.
* We install only the absolute minimal operating system. It is strongly recommended to do the minimal amount of tasks during the auto-installation as it is way simpler to debug things installing once system is running.
* Ensure also your keyboard type is correct.
* For compatibility purpose, this example does not specify which hard drive disk to use, installer will auto-choose what to use. Tune it later according to your needs.

Now, ensure all services are started:

```
systemctl start apache2
systemctl enable apache2
systemctl start atftpd
systemctl enable atftpd
```

We can proceed with the boot of `thor` node, and then the other nodes.

## Other nodes installation

### Boot over PXE

Open 2 shell on `odin`. In the first one, launch watch logs of dhcp and tftp server using:

**If Ubuntu system**

```
journalctl -u isc-dhcp-server -u atftpd -f
```

**If RHEL system**

```
journalctl -u dhcpd -u atftpd -f
```

In the second one, watch http server logs using:

**If Ubuntu system**

```
tail -f /var/log/apache2/*
```

**If RHEL system**

```
tail -f /var/log/httpd/*
```

Now, boot the `thor` node over PXE, and watch it deploy. Also watch the logs to
understand all steps.

Once the operating system is installed, and the node has rebooted, have it boot
over disk, and ensure operating system is booted before proceeding.

Repeat this operation to deploy each nodes of your cluster.

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>Note: if you let nodes boot over PXE after reboot, they will again deploy, and enter in an infinite deployment loop.
There are strategies to solve that automatically, but this is out of the scope of this training. For now, simply change boot order after os deployment.</p>
    </div>
</div> -->

Note: if you let nodes boot over PXE after reboot, they will again deploy, and enter in an infinite deployment loop.
There are strategies to solve that automatically, but this is out of the scope of this training. For now, simply change boot order after os deployment.

### Configure client side

Now that other nodes are deployed and reachable over ssh, it is time to configure client side on them.

We will use clustershell (clush) a lot, as it allows to manipulate a lot of hosts over ssh at the same time. You can install clustershell either via packages (EPEL for RHEL, natively for Ubuntu) either via pip.

#### Set hostname

Set hostname on each nodes using the following command (tuned for each nodes of course):

```
hostnamectl set-hostname thor.cluster.local
```

#### Configure repositories

You need the nodes be able to grab packages from `odin`.

##### RHEL

On each client node, backup current repositories, and clean them:

```
cp -a /etc/yum.repos.d/ /root/yum.repos.d.backup
rm -f /etc/yum.repos.d/*.repo
```

Now create file `/etc/yum.repos.d/os.repo` with the following content:

```
[BaseOS]
name=BaseOS
baseurl=http://10.10.0.1/repositories/AlmaLinux/9/x86_64/os/BaseOS
gpgcheck=0
enabled=1

[AppStream]
name=AppStream
baseurl=http://10.10.0.1/repositories/AlmaLinux/9/x86_64/os/AppStream
gpgcheck=0
enabled=1
```

And create file `/etc/yum.repos.d/extra.repo` with the following content:

```
[Extra]
name=Extra
baseurl=http://10.10.0.1/repositories/AlmaLinux/9/x86_64/extra
gpgcheck=0
enabled=1
```

Now clean cache, and ensure you can reach the repositories and download packages (try to install wget for example):

```
dnf clean all
dnf update
dnf install wget -y
```

A simpler way can be also to copy `odin` repositories files directly on clients, and do all in parallel using clush.
Lets redo it, this time faster:

```
clush -bw thor,heimdall,valkyrie[01-02] 'cp -a /etc/yum.repos.d/ /root/yum.repos.d.backup'
clush -bw thor,heimdall,valkyrie[01-02] 'rm -f /etc/yum.repos.d/*.repo'
clush -w thor,heimdall,valkyrie[01-02] --copy /etc/yum.repos.d/* --dest /etc/yum.repos.d/
clush -bw thor,heimdall,valkyrie[01-02] 'dnf clean all'
clush -bw thor,heimdall,valkyrie[01-02] 'dnf update -y'
clush -bw thor,heimdall,valkyrie[01-02] 'dnf install wget -y'
```

##### Ubuntu

On each client, simply upload the extra.sources file we created on our Odin server, and done!
Just remember to apt update to have it taken into account.

For a single host:

```
scp /etc/apt/sources.list.d/extra.sources bluebanquise@thor:/etc/apt/sources.list.d/extra.sources
```

Or in parallel using clustershell:

```
clush -w thor,heimdall,valkyrie[01-02] --copy /etc/apt/sources.list.d/extra.sources --dest /etc/apt/sources.list.d/extra.sources
```

#### DNS client

IF not already automatically done from DHCP, on each client node, set `odin` as default DNS server by using previously seen nmcli commands (take this opportunity to set static ips on hosts).

#### Hosts file

On each client, edit `/etc/hosts` file and have it match the following:

```
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

10.10.0.1   odin
10.10.1.1   thor
10.10.2.1   heimdall
10.10.3.1   valkyrie01
10.10.3.2   valkyrie02
```

You can also simply upload the file from `odin` on clients, using clush.

#### Time client

On each client, ensure time server is `odin` sp that our cluster is time synchronised.

Install needed packages:

**If Ubuntu system**

```
apt install chrony
```

**If RHEL system**

```
dnf install chrony
```

Configuration file is `/etc/chrony.conf`. The file content should be as bellow:

```
# Source server to bind to
server 10.10.0.1 iburst

# Record the rate at which the system clock gains/losses time.
driftfile /var/lib/chrony/drift

# Allow the system clock to be stepped in the first three updates
# if its offset is larger than 1 second.
makestep 1.0 3

# Enable kernel synchronization of the real-time clock (RTC).
rtcsync

# Specify directory for log files.
logdir /var/log/chrony
```

Ensure client can communicate with the server.

Stop service:

```
systemctl stop chronyd
```

And force a clock sync:

```
chronyd -q 'server 10.10.0.1 iburst'
```

If you get the following (or something close) then your clock can sync from server:

```
chronyd version 3.5 starting (+CMDMON +NTP +REFCLOCK +RTC +PRIVDROP +SCFILTER +SIGND +ASYNCDNS +SECHASH +IPV6 +DEBUG)
Initial frequency 12.820 ppm
System clock wrong by 0.000050 seconds (step)
chronyd exiting
```

However, if you get something similar to this:

```
chronyd version 3.5 starting (+CMDMON +NTP +REFCLOCK +RTC +PRIVDROP +SCFILTER +SIGND +ASYNCDNS +SECHASH +IPV6 +DEBUG)
Initial frequency 12.820 ppm
No suitable source for synchronisation
chronyd exiting
```

It means something went wrong (firewall ?).

Then start and enable service:

```
systemctl start chronyd
systemctl enable chronyd
```

Again, you can use clush to do all these tasks in parallel on all client nodes.

Our nodes are now configured with the very basic needs. Time to focus on storage.

## Storage

Storage is hosted on `thor`. We will share `/home` and `/software` from this server.
Then we will mount these directories on the login node `heimdall` and computes nodes `valkyrie01,valkyrie02`.

### NFS server

Ssh on `thor`.

Now ensure first these 2 directories exist:

```
mkdir /home
mkdir /software
```

Now, install needed packages:

**If Ubuntu system**

```
apt install nfs-kernel-server -y
```

**If RHEL system**

```
dnf install nfs-utils -y
```

Now, ask the nfs server daemon to export those directories over the network.

Since `/home` is expected to be used by users to store there data, it must be read/write access.
On the other hand, `/software` is designed to provide software (compiler, libraries, etc.) across
the cluster, and so it should be read only access.

Edit `/etc/exports` file, and add the 2 exported folders with good parameters:

```
/home 10.10.0.0/16(rw,no_root_squash,sync)
/software 10.10.0.0/16(ro,no_root_squash,sync)
```

Simply put, we ask here nfs-server to export both directories, restricted only to the
10.10.0.0/16 subnet. Note that one is `rw` (read/write), the other is `ro` (read only).

Start now the nfs-server:

```
systemctl start nfs-server
systemctl enable nfs-server
```

Now, ensure the exports are working, using the following command targeting the server ip:

```
showmount -e thor
```

You should see the exports available on this server.

### NFS clients

Ssh on `heimdall`.

Install needed packages to mount nfs foreign export:

**If Ubuntu system**

```
apt install nfs-common -y
```

**If RHEL system**

```
dnf install nfs-utils -y
```

Now edit `/etc/fstab` file, and add the 2 entries needed for our folders exported by `thor`:

```
thor:/home /home nfs rw,rsize=32768,wsize=32768,intr,nfsvers=4,bg 0 0
thor:/software /software nfs ro,intr,nfsvers=4,bg 0 0
```

Note: bg parameter ensure that the mounts are done in background mode. This avoid
blocking the system at boot if these folder are not reachable (for example if `thor` server is down at this very moment).

Now ask for mount of them:

```
mkdir /software
mkdir /home
mount /home
mount /software
```

And ensure they are mounted using `df` command.

Redo these client steps on all other clients, so computes nodes `valkyrie01,valkyrie02`,
so that the exported folders are available on each nodes where users interact.

## Users

To have users on the cluster, you need to have the users registered on each node, with same pid and same group gid.

There are multiple ways to synchronize users on a cluster of nodes. Popular tools are based on Ldap or Ad.
However, this is out of the scope of this tutorial, and so we will manage users manually on our small cluster.

To generate a user with a fix pid and fix gid, use the following commands on `heimdall` login node:

```
groupadd -g 2001 myuser
adduser myuser --shell /bin/bash -d /home/myuser -u 2001 -g 2001
mkdir /home/myuser
chown -R myuser:myuser /home/myuser
```

Then on all other nodes, including `thor` and `odin`, create user only (no need to recreate the `/home` as it is spread over NFS)

On each other nodes, do the following:

```
groupadd -g 2001 myuser
adduser myuser --shell /bin/bash -d /home/myuser -u 2001 -g 2001
```

Note: for each new user, increment the user number (2002 -> 2003 -> 2004 -> etc.).
Also, use number above 2000 to avoid issues or conflict with possible system ids.

It is important to understand that using manual methods to add users may seems simple, but has a major drawback: the cluster can quickly become out of synchronization regarding users.
To prevent that, you can create scripts, rely on automation tools like Ansible, or use a centralized users database (OpenLDAP, etc.).

## Infiniband (optional)

This part is RHEL only, I never was able to get Infiniband hardware on Ubuntu, so I cannot test it.

If you need InfiniBand support on nodes, simply install the package group related:

```
dnf groupinstall 'infiniband support'
```

And then enable rdma service:

```
systemctl start rdma
systemctl enable rdma
```

You should now see the ib0 interface in the NIC list from `ip a`.

## Nvidia GPU (optional)

This part is RHEL only, I never was able to get Nvidia GPU hardware on Ubuntu, so I cannot test it.

To setup an GPU, you need to:

* Ensure kernel do not crash at start (happen often if kernel is too old for hardware)
* Ensure **nouveau** driver do not prevent Nvidia driver to load
* Ensure Nvidia driver load

You can then install CUDA build and runtime environment on a shared space, or on each nodes, as you wish.

Lets do that step by step.

### Ensure kernel do not crash

To prevent kernel from crashing at boot (Kernel Panic) due to too recent GPU hardware, edit the ipxe file that contains the kernel line
(for example file `/var/www/html/nodes_groups/group_compute_gpu.ipxe` and append `nomodeset` to the kernel line. For example on RHEL (same for Ubuntu, just update the corresponding file):

```
#!ipxe

echo Booting OS
echo Group profile: compute_gpu

echo +----------------------------------------------------+
echo |
echo | Loading kernel

kernel http://${next-server}/repositories/AlmaLinux/9/x86_64/os/images/pxeboot/vmlinuz initrd=initrd.img inst.stage2=http://${next-server}/repositories/AlmaLinux/9/x86_64/os/ inst.repo=http://${next-server}/repositories/AlmaLinux/9/x86_64/os/BaseOS/ ks=http://${next-server}/nodes_groups/group_compute_gpu.kickstart.cfg nomodeset

echo | Loading initial ramdisk ...

initrd http://${next-server}/repositories/AlmaLinux/9/x86_64/os/images/pxeboot/initrd.img

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
```

Also, edit kickstart file, for example here file `/var/www/html/nodes_groups/group_compute_gpu.kickstart.cfg`, and ensure the same is added to the bootloader parameter.
So for example, in the kickstart file, ensure you have this line:

```
bootloader --append="nomodeset" --location=mbr
```

Node should not crash anymore.

### Disable nouveau driver

Again, redo the same process than before, but add another kernel parameter: `modprobe.blacklist=nouveau nouveau.modeset=0 rd.driver.blacklist=nouveau`

So edit ipxe `/var/www/html/nodes_groups/group_compute_gpu.ipxe` file again:

```
#!ipxe

echo Booting OS
echo Group profile: compute_gpu

echo +----------------------------------------------------+
echo |
echo | Loading kernel

kernel http://${next-server}/repositories/AlmaLinux/9/x86_64/os/images/pxeboot/vmlinuz initrd=initrd.img inst.stage2=http://${next-server}/repositories/AlmaLinux/9/x86_64/os/ inst.repo=http://${next-server}/repositories/AlmaLinux/9/x86_64/os/BaseOS/ ks=http://${next-server}/nodes_groups/group_compute_gpu.kickstart.cfg nomodeset modprobe.blacklist=nouveau nouveau.modeset=0 rd.driver.blacklist=nouveau

echo | Loading initial ramdisk ...

initrd http://${next-server}/repositories/AlmaLinux/9/x86_64/os/images/pxeboot/initrd.img

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
```

And edit `/var/www/html/nodes_groups/group_compute_gpu.kickstart.cfg` file again:

```
bootloader --append="nomodeset modprobe.blacklist=nouveau nouveau.modeset=0 rd.driver.blacklist=nouveau" --location=mbr
```

Now, node will boot without `nouveau` driver loaded.

### Install Nvidia driver

Grab driver from Nvidia website, that match your hardware and Linux distribution (and arch).

Now install epel repository:

```
dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
```

Now install Nvidia repository:

```
ARCH=$( /bin/arch )
distribution=$(. /etc/os-release;echo $ID`rpm -E "%{?rhel}%{?fedora}"`)
dnf config-manager --add-repo http://developer.download.nvidia.com/compute/cuda/repos/$distribution/${ARCH}/cuda-rhel8.repo
```

Install needed kernel headers:

```
dnf install -y kernel-devel-$(uname -r) kernel-headers-$(uname -r)
```

And install driver

```
dnf clean all
dnf -y module install nvidia-driver:latest-dkms
```

## Other distributions

Here are how to deploy the other commons distributions. Note that all what we have seen so fare apply the same, packages names are just different, and some configuration path might also change, but tools are the same on all distributions.

I will go straight to the point here, adapt to your needs once it worked this way.

Just a quick pro and cons on all PXE solutions:

* RHEL:
  * Pros:
    * Good documentation
    * Kickstart format is efficient, especially for those who like scripting
  * Cons:
    * Anaconda installer often crashes without explanations
    * Some disks (especially old raids) are often not available for installer (even if seen by kernel)
* Ubuntu:
  * Pros:
    * YAML format is efficient for configuration file
  * Cons:
    * Installer often falls back to interactive installation if anything is wrong, and does not advertise why (need to spend time searching in logs)
    * Weird behavior with some serial consols
    * No detailed documentation
* Debian:
  * Pros:
    * Light installer
  * Cons:
    * Lack of documentation
    * Some missing key features in preseed autoinstall (like support for multiple NICs, you need to manually define wich one to use)
* OpenSuse Leap:
  * Pros:
    * Nice installer
    * Good documentation
  * Cons:
    * XML not efficient for configuration file
    * Need to manage some 2 part install (install and post-install)

### Ubuntu 20.04 and 22.04

Since 20.04, LTS versions of Ubuntu do not rely anymore on preseed, but on a new mechanism.
In this example, we will cover deployment of Ubuntu 22.04, but it is the same for 20.04.

To deploy Ubuntu over the network:

1. Prepare folders:

```
mkdir -p /var/www/html/pxe/ubuntu/22.04/
mkdir -p /var/www/html/pxe/ubuntu/22.04/iso_content/
mkdir -p /var/www/html/pxe/ubuntu/22.04/autoinstall.cloud-init/

```

2. Download Ubuntu 22.04 live server iso, put it in `/var/www/html/pxe/ubuntu/22.04/` folder and mount it also in `/var/www/html/pxe/ubuntu/22.04/iso_content/` (or copy its content here, its up to you).

```
cd /var/www/html/pxe/ubuntu/22.04/
wget https://releases.ubuntu.com/22.04/ubuntu-22.04.1-live-server-amd64.iso
mv ubuntu-22.04.1-live-server-amd64.iso ubuntu-22.04-live-server-amd64.iso
mount ubuntu-22.04-live-server-amd64.iso /var/www/html/pxe/ubuntu/22.04/iso_content/
```

3. Create autoinstall file at `/var/www/html/pxe/ubuntu/22.04/autoinstall.cloud-init/user-data`

```yaml
#cloud-config
autoinstall:
  version: 1
  apt:
    geoip: false
    preserve_sources_list: true
  keyboard: {layout: us, toggle: null, variant: ''}
  locale: en_US.UTF-8
  user-data:
    users:
      - name: bluebanquise
        homedir: /home/bluebanquise
        ssh-authorized-keys:
          - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqpyyh44Hz3gvhISaIE9yJ/ao8fBLNo7qwPJcYjQdIl root@odin.cluster.local
        sudo: ['ALL=(ALL:ALL) NOPASSWD:ALL']
        groups: sudo
        shell: /bin/bash
        passwd: "!"  # Means no password
    disable_root: true
  ssh:
    install-server: true
    allow-pw: true
```

4. Create needed empty file at `/var/www/html/pxe/ubuntu/22.04/autoinstall.cloud-init/meta-data` (don't ask me why, but its mandatory):

```
touch /var/www/html/pxe/ubuntu/22.04/autoinstall.cloud-init/meta-data
```

5. Create ipxe file to boot:

```
#!ipxe

echo Booting OS

echo +----------------------------------------------------+
echo |
echo | Loading kernel

kernel http://${next-server}/pxe/ubuntu/22.04/iso_content/casper/vmlinuz initrd=initrd root=/dev/ram0 ramdisk_size=1500000 ip=dhcp url=http://${next-server}/pxe/ubuntu/22.04/ubuntu-22.04-live-server-amd64.iso autoinstall ds=nocloud-net;s=http://${next-server}/pxe/ubuntu/22.04/autoinstall.cloud-init/

echo | Loading initial ramdisk ...

initrd http://${next-server}/pxe/ubuntu/22.04/iso_content/casper/initrd

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
```

Few notes:

* The Ubuntu installer needs a lot of ram to operate, since it downloads and extract iso into memory. Ensure at least 4 or even 6 Gb ram.
* If anything happen wrong, installer automatically fallback to interactive installation mode. You will have to change shell and investigate into installer logs to find issue. This is not always easy as installer logs huge.
* If serial console is wrong, installer will fallback on interactive installation mode.
* If installer hang without errors, let it some time. Some steps try some connection and wait for timeout before continuing.

### Debian 11 and 12

Debian uses preseed file to configure auto-installation. Preseed is difficult to use due to a strange lack of **detailed** documentation.
Also, you will need to have access to external repositories to perform the deployment (I wasn't able to deploy Debian with local repositories as I cannot find the preseed tag to allow unauthenticated repos at second stage), which involves that all your nodes have access to a gateway to reach the web. Installation is done using a netboot and not an ISO.

To deploy Debian over the network:

1. Prepare folders:

```
mkdir -p /var/www/html/pxe/debian/12/
mkdir -p /var/www/html/pxe/debian/12/iso_content/
```

2. Download Debian 12 bootstrap, put it in `/var/www/html/pxe/debian/12/` folder and extract part of it in `/var/www/html/pxe/debian/12/iso_content/`.

```
cd /var/www/html/pxe/debian/12/
wget https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/netboot/netboot.tar.gz
tar xvzf netboot.tar.gz
cp debian-installer/amd64/initrd.gz /var/www/html/pxe/debian/12/iso_content/
cp debian-installer/amd64/linux /var/www/html/pxe/debian/12/iso_content/

```

3. Create autoinstall file at /var/www/html/pxe/debian/12/preseed.cfg

```
### zone
d-i debian-installer/locale string en_US.UTF-8
d-i keyboard-configuration/xkb-keymap select us
d-i debian-installer/language string en
d-i debian-installer/country string US
d-i localechooser/supported-locales multiselect en_US.UTF-8

### network
## Note: a dhcp gateway MUST be set for the network, even a dummy one
d-i netcfg/choose_interface select auto
d-i netcfg/use_dhcp string true
d-i netcfg/link_wait_timeout string 10
d-i netcfg/dhcp_timeout string 60
d-i netcfg/dhcp_failed note
d-i netcfg/wireless_wep string
d-i netcfg/get_hostname unassigned-hostname
d-i netcfg/get_domain unassigned-domain
d-i netcfg/get_hostname seen true
d-i netcfg/get_domain seen true

### Repositories
d-i mirror/country string manual
d-i mirror/http/hostname string deb.debian.org
d-i mirror/http/directory string /debian
d-i mirror/http/proxy string

### Time
d-i clock-setup/utc-auto boolean true
d-i clock-setup/utc boolean true
d-i time/zone string Europe/Brussels #US/Pacific
d-i clock-setup/ntp boolean true

### Partitioning
d-i partman-lvm/device_remove_lvm boolean true
d-i partman-md/device_remove_md boolean true
d-i partman-lvm/confirm boolean true
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true

d-i partman-auto/disk string /dev/vda
d-i partman-auto/method string regular
d-i partman-auto/choose_recipe select atomic
d-i partman-auto/init_automatically_partition select Guided - use entire disk

### Users
d-i passwd/root-login boolean false
d-i passwd/user-fullname string Bluebanquise User
d-i passwd/username string bluebanquise
d-i passwd/user-password-crypted password !

### Packages
tasksel tasksel/first multiselect minimal
d-i pkgsel/include string openssh-server curl python3
d-i pkgsel/upgrade select none
d-i pkgsel/updatedb boolean false
d-i pkgsel/update-policy select none
d-i apt-setup/restricted boolean false
d-i apt-setup/universe boolean false
d-i apt-setup/backports boolean false
d-i apt-setup/proposed boolean false
popularity-contest popularity-contest/participate boolean false

### Grub
d-i grub-installer/only_debian boolean true
d-i grub-installer/bootdev  string default

### Reboot
d-i finish-install/reboot_in_progress note

### Add our user
d-i preseed/late_command string \
  in-target sh -c '/sbin/usermod -m -d /home/bluebanquise bluebanquise'; \
  in-target sh -c 'mkdir /home/bluebanquise/.ssh'; \
  in-target sh -c 'echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqpyyh44Hz3gvhISaIE9yJ/ao8fBLNo7qwPJcYjQdIl root@odin.cluster.local" >> /home/bluebanquise/.ssh/authorized_keys';\
  in-target sh -c 'chown -R bluebanquise:bluebanquise /home/bluebanquise/.ssh'; \
  in-target sh -c 'sed -i "s/^#PermitRootLogin.*\$/PermitRootLogin no/g" /etc/ssh/sshd_config'; \
  in-target sh -c 'echo "bluebanquise ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers.d/bluebanquise'
```

4. Create ipxe file to boot:

Important note: if your server have more than 1 NIC, then you need to hardcode it on the kernel command line. See comment in the file.

```
#!ipxe

echo Booting OS

echo +----------------------------------------------------+
echo |
echo | Loading kernel

kernel http://${next-server}/pxe/debian/12/iso_content/linux initrd=initrd.gz preseed/url=http://${next-server}/pxe/debian/12/preseed.cfg auto=true priority=critical

# If your server have more than 1 NIC, assuming here its enp0s1 (you might need to boot it once to know the NIC name and adjust here)
# kernel http://${next-server}/pxe/debian/12/iso_content/linux initrd=initrd.gz preseed/url=http://${next-server}/pxe/debian/12/preseed.cfg auto=true priority=critical netcfg/choose_interface=enp0s1

echo | Loading initial ramdisk ...

initrd http://${next-server}/pxe/debian/12/iso_content/initrd.gz

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
```

Few notes:

* You absolutely need to have a gateway defined to make it automatic.
* If installer does not see your SATA/NvME disks, then it means it couldn't grab modules from repo (try using an official repo). It is possible to inject modules from the DVD iso manually, see https://github.com/bluebanquise/infrastructure/blob/29b503eab507b056f9658f36e01287192e8b66cb/Validation/steps/12_deploy_debian11.sh#L16
* I found not working automatic disk selection, you need to manually define it like in this preseed example above (here /dev/sda).

### OpenSUSE Leap 15

OpenSuse AutoYast installer is a stable installer. It is however slower than the others, XML of autoyast file is a pain, and you have to handle the second stage installation. But globally, this installer is nice to use.

1. Prepare folders:

```
mkdir -p /var/www/html/pxe/leap/15/
mkdir -p /var/www/html/pxe/leap/15/iso_content/
```

2. Download OpenSuse Leap 15 iso, put it in `/var/www/html/pxe/leap/15/` folder and mount or extract in `/var/www/html/pxe/leap/15/iso_content/`.

```
cd /var/www/html/pxe/leap/15/
wget https://mirror.its.dal.ca/opensuse/distribution/leap/15.4/iso/openSUSE-Leap-15.4-DVD-x86_64-Build243.2-Media.iso
mount openSUSE-Leap-15.4-DVD-x86_64-Build243.2-Media.iso /var/www/html/pxe/leap/15/iso_content/
```

3. Create autoinstall file at /var/www/html/pxe/leap/15/autoyast.xml

```xml
<?xml version="1.0"?>
<!DOCTYPE profile>
<profile xmlns="http://www.suse.com/1.0/yast2ns" xmlns:config="http://www.suse.com/1.0/configns">

  <add-on>
    <add_on_products config:type="list">
    </add_on_products>
  </add-on>

  <keyboard>
    <keymap>us</keymap>
  </keyboard>

  <language>
    <language>en_US</language>
    <languages/>
  </language>

  <timezone>
    <hwclock>UTC</hwclock>
    <timezone>Europe/Brussels</timezone>
  </timezone>


  <networking>
    <keep_install_network config:type="boolean">true</keep_install_network>
    <managed config:type="boolean">true</managed>
  </networking>

  <software>
    <install_recommended config:type="boolean">true</install_recommended>
    <patterns config:type="list">
      <pattern>base</pattern>
    </patterns>
    <packages config:type="list">
      <package>openssh-server</package>
      <package>sudo</package>
    </packages>
  </software> 

  <bootloader>
    <loader_type>default</loader_type>
  </bootloader>

<partitioning config:type="list">
  <drive>
    <initialize config:type="boolean">true</initialize>
    <use>all</use>
    <partitions config:type="list">
      <partition>
        <filesystem config:type="symbol">ext4</filesystem>
        <mount>/</mount>
        <size>max</size>
      </partition>
      <partition>
        <filesystem config:type="symbol">ext4</filesystem>
        <mount>/boot</mount>
        <size>512MiB</size>
      </partition>
      <partition>
        <mount>swap</mount>
        <size>512MiB</size>
      </partition>
    </partitions>
  </drive>
</partitioning>

  <!-- disable root password and add ssh keys to sudo user -->
  <users config:type="list">
    <user>
      <username>root</username>
      <user_password>!</user_password>
      <encrypted config:type="boolean">true</encrypted>
    </user>
    <user>
      <username>bluebanquise</username>
      <home>/home/bluebanquise</home>
      <user_password>!</user_password>
      <encrypted config:type="boolean">true</encrypted>
      <authorized_keys config:type="list">
        <listentry>ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqpyyh44Hz3gvhISaIE9yJ/ao8fBLNo7qwPJcYjQdIl root@odin.cluster.local</listentry>
      </authorized_keys>
    </user>
  </users>

<services-manager>
  <default_target>multi-user</default_target>
  <services>
    <enable config:type="list">
      <service>sshd</service>
    </enable>
  </services>
</services-manager>

<scripts>
    <chroot-scripts config:type="list">
      <script>
        <chrooted config:type="boolean">true</chrooted>
        <filename>add_sles_sudo_rule.sh</filename>
        <interpreter>shell</interpreter>
        <source>
<![CDATA[
#!/bin/sh
echo "Defaults:sles !targetpw
bluebanquise ALL=(ALL,ALL) NOPASSWD: ALL" > /etc/sudoers.d/bluebanquise
]]>
          </source>
      </script>
    </chroot-scripts>
  </scripts>

<general>
  <mode>
    <confirm config:type="boolean">false</confirm>
  </mode>
  <!-- Be sure to understand that and adapt to your needs, this is used here to allow local repos -->
  <signature-handling>
    <accept_unsigned_file config:type="boolean">true</accept_unsigned_file>
    <accept_unknown_gpg_key config:type="boolean">true</accept_unknown_gpg_key>
    <accept_non_trusted_gpg_key config:type="boolean">true</accept_non_trusted_gpg_key>
    <import_gpg_key config:type="boolean">true</import_gpg_key>
  </signature-handling>
 </general>

</profile>
```

4. Create ipxe file to boot:

Note: you can change textmode=1 to textmode=0 if you wish to see the GUI of the installer on screen (if not using a serial console).

```
#!ipxe

echo Booting OS

echo +----------------------------------------------------+
echo |
echo | Loading kernel

kernel http://${next-server}/pxe/leap/15/iso_content/boot/x86_64/loader/linux install=http://${next-server}/pxe/leap/15/iso_content/ autoyast=http://${next-server}/pxe/leap/15/autoyast.xml textmode=1

echo | Loading initial ramdisk ...

initrd http://${next-server}/pxe/leap/15/iso_content/boot/x86_64/loader/initrd

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
```

Few notes:

* You will need after boot to configure either NetworkManager or systemd-networkd if you wish to use a tool like Ansible or equivalent, as embed network manager does not seems to be supported by all these tools.

## Conclusion

CONGRATULATION!! The cluster is ready to be used!!

Next step now is to learn how to automate what we did here. Proposal in next tutorial is based on Ansible but you can user other tools like Salt Stak, Pupper, Chef, etc. >> [Ansible tutorial](sysadmin_ansible.md).

Or you can also specialize the cluster, with [HPC cluster tutorial](hpc_slurm.md) or [K8S cluster tutorial](kubernetes_deploy.md).

<!-- <div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/avatar.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>Thank you for following this tutorial. If you find something is missing, or find an issue, please notify the me on github by opening an issue or a PR :)</p>
    </div>
</div> -->

Thank you for following this tutorial. If you find something is missing, or find an issue, please notify the me on github by opening an issue or a PR :)

