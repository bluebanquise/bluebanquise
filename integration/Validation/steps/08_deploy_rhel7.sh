#!/bin/bash
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export mgt1_ip=$(virsh net-dhcp-leases default | grep '52:54:00:fa:12:01' | tail -1 | awk -F ' ' '{print $5}' | sed 's/\/24//')
# Prepare target deployment
mgt1_PYTHONPATH=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip pip3 show ClusterShell | grep Location | awk -F ' ' '{print $2}')

cd $CURRENT_DIR/../http
wget -nc http://centos.mirror.vexxhost.com/7.9.2009/isos/x86_64/CentOS-7-x86_64-Everything-2207-02.iso
cd $CURRENT_DIR

ssh -o StrictHostKeyChecking=no bluebanquise@$mgt1_ip wget -nc http://$host_ip:8000/CentOS-7-x86_64-Everything-2207-02.iso

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo mkdir -p /var/www/html/pxe/netboots/redhat/7/x86_64/iso
sudo mount /var/lib/bluebanquise/CentOS-7-x86_64-Everything-2207-02.iso /var/www/html/pxe/netboots/redhat/7/x86_64/iso
export PYTHONPATH=$mgt1_PYTHONPATH
sudo bluebanquise-bootset -n mgt4 -b osdeploy
# temporary fix
sudo mkdir -p /var/www/html/preboot_execution_environment/
cd /var/www/html/preboot_execution_environment/
sudo rm -f convergence.ipxe
sudo ln -s ../pxe/convergence.ipxe convergence.ipxe
EOF

virsh destroy mgt4 && echo "mgt4 destroyed" || echo "mgt4 not found, skipping"
virsh undefine mgt4 && echo "mgt4 undefined" || echo "mgt4 not found, skipping"

virt-install --name=mgt4 --os-variant rhel8-unknown --ram=6000 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/mgt4.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=1a:2b:3c:4d:4e:8f --pxe
virsh setmem mgt4 2G --config
virsh start mgt4

# Validation step
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh-keygen -f "/var/lib/bluebanquise/.ssh/known_hosts" -R mgt4
/tmp/waitforssh.sh bluebanquise@mgt4
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt4 hostname
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
ssh -o StrictHostKeyChecking=no mgt4 sudo curl http://bluebanquise.com/repository/releases/latest/el7/x86_64/bluebanquise/bluebanquise.repo --output /etc/yum.repos.d/bluebanquise.repo
EOF
set +e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
set -x
sleep 200 # wait for network to stabilize
ssh -o StrictHostKeyChecking=no mgt4 'sudo yum install wget -y && wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && sudo yum install epel-release-latest-7.noarch.rpm -y && sudo yum update -y && sudo reboot -h now'
EOF
set -e
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
/tmp/waitforssh.sh bluebanquise@mgt4
EOF
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
source /var/lib/bluebanquise/ansible_venv/bin/activate
cd validation/inventories/ 
export ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.commons.core
export ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do
ansible-playbook ../playbooks/managements.yml -i minimal_extended --limit mgt4 -b
EOF
if [ $? -eq 0 ]; then
  echo SUCCESS deploying RHEL 7 mgt4
else
  echo FAILED deploying RHEL 7 mgt4
  exit 1
fi

# Cleaning
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo umount /var/www/html/pxe/netboots/redhat/7/x86_64/iso
rm CentOS-7-x86_64-Everything-2207-02.iso
EOF
virsh shutdown mgt4
