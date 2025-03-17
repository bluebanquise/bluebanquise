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
  if [[ "$arg" == *"--debug"* ]]; then
    set -x
  fi
done

echo -e "\e[34m"
echo ""
echo '
              (o_
    (o_  (o_  //\
    (/)_ (/)_ V_/_

    BlueBanquise bootstrap.
    v 3.2.0
    Benoit Leveugle <oxedions@gmail.com>
'
echo -e "\e[39m"

# Get current environment
echo
echo -n " Getting OS environment..."
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source /etc/os-release
echo -e " \e[31mOK\e[0m"

echo -n " Checking you are root..."
if [ "$EUID" -ne 0 ]; then
  echo -e " \e[31mPlease run this tool either as root or with a sudo-able user."
  echo -e " Fatal error, exiting.\e[0m"
  exit 1
fi

echo -e " \e[31mOK\e[0m"
echo

echo " Welcome to the BlueBanquise stack base bootstraper."
echo
echo -e " \e[31mThis tool is going to install packages and act as"
echo -e " priviledged user on this system to perform needed"
echo -e " operations to create the bluebanquise user."
echo -e " Commands executed are logged into /var/log/bluebanquise/bootstrap"
echo -e " This script is set to stop if anything returns an error."
echo -e " You can relaunch this script with the --debug flag to enable debug mode."
echo -e "\e[0m"

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

echo -n " Creating logs directory..."
mkdir -p /var/log/bluebanquise/
touch /var/log/bluebanquise/bootstrap
chown -R $USER: /var/log/bluebanquise/bootstrap
echo "Starting new bootstrap at $(date)" >> /var/log/bluebanquise/bootstrap 2>&1
echo -e " \e[31mOK\e[0m"

echo -n " Installing needed dependencies, could take some time..."
(
  set -x
  # UBUNTU
  if [ "$NAME" == "Ubuntu" ]; then
    if [ "$VERSION_ID" == "24.04" ]; then
      apt-get update
      DEBIAN_FRONTEND=noninteractive apt-get install python3 python3-pip python3-venv ssh curl git -y
    fi
    if [ "$VERSION_ID" == "22.04" ]; then
      apt-get update
      DEBIAN_FRONTEND=noninteractive apt-get install python3 python3-pip python3-venv ssh curl git -y
    fi
    if [ "$VERSION_ID" == "20.04" ]; then
      echo
      echo " INFO - Ubuntu 20.04 python3 is too old, building a recent python... This may take a while."
      echo
      apt-get update
      DEBIAN_FRONTEND=noninteractive apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev pkg-config ssh curl git -y
      wget https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tgz
      tar -xf Python-3.11.*.tgz
      cd Python-3.11.*/
      ./configure --enable-optimizations --with-ensurepip=install
      make -j
      make altinstall
      update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 3
      update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 3
      update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.11 3
      update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.11 3
      cd ../
      wget http://deb.debian.org/debian/pool/main/p/python-apt/python-apt_2.6.0.tar.xz
      tar xJvf python-apt_2.6.0.tar.xz
      cd python-apt-2.6.0/   
      apt build-dep ./ -y
      python setup.py build
      python setup.py build install
      cd ../
    fi
  fi
  # RHEL
  if [ "$VERSION_ID" == "7" ]; then
    # We need Python 3.8 minimum
    yum -y install epel-release openssh
    yum -y install centos-release-scl-rh centos-release-scl
    yum --enablerepo=centos-sclo-rh -y install rh-python38
    # Now we can 'scl enable rh-python38 bash' to trigger python3.8
  fi
  if [ "$PLATFORM_ID" == "platform:el8" ]; then
    dnf install git python39 python39-pip python3-policycoreutils openssh-clients -y
    alternatives --set python3 /usr/bin/python3.9
  fi
  if [ "$PLATFORM_ID" == "platform:el9" ]; then
    dnf install git python3 python3-pip python3-pip python3-policycoreutils openssh-clients -y
  fi
  # OPENSUSE LEAP
  if [ "$ID" == "opensuse-leap" ]; then
    zypper -n install python3 python3-pip
    zypper -n install python311 python311-pip git openssh curl
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 3
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 3
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3.11 3
    update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 3
    # ln -s /usr/bin/python3.9 /usr/bin/python3
    # ln -s /usr/bin/pip3.9 /usr/bin/pip3
  fi
  # DEBIAN
  if [ "$VERSION_ID" == "11" ] || [ "$VERSION_ID" == "12" ]; then
    apt update
    export DEBIAN_FRONTEND=noninteractive
    apt install -y python3 python3-pip python3-venv git ssh curl
  fi
  set +x
) >> /var/log/bluebanquise/bootstrap 2>&1
echo -e " \e[31mOK\e[0m"

echo -n " Creating bluebanquise user..."
(
  set -x
  getent group bluebanquise &>/dev/null || groupadd --gid 377 bluebanquise
  getent passwd bluebanquise &>/dev/null || useradd --gid 377 --uid 377 --create-home --home-dir /var/lib/bluebanquise --shell /bin/bash --system bluebanquise
  echo 'bluebanquise ALL=(ALL:ALL) NOPASSWD:ALL' | tee /etc/sudoers.d/bluebanquise
  set +x
) >> /var/log/bluebanquise/bootstrap 2>&1
echo -e " \e[31mOK\e[0m"

if [[ $SKIP_ENVIRONMENT == "false" ]]
then
echo -n " Setting bluebanquise user environment, this might take a while..."
(
  set -x
  sudo -u bluebanquise /bin/bash -c '
  cd /var/lib/bluebanquise
  git clone https://github.com/bluebanquise/bluebanquise.git
  cd bluebanquise
  cd bootstrap/
  chmod +x configure_environment.sh
  ./configure_environment.sh
  '
  set +x
) >> /var/log/bluebanquise/bootstrap 2>&1
echo -e " \e[31mOK\e[0m"
fi

echo -n " Setting rights on /var/log/bluebanquise/..."
(
chown -R bluebanquise:bluebanquise /var/log/bluebanquise/
) >> /var/log/bluebanquise/bootstrap 2>&1
echo -e " \e[31mOK\e[0m"

echo
echo " Bootstrap done."
echo " You can now login as bluebanquise user via 'su - bluebanquise'"
echo
echo " To use BlueBanquise, remember to set Ansible environment variable:"
echo " ANSIBLE_CONFIG=\$HOME/bluebanquise/ansible.cfg"
echo
echo " You can find documentation at http://bluebanquise.com/documentation/"
echo " You can ask for help or rise issues at https://github.com/bluebanquise/bluebanquise/"
echo
echo " Thank you for using BlueBanquise :)"
echo " Have fun!"
echo
