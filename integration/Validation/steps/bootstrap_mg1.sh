#!/bin/bash
# prepare infra
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

export ubuntu_mg1_ip=$(virsh net-dhcp-leases default | grep '52:54:00:fa:1f:01' | awk -F ' ' '{print $5}' | sed 's/\/24//')

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$ubuntu_mg1_ip apt-get update
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$ubuntu_mg1_ip apt-get install wget -y


echo "Creating network"
virsh net-list --all | grep private_network > /dev/null
if [ $? -ne 0 ]; then
    set -e
    virsh net-define $CURRENT_DIR/../vms/private_network.xml
fi
set -e
if [ $(virsh net-list --all | grep private_network | awk -F ' ' '{print $2}') != 'active' ]; then
    virsh net-start private_network
fi
echo "Creating http server"
(
cd $CURRENT_DIR/../http
python3 -m http.server 8000
) &
http_server_pid=$!

echo "Installing system..."

virt-install --name=ubuntu_mg1 --ram=4096 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/ubuntu_mg1.qcow2,bus=virtio,size=6 --network bridge=virbr0,mac=52:54:00:fa:1f:01 --network bridge=virbr1,mac=52:54:00:fa:1f:02 --install kernel=http://192.168.122.1:8000/kernels/ubuntu_mg1/vmlinuz,initrd=http://192.168.122.1:8000/kernels/ubuntu_mg1/initrd,kernel_args_overwrite=yes,kernel_args="root=/dev/ram0 ramdisk_size=1500000 ip=dhcp url=http://192.168.122.1:8000/isos/ubuntu-20.04.2-live-server-amd64.iso autoinstall ds=nocloud-net;s=http://192.168.122.1:8000/autoinstall/ubuntu_mg1/ console=ttyS0,115200n8 serial" --graphics none --console pty,target_type=serial

echo "Killing http server"

#kill -9 $(ps -ax | grep 'http.server 8000' | sed -n 1p | awk -F ' ' '{print $1}')
kill -9 $http_server_pid
echo done
virsh start ubuntu_mg1

export ubuntu_mg1_ip=$(virsh net-dhcp-leases default | grep '52:54:00:fa:1f:01' | awk -F ' ' '{print $5}' | sed 's/\/24//')

echo "Waiting for VM to be ready at $ubuntu_mg1_ip"
set +e
$CURRENT_DIR/functions/waitforssh.sh $ubuntu_mg1_ip

