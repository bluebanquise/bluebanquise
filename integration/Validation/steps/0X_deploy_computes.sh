if (( $STEP < 8 )); then
    virt-install --name=c001 --os-variant rhel8-unknown --ram=6000 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/c001.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=1a:2b:3c:4d:5e:8f --pxe
#    virt-install --name=c002 --ram=4096 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/c002.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=08:00:27:0d:44:92 --pxe
#    virt-install --name=c003 --ram=4096 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/c003.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=08:00:27:0d:44:93 --pxe
#    virt-install --name=c004 --ram=4096 --vcpus=4 --noreboot --disk path=/var/lib/libvirt/images/c004.qcow2,bus=virtio,size=10 --network bridge=virbr1,mac=08:00:27:0d:44:94 --pxe
fi
