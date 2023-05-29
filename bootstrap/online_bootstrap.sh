#!/usr/bin/env bash
set -e

export SILENT="false"
export SKIP_ENVIRONMENT="false"

for arg in "$@"; do
  if [[ "$arg" == *"--silent"* ]]; then
    export SILENT="true"
  fi
  if [[ "$arg" == *"--skip_environment"* ]]; then
    export SKIP_ENVIRONMENT="true"
  fi
done

function message_output () {
  echo -e "\e[34m"
  echo -e " ╔═══════════════════════════════════════════════════════════════╗"
  echo -e " ║ $1"
  echo -e " ╚═════════════════════\e[39m"
}

echo -e "\e[34m"
echo -e " ╔═══════════════════════════════════════════════════════════════╗"
echo -e " ║ BlueBanquise bootstrap.                                       ║"
echo -e " ║ v 2.0.0                                                       ║"
echo -e " ╚═══════════════════════════════════════════════════════════════╝\e[39m"

# Get current environment
echo
echo " Getting environment..."
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source /etc/os-release

echo " Welcome in the BlueBanquise stack base bootstraper."
echo
echo -e " \e[31mThis tool is going to install packages and act as"
echo -e " priviledged user on this system to perform needed"
echo -e " operations.\e[0m"
echo
if [[ $SILENT == "false" ]]
then
  read -p " Please confirm you agree with that (Y/N): " -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
    echo " Exiting tool."
    exit 0
  fi
fi
echo " Proceeding..."
sleep 1
echo
message_output "Installing OS needed dependencies..."
if [ "$NAME" == "Ubuntu" ]; then
  if [ "$VERSION_ID" == "20.04" ] || [ "$VERSION_ID" == "22.04" ]; then
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update
    sudo apt-get install python3 python3-pip python3-venv ssh curl git -y
  fi
fi
if [ "$VERSION_ID" == "7" ]; then
  # We need Python 3.8 minimum
  sudo yum -y install epel-release openssh
  sudo yum -y install centos-release-scl-rh centos-release-scl
  sudo yum --enablerepo=centos-sclo-rh -y install rh-python38
  # Now we can 'scl enable rh-python38 bash' to trigger python3.8
fi
if [ "$PLATFORM_ID" == "platform:el8" ]; then
  sudo dnf install git python39 python39-pip python3-policycoreutils openssh-clients -y
  sudo alternatives --set python3 /usr/bin/python3.9
fi
if [ "$PLATFORM_ID" == "platform:el9" ]; then
  sudo dnf install git python3 python3-pip python3-pip python3-policycoreutils openssh-clients -y
fi
if [ "$ID" == "opensuse-leap" ]; then
  sudo zypper -n install python3 python3-pip
  sudo zypper -n install python39 python39-pip git openssh
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 3
  sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 3
  sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3.9 3
  sudo update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.9 3
  # sudo ln -s /usr/bin/python3.9 /usr/bin/python3
  # sudo ln -s /usr/bin/pip3.9 /usr/bin/pip3
fi
if [ "$VERSION_ID" == "11" ]; then
  sudo apt update
  export DEBIAN_FRONTEND=noninteractive
  sudo apt install -y python3 python3-pip python3-venv git ssh curl
fi

message_output "Creating bluebanquise user, may take a while..."
id -u bluebanquise &>/dev/null || sudo useradd --create-home --home-dir /var/lib/bluebanquise --shell /bin/bash bluebanquise
echo 'bluebanquise ALL=(ALL:ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/bluebanquise

if [[ $SKIP_ENVIRONMENT == "false" ]]
then
sudo -u bluebanquise /bin/bash -c '
cd /var/lib/bluebanquise
git clone https://github.com/bluebanquise/bluebanquise.git
cd bluebanquise
cd bootstrap/
chmod +x configure_environment.sh
./configure_environment.sh
'
fi

echo
echo " Bootstrap done."
echo " You can now login as bluebanquise user via 'sudo su - bluebanquise'"
echo
echo " To use BlueBanquise, remember to set Ansible environment variable:"
echo " ANSIBLE_CONFIG=$HOME/bluebanquise/ansible.cfg"
echo
echo " You can find documentation at http://bluebanquise.com/documentation/"
echo " You can ask for help or rise issues at https://github.com/bluebanquise/bluebanquise/"
echo
echo " Thank you for using BlueBanquise."
echo
