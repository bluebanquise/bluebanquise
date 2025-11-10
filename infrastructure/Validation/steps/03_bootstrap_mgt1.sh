#!/bin/bash

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo " 03 Bootstrap mgt1."

# Inject host ssh key into user-data
rm -f $CURRENT_DIR/../http/user-data
cp $CURRENT_DIR/../http/user-data.template $CURRENT_DIR/../http/user-data
echo "          - $(cat $HOME/.ssh/id_ed25519.pub)" >> $CURRENT_DIR/../http/user-data

sudo mkdir -p /data/images
CUSER=$USER
sudo chown -R $CUSER:$CUSER /data/images 
echo "  - Deploying base OS..."

virsh destroy mgt1 && echo "mgt1 destroyed" || echo "mgt1 not found, skipping"
virsh undefine mgt1 && echo "mgt1 undefined" || echo "mgt1 not found, skipping"

virt-install --os-variant ubuntu22.04 --name=mgt1 --ram=8192 --vcpus=4 --check mac_in_use=off --noreboot --disk path=/data/images/mgt1_2.qcow2,bus=virtio,size=24 --network bridge=virbr0,mac=52:54:00:fa:12:01 --network bridge=virbr1,mac=52:54:00:fa:12:02 --install kernel=http://$host_ip:8000/vmlinuz,initrd=http://$host_ip:8000/initrd,kernel_args_overwrite=yes,kernel_args="root=/dev/ram0 ramdisk_size=1500000 ip=dhcp url=http://$host_ip:8000/ubuntu-22.04.1-live-server-amd64.iso autoinstall ds=nocloud-net;s=http://$host_ip:8000/"

# Reduce memory once installed, no need for more
virsh setmem mgt1 2G --config

if (( $STEP < 4 )); then

    echo "  - Starting VM and wait 5s."
    virsh start mgt1

    echo "  - Getting mgt1 ip."
    sleep 30
    export mgt1_ip=$(virsh net-dhcp-leases default | grep '52:54:00:fa:12:01' | tail -1 | awk -F ' ' '{print $5}' | sed 's/\/24//')
    echo "  $mgt1_ip"

    ssh-keygen -f "$HOME/.ssh/known_hosts" -R $mgt1_ip

    echo "Waiting for VM to be ready at $mgt1_ip"
    set +e
    $CURRENT_DIR/functions/waitforssh.sh generic@$mgt1_ip
    set -e
    echo "  - Estabilishing link with mgt1."

   # sshpass -e ssh-copy-id -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null generic@$mgt1_ip
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null generic@$mgt1_ip sudo apt-get update
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null generic@$mgt1_ip DEBIAN_FRONTEND=noninteractive sudo apt-get upgrade -y

    echo "  - Configuring mgt1 as gateway."
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null generic@$mgt1_ip << EOF
sudo bash -c 'echo 1 > /proc/sys/net/ipv4/ip_forward'
sudo iptables -t nat -A POSTROUTING -s 10.10.0.0/16 -o enp1s0 -j MASQUERADE
EOF

    echo "  - Expand default FS."
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null generic@$mgt1_ip << EOF
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
EOF

    echo "  - Send waitssh."
    scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $CURRENT_DIR/functions/waitforssh.sh generic@$mgt1_ip:/tmp/waitforssh.sh

fi
