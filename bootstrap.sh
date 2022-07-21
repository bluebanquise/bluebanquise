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

#CURRENT_DIR=$(dirname "$(realpath "${0}")")
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source $CURRENT_DIR/bootstrap_input.sh
source /etc/os-release

if $GATHER_PACKAGES; then
  message_output "Gathering packages and images repositories, may take a while..."
  sudo mkdir -p /var/www/html/
  sudo chown -R bluebanquise:bluebanquise /var/www/html/
  if [ "$NAME" == "Ubuntu" ]; then
    if [ "$VERSION_ID" == "20.04" ]; then
      if $GATHER_PACKAGES_UBUNTU_2004; then
        REPO_PATH="/var/www/html/repositories/ubuntu/20.04/x86_64/"
        if [[ -d "${REPO_PATH}"/bluebanquise ]]; then
          message_output "BlueBanquise folder already exist, skipping packages."
        else
          if $OFFLINE_MODE; then
            cp -a "${CURRENT_DIR}/offline_bootstrap/repositories/bluebanquise"\
                  "${REPO_PATH}"
          else
            wget -P "${REPO_PATH}"\
                 -np\
                 -nH\
                 --cut-dirs 5\
                 -r\
                 --reject "index.html*"\
                 http://bluebanquise.com/repository/releases/latest/ubuntu2004/x86_64/bluebanquise/
          fi
        fi
        if [[ -d "${REPO_PATH}"/os ]]; then
          message_output "Os folder already exist, skipping iso."
        else
          if $OFFLINE_MODE; then
            cp -a\
              "$CURRENT_DIR/offline_bootstrap/repositories/iso/$UBUNTU_2004_ISO"\
              "${REPO_PATH}"
          else
            wget -P "${REPO_PATH}"\
                 "${UBUNTU_2004_ISO_URL}"
          fi
          mountpoint -q /mnt
          if [ $? -eq 0 ]; then
            sudo umount /mnt
          fi
          sudo mount /var/www/html/repositories/ubuntu/20.04/x86_64/$UBUNTU_2004_ISO /mnt
          mkdir -p /var/www/html/repositories/ubuntu/20.04/x86_64/os/
          cp -a /mnt/* /var/www/html/repositories/ubuntu/20.04/x86_64/os/
          sudo umount /mnt
          ln -s "${UBUNTU_2004_ISO}" ubuntu-20.04-live-server-amd64.iso
        fi
      fi
    fi
  fi
  if [ "$PLATFORM_ID" == "platform:el8" ]; then
    if $GATHER_PACKAGES_REDHAT_8; then
      REPO_PATH="/var/www/html/repositories/redhat/8/x86_64/"
      mkdir -p "${REPO_PATH}"
      if [[ -d bluebanquise ]]; then
        message_output "BlueBanquise folder already exist, skipping packages download."
      else
        if $OFFLINE_MODE; then
          cp -a "$CURRENT_DIR/offline_bootstrap/repositories/bluebanquise"\
            "${REPO_PATH}"
        else
          wget -P "${REPO_PATH}"\
               -np\
               -nH\
               --cut-dirs 5\
               -r\
               --reject "index.html*"\
               http://bluebanquise.com/repository/releases/latest/el8/x86_64/bluebanquise/
        fi
      fi
      if [[ -d os ]]; then
        message_output "Os folder already exist, skipping iso download."
      else
        if $OFFLINE_MODE; then
          cp -a "$CURRENT_DIR/offline_bootstrap/iso/$REDHAT_8_ISO"\
          "${REPO_PATH}"
        else
          wget -P "{REPO_PATH}" "${REDHAT_8_ISO_URL}"
        fi
        mountpoint -q /mnt
        if [ $? -eq 0 ]; then
          sudo umount /mnt
        fi
        sudo mount /var/www/html/repositories/redhat/8/x86_64/$REDHAT_8_ISO /mnt
        mkdir -p /var/www/html/repositories/redhat/8/x86_64/os/
        cp -a /mnt/* /var/www/html/repositories/redhat/8/x86_64/os/
        sudo umount /mnt
      fi
      restorecon -Rv /var/www/html/
    fi
  fi
fi

cd "${CURRENT_DIR}"

if [ "$PLATFORM_ID" == "platform:el8" ]; then
  if $OFFLINE_MODE; then
    message_output "Configuring offline repositories..."
cat << EOF | sudo tee -a /etc/yum.repos.d/bootstrap.repo
[BaseOS]
name=BaseOS
baseurl=file:///var/www/html/repositories/redhat/8/x86_64/os/BaseOS/
gpgcheck=0
enabled=1

[AppStream]
name=AppStream
baseurl=file:///var/www/html/repositories/redhat/8/x86_64/os/AppStream/
gpgcheck=0
enabled=1
EOF
  fi
fi

if $INSTALL_SYSTEM_REQUIREMENTS; then
  message_output "Installing OS needed dependencies..."
  if [ "$NAME" == "Ubuntu" ]; then
    if [ "$VERSION_ID" == "20.04" ]; then
      sudo apt-get install python3-pip
    fi
  fi
  if [ "$PLATFORM_ID" == "platform:el8" ]; then
    sudo dnf install python3 python3-pip python3-policycoreutils openssh-clients -y
  fi
fi

if $INSTALL_PIP_REQUIREMENTS; then
  message_output "Installing python needed dependencies via pip3..."
  if $OFFLINE_MODE; then
    sudo pip3 install --upgrade pip --no-index --find-links "${CURRENT_DIR}/offline_bootstrap/pip3/"
    pip3 install --no-index\
                 --find-links "${CURRENT_DIR}/offline_bootstrap/pip3/"\
                 -r requirements.txt
  else
    sudo pip3 install --upgrade pip
    pip3 install -r requirements.txt
  fi
fi

export PATH=$HOME/.local/bin:$PATH

if $INSTALL_GALAXY_REQUIREMENTS; then
  message_output "Installing Ansible needed collections..."
  if $OFFLINE_MODE; then
    cd "$CURRENT_DIR/offline_bootstrap/collections/collections/"
    ansible-galaxy collection install -r requirements.yml
  else
    ansible-galaxy collection install community.general
  fi
fi

cd "${CURRENT_DIR}"

message_output "Copying sample inventory and playbooks."
if [[ -d inventory ]]; then
  message_output "Inventory folder already exist, skipping copy."
else
  cp -a resources/examples/$SAMPLE_INVENTORY/inventory .
fi
if [[ -d playbooks ]]; then
  message_output "Playbooks folder already exist, skipping copy."
else
  cp -a resources/examples/$SAMPLE_INVENTORY/playbooks .
fi

message_output "Setting system variables into .bashrc and sudoers..."
grep -q -E "^export PATH.*/\.local/bin" "${HOME}"/.bashrc ||\
echo "export PATH=\$HOME/.local/bin:\$PATH" |\
tee -a "${HOME}"/.bashrc

grep -q PYTHONPATH "${HOME}"/.bashrc ||\
echo "export PYTHONPATH=\$(pip3 show ClusterShell | grep Location | awk -F ' ' '{print \$2}')" >> "${HOME}"/.bashrc

echo "export ANSIBLE_CONFIG=\$HOME/bluebanquise/ansible.cfg" |
tee -a "${HOME}"/.bashrc
sudo grep -q PYTHONPATH /etc/sudoers ||\
echo 'Defaults env_keep += "PYTHONPATH"' |\
sudo EDITOR='tee -a' visudo

message_output "Generating ssh keys..."
mkdir -p $HOME/.ssh
# Create SSH key pair if id_ed25519 doesn't exist
if [[ ! -f "${HOME}/.ssh/id_ed25519" ]]; then
  ssh-keygen -t ed25519\
    -f "${HOME}"/.ssh/id_ed25519\
    -q\
    -N ""
fi

# Add id_ed25519 public key to authorized keys
if [[ ! -f "${HOME}/.ssh/authorized_keys" ]]; then
  cp "${HOME}/.ssh/id_ed25519.pub"\
    "${HOME}/.ssh/authorized_keys"
else
  if ! grep -q -f "${HOME}/.ssh/id_ed25519.pub"\
       "${HOME}/.ssh/authorized_keys";
then
    tee -a "${HOME}/.ssh/authorized_keys" > /dev/null\
    < "${HOME}/.ssh/id_ed25519.pub"
  fi
fi

cd "${CURRENT_DIR}"

sed -i '/ssh-rsa/d' inventory/group_vars/all/equipment_all/authentication.yml
sed -i '/ssh-ed25519/d' inventory/group_vars/all/equipment_all/authentication.yml
echo "  - $(cat "${HOME}"/.ssh/id_ed25519.pub)" |\
tee -a inventory/group_vars/all/equipment_all/authentication.yml

message_output "Setting first connection..."
grep -q mgt1 /etc/hosts ||\
echo "127.0.0.1 mgt1" |\
sudo tee -a /etc/hosts

if $ESTABLISH_FIRST_SSH; then
ssh -o StrictHostKeyChecking=no mgt1 echo Ok
fi

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

