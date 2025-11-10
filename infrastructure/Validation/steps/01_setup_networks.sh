#!/bin/bash
# prepare infra
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if (( $STEP < 1 )); then
	set -x
    echo " 01 Setup networks."
    echo "  - Creating VMs private network."
    set +e
    virsh net-list --all | grep private_network
    if [ $? -ne 0 ]; then
        set -e
        virsh net-define $CURRENT_DIR/../vms/private_network.xml
	virsh net-start private_network
    fi
    set -e

fi
