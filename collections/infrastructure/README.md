# Infrastructure

Infrastructure collection of roles for BlueBanquise collection set.

This collection regroups all roles related to basic deployment of nodes (servers, VMs, etc.) of a non specialized cluster.

## List of plugins:

* [plugins/modules/networkd](plugins/modules/networkd): systemd-networkd module to provide a nmcli equivalent module from community.general, but dedicated to networkd-systemd (mainly for Debian/Ubuntu).

## List of roles:

* [roles/access_control](roles/access_control): configure access control (SELinux / AppArmor).
* [roles/clustershell](roles/clustershell): configure and install clustershell (parallel shell).
* [roles/conman](roles/conman): configure and install conman (IPMI consoles).
* [roles/cron](roles/cron): configure cron rules.
* [roles/dhcp_server](roles/dhcp_server): configure and install a dhcp server.
* [roles/dns_client](roles/dns_client): configure `/etc/resolv.conf`. Note that this role should not be used when using NetworkManager or systemd-networkd as this file is managed by these services.
* [roles/dns_server](roles/dns_server): configure and install a dns server.
* [roles/firewall](roles/firewall): configure firewall. Role is currently limited to Firewalld.
* [roles/hosts_file](roles/hosts_file): generate the `/etc/hosts` file.
* [roles/http_server](roles/http_server): install and configure an http server.
* [roles/kernel_config](roles/kernel_config): configure systctl and kernel command line.
* [roles/modprobe](roles/modprobe): load/unload kernel modules.
* [roles/nic](roles/nic): configure network interfaces (nic) using either NetworkManager (RedHat/Suse) or systemd-networkd (Debian/Ubuntu).
* [roles/pam_limits](roles/pam_limits): set pam limits for users.
* [roles/powerman](roles/powerman): install and configure powerman.
* [roles/pxe_stack](roles/pxe_stack): install and configure everything needed to boot and deploy remote nodes via PXE.
* [roles/repositories](roles/repositories): configure OS packages repositories.
* [roles/root_password](roles/root_password): configure root password on non sudo systems.
* [roles/set_hostname](roles/set_hostname): set hostname on remote host.
* [roles/ssh_client](roles/ssh_client): configure `.ssh/config` file.
* [roles/ssh_remote_keys](roles/ssh_remote_keys): set `.ssh/authorized_keys` file on remote host.
* [roles/sudoers](roles/sudoers): configure host sudo users.
* [roles/system](roles/system): all in one wrapper for basic operations: package, file, template, service, lineinfile.
* [roles/time](roles/time): install and configure chrony ntp server/client.
* [roles/update_reboot](roles/update_reboot): update system and/or reboot system.
* [roles/users](roles/users): configure local users (can replace centralized authentication like LDAP for a small cluster).
