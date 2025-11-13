#!/bin/bash
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -x
export mgt1_ip=$(virsh net-dhcp-leases default | grep '52:54:00:fa:12:01' | tail -1 | awk -F ' ' '{print $5}' | sed 's/\/24//')
# Prepare target deployment
mgt1_PYTHONPATH=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip pip3 show ClusterShell | grep Location | awk -F ' ' '{print $2}')

if (( $STEP < 11 )); then

cd $CURRENT_DIR/../http
wget -nc https://repo.almalinux.org/almalinux/8/isos/x86_64/AlmaLinux-8-latest-x86_64-dvd.iso
cd $CURRENT_DIR

ssh -o StrictHostKeyChecking=no bluebanquise@$mgt1_ip wget -nc http://$host_ip:8000/AlmaLinux-8-latest-x86_64-dvd.iso

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
set -x
sudo mkdir -p /var/www/html/pxe/netboots/redhat/8/x86_64/iso
sudo mount /var/lib/bluebanquise/AlmaLinux-8-latest-x86_64-dvd.iso /var/www/html/pxe/netboots/redhat/8/x86_64/iso
export PYTHONPATH=$mgt1_PYTHONPATH
sudo bluebanquise-bootset -n mgt2 -b osdeploy
# temporary fix
sudo mkdir -p /var/www/html/preboot_execution_environment/
cd /var/www/html/preboot_execution_environment/
sudo rm -f convergence.ipxe
sudo ln -s ../pxe/convergence.ipxe convergence.ipxe
EOF

virsh destroy mgt2 && echo "mgt2 destroyed" || echo "mgt2 not found, skipping"
virsh undefine mgt2 && echo "mgt2 undefined" || echo "mgt2 not found, skipping"
virt-install --name=mgt2 --os-variant rhel8-unknown --ram=6000 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/mgt2.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=1a:2b:3c:4d:2e:8f --pxe
virsh setmem mgt2 2G --config
virsh start mgt2
fi

if (( $STEP < 12 )); then

# Validation step
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh-keygen -f "/var/lib/bluebanquise/.ssh/known_hosts" -R mgt2
/tmp/waitforssh.sh bluebanquise@mgt2
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt2 hostname
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt2 sudo curl http://bluebanquise.com/repository/releases/latest/el8/x86_64/bluebanquise/bluebanquise.repo --output /etc/yum.repos.d/bluebanquise.repo
EOF
set +e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
set -x
sleep 200 # wait for network to stabilize
#ssh -o StrictHostKeyChecking=no mgt2 'sudo dnf install wget -y && wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && sudo dnf install epel-release-latest-8.noarch.rpm -y && sudo dnf update -y && sudo dnf install git python39 python39-pip python3-policycoreutils openssh-clients -y && sudo alternatives --set python3 /usr/bin/python3.9 && sudo reboot -h now
ssh -o StrictHostKeyChecking=no mgt2 'sudo dnf install wget -y && wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && sudo dnf install epel-release-latest-8.noarch.rpm -y && sudo dnf update -y && sudo dnf install git python3-policycoreutils openssh-clients -y && sudo reboot -h now
'
EOF
set -e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
/tmp/waitforssh.sh bluebanquise@mgt2
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
source /var/lib/bluebanquise/ansible_venv/bin/activate
cd validation/inventories/
export ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.commons.core
export ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do
ansible-playbook ../playbooks/managements.yml -i minimal_extended --limit mgt2 -b
EOF
if [ $? -eq 0 ]; then
  echo SUCCESS deploying RHEL 8 on mgt2
else
  echo FAILED deploying RHEL 8 on mgt2
  exit 1
fi

# Cleaning
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo umount /var/www/html/pxe/netboots/redhat/8/x86_64/iso
rm AlmaLinux-8-latest-x86_64-dvd.iso
EOF
virsh shutdown mgt2

fi
