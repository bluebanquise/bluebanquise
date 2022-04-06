#!/usr/bin/env bash
set -e

function message_output () {
  echo -e "\e[34m"
  echo -e " ╔══════════════════════════════════════════════╗"
  echo -e " ║ $1"
  echo -e " ╚══════════════════════════════════════════════╝\e[39m"
}

echo -e "\e[34m"
echo -e " ╔══════════════════════════════════════════════╗"
echo -e " ║ BlueBanquise bootstrap.                      ║"
echo -e " ║ v 1.0.0                                      ║"
echo -e " ╚══════════════════════════════════════════════╝\e[39m"

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source bootstrap_input.sh
source /etc/os-release

if $INSTALL_SYSTEM_REQUIREMENTS; then
  message_output "Installing OS needed dependencies..."
  if [ "$NAME" == "Ubuntu" ]; then
    if [ "$VERSION_ID" == "20.04" ]; then
      sudo apt-get install python3-pip
    fi
  fi
fi

if $INSTALL_PIP_REQUIREMENTS; then
  message_output "Installing python needed dependencies via pip3..."
  pip3 install -r requirements.txt
fi

export PATH=/home/bluebanquise/.local/bin:$PATH

if $INSTALL_GALAXY_REQUIREMENTS; then
  message_output "Installing Ansible needed collections..."
  ansible-galaxy collection install community.general
fi

message_output "Copying sample inventory and playbooks."
cp -a resources/examples/simple_cluster/inventory .
cp -a resources/examples/simple_cluster/playbooks .

if $GATHER_PACKAGES; then
  message_output "Gathering packages and images repositories, may take a while..."
  sudo mkdir -p /var/www/html/
  sudo chown -R bluebanquise:bluebanquise /var/www/html/
  if $GATHER_PACKAGES_UBUNTU_2004; then
    mkdir -p /var/www/html/repositories/ubuntu/20.04/x86_64/
    cd /var/www/html/repositories/ubuntu/20.04/x86_64/
    if [[ -d bluebanquise ]]; then
      message_output "BlueBanquise folder already exist, skipping packages download."
    else
      wget -np -nH --cut-dirs 5 -r --reject "index.html*" http://bluebanquise.com/repository/releases/latest/ubuntu2004/x86_64/bluebanquise/
    fi
    if [[ -d os ]]; then
      message_output "Os folder already exist, skipping iso download."
    else
      wget $UBUNTU_2004_ISO_URL
      sudo mount /var/www/html/repositories/ubuntu/20.04/x86_64/$UBUNTU_2004_ISO /mnt
      mkdir /var/www/html/repositories/ubuntu/20.04/x86_64/os/
      cp -a /mnt/* /var/www/html/repositories/ubuntu/20.04/x86_64/os/
      sudo umount /mnt
      ln -s $UBUNTU_2004_ISO ubuntu-20.04-live-server-amd64.iso
    fi
  fi
fi

message_output "Setting system variables into .bashrc and sudoers..."
cat $HOME/.bashrc | grep -q '.local/bin' || echo "export PATH=/home/bluebanquise/.local/bin:\$PATH" >> $HOME/.bashrc
cat $HOME/.bashrc | grep -q PYTHONPATH || echo "export PYTHONPATH=\$(pip3 show ClusterShell | grep Location | awk -F ' ' '{print \$2}')" >> $HOME/.bashrc
sudo cat /etc/sudoers | grep -q PYTHONPATH || echo 'Defaults env_keep += "PYTHONPATH"' | sudo EDITOR='tee -a' visudo

message_output "Generating ssh keys..."
ls $HOME/.ssh/ | grep -q id_ed25519 || ssh-keygen -t ed25519 -f $HOME/.ssh/id_ed25519 -q -N ""
cat $HOME/.ssh/authorized_keys | grep -q bluebanquise || cat $HOME/.ssh/id_ed25519.pub >> $HOME/.ssh/authorized_keys
cd $CURRENT_DIR
sed -i '/ssh-rsa/d' inventory/group_vars/all/equipment_all/authentication.yml
sed -i '/ssh-ed25519/d' inventory/group_vars/all/equipment_all/authentication.yml
echo "  - $(cat $HOME/.ssh/id_ed25519.pub)" >> inventory/group_vars/all/equipment_all/authentication.yml

message_output "Setting first connection..."
cat /etc/hosts | grep -q mgt1 || sudo echo 127.0.0.1 mgt1 >> /etc/hosts
ssh -o StrictHostKeyChecking=no mgt1 echo Ok

echo -e "\e[34m"
echo -e " ╔══════════════════════════════════════════════╗"
echo -e " ║ BlueBanquise bootstrap done."
echo -e " ║"
echo -e " ║ To use BlueBanquise, remember to set Ansible environment variable:"
echo -e " ║ ANSIBLE_CONFIG=$HOME/bluebanquise/ansible.cfg"
echo -e " ║"
echo -e " ║ You can find documentation at http://bluebanquise.com/documentation/"
echo -e " ║ You can ask for help or rise issues at https://github.com/bluebanquise/bluebanquise/"
echo -e " ║"
echo -e " ║ Thank you for using BlueBanquise."
echo -e " ║                                              ║"
echo -e " ╚══════════════════════════════════════════════╝\e[39m"

