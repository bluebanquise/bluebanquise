#!/bin/bash
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export mgt1_ip=$(virsh net-dhcp-leases default | grep '52:54:00:fa:12:01' | tail -1 | awk -F ' ' '{print $5}' | sed 's/\/24//')
# Prepare target deployment
mgt1_PYTHONPATH=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip pip3 show ClusterShell | grep Location | awk -F ' ' '{print $2}')

cd $CURRENT_DIR/../http
wget -nc https://releases.ubuntu.com/focal/ubuntu-20.04.5-live-server-amd64.iso
cd $CURRENT_DIR

ssh -o StrictHostKeyChecking=no bluebanquise@$mgt1_ip wget -nc http://$host_ip:8000/ubuntu-20.04.5-live-server-amd64.iso

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo mkdir -p /var/www/html/pxe/netboots/ubuntu/20.04/x86_64/iso
sudo mv /var/lib/bluebanquise/ubuntu-20.04.5-live-server-amd64.iso /var/www/html/pxe/netboots/ubuntu/20.04/x86_64/ubuntu-20.04-live-server-amd64.iso
sudo mount /var/www/html/pxe/netboots/ubuntu/20.04/x86_64/ubuntu-20.04-live-server-amd64.iso /var/www/html/pxe/netboots/ubuntu/20.04/x86_64/iso
export PYTHONPATH=$mgt1_PYTHONPATH
sudo bluebanquise-bootset -n mgt5 -b osdeploy
# temporary fix
sudo mkdir -p /var/www/html/preboot_execution_environment/
cd /var/www/html/preboot_execution_environment/
sudo rm -f convergence.ipxe
sudo ln -s ../pxe/convergence.ipxe convergence.ipxe
EOF

virsh destroy mgt5 && echo "mgt5 destroyed" || echo "mgt5 not found, skipping"
virsh undefine mgt5 && echo "mgt5 undefined" || echo "mgt5 not found, skipping"

virt-install --name=mgt5 --os-variant ubuntu20.04 --ram=6000 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/mgt5.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=1a:2b:3c:4d:5e:8f --pxe
virsh setmem mgt5 2G --config
virsh start mgt5

# Validation step
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh-keygen -f "/var/lib/bluebanquise/.ssh/known_hosts" -R mgt5
/tmp/waitforssh.sh bluebanquise@mgt5
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt5 hostname
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt5 sudo curl http://bluebanquise.com/repository/releases/latest/u20/x86_64/bluebanquise/bluebanquise.list --output /etc/apt/sources.list.d/bluebanquise.list
EOF
set +e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
set -x
sleep 200 # wait for network to stabilize
ssh -o StrictHostKeyChecking=no mgt5 'DEBIAN_FRONTEND=noninteractive sudo apt-get update && sudo apt-get upgrade -y && sudo reboot -h now'
EOF
set -e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
/tmp/waitforssh.sh bluebanquise@mgt5
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
source /var/lib/bluebanquise/ansible_venv/bin/activate
cd validation/inventories/ 
export ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.commons.core
export ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do
ansible-playbook ../playbooks/managements.yml -i minimal_extended --limit mgt5 -b
EOF
if [ $? -eq 0 ]; then
  echo SUCCESS deploying Ubuntu 20.04 mgt5
else
  echo FAILED deploying Ubuntu 20.04 mgt5
  exit 1
fi

# Cleaning
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo umount /var/www/html/pxe/netboots/ubuntu/20.04/x86_64/iso
sudo rm /var/www/html/pxe/netboots/ubuntu/20.04/x86_64/ubuntu-20.04-live-server-amd64.iso
EOF
virsh shutdown mgt5
