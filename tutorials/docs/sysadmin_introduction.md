# System administration introduction

The following tutorials are available:

* [Servers farm deployment and system administration](sysadmin_servers_farm_deployment.md)
* [Learn Ansible basics to automate deployments](sysadmin_ansible.md)
* [Basic monitoring with Prometheus](sysadmin_monitoring.md)

You can find also bellow some recommendations that could help on your day to day duties.

## Equipment

The following list of equipment prove to help when delivering IT equipment inside datacenters.

1. A Linux based laptop. Whatever distribution you need (I recommend Debian, as its very standard). This does not prevent you to have Microsoft Windows or MacOS on another computer, but a Linux based computer prove to be a real help on site. You can have Microsoft Windows installed on the internal SSD of the laptop, and Debian installed on an USB SSD, so boot on the one needed depending of tasks (use EFI for that, its simpler than managing MBRs and dual boots).

2. 2 ethernet cables, around 5 to 10 meters long, and a small ethernet switch. **It is important that one of the 2 cables have on one side the locking clip broken**: reason is, many hardware providers find fun to put BMCs ethernet ports just above the chassis, and you can't remove easily the cable once its plugged in due to the lock (you cant reach it). Using a broken cable for such hardware makes your life easier.

3. 1 Ethernet/USB to Serial cable, to manage some ethernet switches.

4. Basic tooling: screwdrivers (small, bigs, and long ones), electrical scotch tape, a small flash light, 

5. Basic protections and first aid kit (many parts can be sharp).

6. Water. We tend to forget to drink, and its bad for concentration. (And if you drink enough water, it later forces you to do a break...)

Never have on you something in metal that could be in contact with electrical components. When manipulating hardware, ensure you do not have a watch, a chain around neck, or a bracelet.

## Software

It is nice to have on your system few VMs, bridged to your Ethernet card, that you can start on demand.

This VM would embed a small DHCP server, and be able to boot a target in PXE.

Then it would allow this via PXE:

* Boot a CloneZilla live, to clone target server disk.
* Boot an alpine live, latest version, to have a recent kernel available to test some hardware.
* Deploy a basic distribution, like RHEL, Ubuntu, Debian, Suse, etc, so you can easily bootstrap your management servers without having to rely on a USB key.

Note that a small Raspberry pi can perfectly do all of that instead of a VM. Its up to you. Nmap tool is also your friend.
