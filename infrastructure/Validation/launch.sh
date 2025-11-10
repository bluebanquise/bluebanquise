echo
LAUNCH_CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
#sudo apt-get update && sudo apt-get install -y qemu-kvm virt-manager libvirt-daemon-system virtinst libvirt-clients bridge-utils
#sudo systemctl enable libvirtd
#sudo systemctl start libvirtd
#sudo usermod -aG kvm $USER
#sudo usermod -aG libvirt $USER
#newgrp kvm
#newgrp libvirt
#trap "kill -9 $(ps -ax | grep 'http.server 8000' | sed 2d | awk -F ' ' '{print $1}')" EXIT
echo "Starting test."
set -e
source values.sh
if (( $STEP < 1 )); then
    source steps/01_setup_networks.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 2 )); then
    source steps/02_start_http_server.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 3 )); then
    source steps/03_bootstrap_mgt1.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 9 )); then
    source steps/04_deploy_bluebanquise_on_mgt1.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 20 )); then
    source steps/06_deploy_rhel8.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 30 )); then
    source steps/07_deploy_rhel9.sh
fi
cd $LAUNCH_CURRENT_DIR
#if (( $STEP < 40 )); then
#    source steps/08_deploy_rhel7.sh
#fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 50 )); then
    source steps/09_deploy_ubuntu20.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 60 )); then
    source steps/10_deploy_ubuntu22.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 70 )); then
    source steps/11_deploy_osl13.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 80 )); then
    # Note: if this part fails when grabing repos, clean netboot and kernels everywhere, and relaunch
    source steps/12_deploy_debian11.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 90 )); then
    source steps/13_deploy_debian12.sh
fi
cd $LAUNCH_CURRENT_DIR
if (( $STEP < 100 )); then
    source steps/14_deploy_ubuntu24.sh
fi

