#!/bin/bash
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if (( $STEP < 6 )); then

    remote_pubkey=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip /bin/echo \$\(cat /var/lib/bluebanquise/.ssh/id_ed25519.pub\))
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
set -x
cd validation/inventories/
mkdir -p minimal_extended/group_vars/all/
cp bb_core.yml minimal_extended/group_vars/all/
echo ep_admin_ssh_keys=[\"$remote_pubkey\"] >> minimal_extended/hosts
EOF

# Validation step
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bluebanquise@$mgt1_ip <<EOF
cd validation/inventories/ 
ansible-playbook ../playbooks/managements.yml -i minimal_extended --limit mgt1 -b
EOF
if [ $? -eq 0 ]; then
  echo SUCCESS deploying minimal extended on mgt1
else
  echo FAILED deploying minimal extended on mgt1
  exit 1
fi

fi

