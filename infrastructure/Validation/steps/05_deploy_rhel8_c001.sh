#!/bin/bash
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo $CURRENT_DIR
cd $CURRENT_DIR/../http
wget -nc https://repo.almalinux.org/almalinux/8/isos/x86_64/AlmaLinux-8-latest-x86_64-dvd.iso
cd $CURRENT_DIR

if (( $STEP < 7 )); then
ssh -o StrictHostKeyChecking=no bluebanquise@$mgt1_ip wget -nc http://$host_ip:8000/AlmaLinux-8-latest-x86_64-dvd.iso

# Update configuration
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
cd validation/inventories/ 
ansible-playbook ../playbooks/managements.yml -i minimal --limit mgt1 -b
EOF

# Prepare target deployment
mgt1_PYTHONPATH=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip pip3 show ClusterShell | grep Location | awk -F ' ' '{print $2}')

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo mkdir -p /var/www/html/pxe/netboots/redhat/8/x86_64/iso
sudo mount /var/lib/bluebanquise/AlmaLinux-8-latest-x86_64-dvd.iso /var/www/html/pxe/netboots/redhat/8/x86_64/iso
export PYTHONPATH=$mgt1_PYTHONPATH
sudo bluebanquise-bootset -n c001 -b osdeploy
# temporary fix
sudo mkdir -p /var/www/html/preboot_execution_environment/
cd /var/www/html/preboot_execution_environment/
sudo rm -f convergence.ipxe
sudo ln -s ../pxe/convergence.ipxe convergence.ipxe
EOF

fi

if (( $STEP < 8 )); then
    virsh destroy c001
    virsh undefine c001
    virt-install --name=c001 --os-variant rhel8-unknown --ram=6000 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/c001.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=1a:2b:3c:4d:5e:9f --pxe
fi

# Validation step
if (( $STEP < 9 )); then
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
cd validation/inventories/ 
ansible-playbook ../playbooks/computes.yml -i minimal --limit c001 -b
EOF
if [ $RESULT -eq 0 ]; then
  echo SUCCESS deploying RHEL 8 c001
else
  echo FAILED deploying RHEL 8 c001
  exit 1
fi

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
sudo umount /var/www/html/pxe/netboots/redhat/8/x86_64/iso
rm AlmaLinux-8-latest-x86_64-dvd.iso
EOF

fi
