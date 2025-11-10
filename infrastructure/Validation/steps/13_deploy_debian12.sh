#!/bin/bash
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export mgt1_ip=$(virsh net-dhcp-leases default | grep '52:54:00:fa:12:01' | tail -1 | awk -F ' ' '{print $5}' | sed 's/\/24//')
# Prepare target deployment
mgt1_PYTHONPATH=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip pip3 show ClusterShell | grep Location | awk -F ' ' '{print $2}')

cd $CURRENT_DIR/../http
# wget -nc --no-parent -r -l 0 --cut-dirs 5 -nH -A iso https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/
# export DEBIAN_ISO=$(ls debian*.iso)
rm -f netboot.tar.gz
wget -nc https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/netboot/netboot.tar.gz
cd $CURRENT_DIR

ssh -o StrictHostKeyChecking=no bluebanquise@$mgt1_ip rm -Rf netboot.tar.gz debian-installer
ssh -o StrictHostKeyChecking=no bluebanquise@$mgt1_ip wget -nc http://$host_ip:8000/netboot.tar.gz
# ssh -o StrictHostKeyChecking=no bluebanquise@$mgt1_ip wget -nc http://$host_ip:8000/$DEBIAN_ISO

# ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
# # Debian preparation is extensive, we need to inject ata/scsi modules into netboot initrd
# sudo mkdir -p /var/www/html/pxe/netboots/debian/11/x86_64/
# sudo mount $DEBIAN_ISO /mnt
# sudo rm -Rf /tmp/netboot
# mkdir -p /tmp/netboot/iso
# mkdir /tmp/netboot/netboot
# cp /mnt/install.amd/initrd.gz /tmp/netboot/iso/
# tar xvzf netboot.tar.gz
# cp debian-installer/amd64/initrd.gz /tmp/netboot/netboot/
# sudo cp debian-installer/amd64/linux /var/www/html/pxe/netboots/debian/11/x86_64/
# cd /tmp/netboot/iso/
# gunzip initrd.gz
# mkdir -p tmp2
# cd tmp2
# sudo cpio -id < ../initrd
# cd /tmp/netboot/netboot/
# gunzip initrd.gz
# mkdir -p tmp2
# cd tmp2
# sudo cpio -id < ../initrd
# cd lib/modules/*-amd64/kernel/drivers
# cd scsi
# sudo cp -a /tmp/netboot/iso/tmp2/lib/modules/*-amd64/kernel/drivers/scsi/* .
# cd ../
# sudo cp -a /tmp/netboot/iso/tmp2/lib/modules/*-amd64/kernel/drivers/ata .
# cd /tmp/netboot/netboot/tmp2/
# find . | cpio --create --format='newc' > /tmp/newinitrd
# cd /tmp
# gzip newinitrd
# sudo mv newinitrd.gz /var/www/html/pxe/netboots/debian/11/x86_64/initrd.gz

# export PYTHONPATH=$mgt1_PYTHONPATH
# sudo bluebanquise-bootset -n mgt9 -b osdeploy
# # temporary fix
# sudo mkdir -p /var/www/html/preboot_execution_environment/
# cd /var/www/html/preboot_execution_environment/
# sudo rm -f convergence.ipxe
# sudo ln -s ../pxe/convergence.ipxe convergence.ipxe
# EOF

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
# Debian preparation is extensive, we need to inject ata/scsi modules into netboot initrd
sudo mkdir -p /var/www/html/pxe/netboots/debian/12/x86_64/iso/
tar xvzf netboot.tar.gz
sudo cp debian-installer/amd64/initrd.gz /var/www/html/pxe/netboots/debian/12/x86_64/iso/
sudo cp debian-installer/amd64/linux /var/www/html/pxe/netboots/debian/12/x86_64/iso/

export PYTHONPATH=$mgt1_PYTHONPATH
sudo bluebanquise-bootset -n mgt9 -b osdeploy
EOF

virsh destroy mgt9 && echo "mgt9 destroyed" || echo "mgt9 not found, skipping"
virsh undefine mgt9 && echo "mgt9 undefined" || echo "mgt9 not found, skipping"

virt-install --name=mgt9 --os-variant debian11 --ram=6000 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/mgt9.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=1a:2b:3c:4d:9e:8f --pxe
virsh setmem mgt9 2G --config
virsh start mgt9

# Validation step
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh-keygen -f "/var/lib/bluebanquise/.ssh/known_hosts" -R mgt9
/tmp/waitforssh.sh bluebanquise@mgt9
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt9 hostname
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt9 sudo curl http://bluebanquise.com/repository/releases/latest/deb12/x86_64/bluebanquise/bluebanquise.list --output /etc/apt/sources.list.d/bluebanquise.list
EOF
set +e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
set -x
sleep 200 # wait for network to stabilize
ssh -o StrictHostKeyChecking=no mgt9 'DEBIAN_FRONTEND=noninteractive sudo apt update && sudo apt upgrade -y && sudo reboot -h now'
EOF
set -e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
/tmp/waitforssh.sh bluebanquise@mgt9
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
source /var/lib/bluebanquise/ansible_venv/bin/activate
cd validation/inventories/ 
export ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.commons.core
export ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do
ansible-playbook ../playbooks/managements.yml -i minimal_extended --limit mgt9 -b
EOF
if [ $? -eq 0 ]; then
  echo SUCCESS deploying Debian 12 mgt9
else
  echo FAILED deploying Debian 12 mgt9
  exit 1
fi

# Cleaning
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo rm /var/lib/bluebanquise/netboot.tar.gz
EOF
virsh shutdown mgt9
