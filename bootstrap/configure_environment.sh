#!/usr/bin/env bash
set -e

# Get parameters if any

export COLLECTIONS_LOCAL_PATH="none"

for arg in "$@"; do
  if [[ "$arg" == *"--bb_collections_local_path="* ]]; then
    export COLLECTIONS_LOCAL_PATH=$(echo $arg | awk -F '=' '{print $2}')
  fi
done

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source /etc/os-release

# Install minimal requirements into a virtual environment
cd $HOME
if [ "$PLATFORM_ID" == "platform:el7" ]; then
  export LANG=en_US.UTF-8
  export LC_ALL=en_US.UTF-8
fi
python3 -m venv ansible_venv
source ansible_venv/bin/activate

python3 -m pip install --upgrade pip && \
pip3 install setuptools setuptools_rust && \
pip3 install -r $CURRENT_DIR/requirements.txt

echo "Trying 3 times to grab community.general..."
ansible-galaxy collection install community.general || ansible-galaxy collection install community.general || ansible-galaxy collection install community.general
# Install BlueBanquise collections
if [[ $COLLECTIONS_LOCAL_PATH != "none" ]]; then
  ansible-galaxy collection install $COLLECTIONS_LOCAL_PATH
else
  ansible-galaxy collection install git+https://github.com/bluebanquise/bluebanquise.git#/collections/infrastructure,master -vvv --upgrade
fi

deactivate

# Set pip bins in PATH
grep -q -E "^export PATH.*/\.local/bin" "${HOME}"/.bashrc ||\
echo "export PATH=\$HOME/.local/bin:\$PATH" |\
tee -a "${HOME}"/.bashrc

# Expand PYTHONPATH, need to make it dynamic
grep -q PYTHONPATH "${HOME}"/.bashrc ||\
echo "export PYTHONPATH=\$(pip3 show ClusterShell | grep Location | awk -F ' ' '{print \$2}')" >> "${HOME}"/.bashrc

# Bind to bluebanquise default ansible.cfg
mkdir -p $HOME/bluebanquise/
echo "export ANSIBLE_CONFIG=\$HOME/bluebanquise/ansible.cfg" |
tee -a "${HOME}"/.bashrc

# Ensure PYTHPATH is preserved while sudo
sudo grep -q PYTHONPATH /etc/sudoers ||\
echo 'Defaults env_keep += "PYTHONPATH"' |\
sudo EDITOR='tee -a' visudo

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

