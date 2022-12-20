#!/usr/bin/env bash
pip3 install -r requirements.txt
export PATH=$HOME/.local/bin:$PATH
ansible-galaxy collection install community.general

# Set pip bins in PATH
grep -q -E "^export PATH.*/\.local/bin" "${HOME}"/.bashrc ||\
echo "export PATH=\$HOME/.local/bin:\$PATH" |\
tee -a "${HOME}"/.bashrc

# Expand PYTHONPATH, need to make it dynamic
grep -q PYTHONPATH "${HOME}"/.bashrc ||\
echo "export PYTHONPATH=\$(pip3 show ClusterShell | grep Location | awk -F ' ' '{print \$2}')" >> "${HOME}"/.bashrc

# Bind to bluebanquise default ansible.cfg
echo "export ANSIBLE_CONFIG=\$HOME/bluebanquise/ansible.cfg" |
tee -a "${HOME}"/.bashrc

# Ensure PYTHPATH is preserved while sudo
sudo grep -q PYTHONPATH /etc/sudoers ||\
echo 'Defaults env_keep += "PYTHONPATH"' |\
sudo EDITOR='tee -a' visudo

mkdir $HOME/.ssh
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

