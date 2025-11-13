#!/bin/bash
# Force script to stop if any error
set -e

echo
echo "  __                 "
echo " '. \                "
echo "  '- \               "
echo "   / /_         .---."
echo "  / | \\,.\/--.//    )"
echo "  |  \//        )/  / "
echo "   \  ' ^ ^    /    )____.----..  6"
echo "    '.____.    .___/            \._) "
echo "       .\/.                      )"
echo "        '\                       /"
echo "        _/ \/    ).        )    ("
echo "       /#  .!    |        /\    /"
echo "       \  C// #  /'-----''/ #  / "
echo "    .   'C/ |    |    |   |    |mrf  ,"
echo "    \), .. .'OOO-'. ..'OOO'OOO-'. ..\(,"
echo
echo "  BlueBanquise packages builder"
echo "    2025 Benoit Leveugle"
echo
distribution=$2
distribution_version=$3
distribution_architecture=$(uname --m)
if [ "$distribution" == 'Ubuntu' ] && [ $distribution_architecture == 'aarch64' ]; then
distribution_architecture=arm64
fi
if [ "$distribution" == 'Debian' ] && [ $distribution_architecture == 'aarch64' ]; then
distribution_architecture=arm64
fi

if [ "$1" == 'shell' ]; then
  /bin/bash -l
  exit 0
fi

echo " Settings set to $distribution $distribution_version $distribution_architecture"

echo " Creating working directory..."
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
root_directory=$SCRIPT_DIR
working_directory=/tmp/wd/
cache_directory=/tmp/cache/
tags_directory=/tmp/tags/
echo " Working directory: $working_directory"
mkdir -p $working_directory
echo " root directory: $root_directory"

echo " Creating source directory..."
mkdir -p $working_directory/sources/

echo " Sourcing parameters."
source $root_directory/parameters.conf

if [ "$1" == "dependencies" ]; then
  set -x
  echo " Installing needed packages... may take some time."

  if [ "$distribution" == 'opensuse_leap' ]; then
    if [[ "$distribution_version" == "15" ]]; then
      zypper -n install dbus-1-devel gcc rpm-build make mkisofs xz xz-devel automake autoconf bzip2 openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2 grub2-x86_64-efi munge munge-devel freeipmi freeipmi-devel  mariadb mariadb-client libmariadb-devel libmariadb3 rpm-build tar wget python3 python3-setuptools unzip xorriso
      if [ $distribution_architecture == 'x86_64' ]; then
         zypper -n install grub2-x86_64-efi
      fi
      if [ $distribution_architecture == 'aarch64' ]; then
         zypper -n install grub2-arm64-efi
      fi
    fi
  elif [ "$distribution" == 'SLES' ]; then
    if [[ "$distribution_version" =~ ^12\. ]]; then
        # no munge RPMs!!
        zypper -n install gcc rpm-build make mkisofs xz xz-devel automake autoconf bzip2 openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2 grub2-x86_64-efi freeipmi freeipmi-devel libmysqlclient-devel mariadb mariadb-client rpm-build unzip xorriso
    elif [[ "$distribution_version" =~ ^15\. ]]; then
        zypper -n install dbus-1-devel gcc rpm-build make mkisofs xz xz-devel automake autoconf bzip2 openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2 grub2-x86_64-efi munge munge-devel freeipmi freeipmi-devel  mariadb mariadb-client libmariadb-devel libmariadb3 rpm-build unzip xorriso
    fi

  elif [ "$distribution" == 'Debian' ]; then
    if [ "$distribution_version" == "11" ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        echo "%_arch x86_64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-amd64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi xz-utils unzip xorriso
        # Possibly missing python3-mysqldb libmysqld-dev
        apt-get install libpmix-dev libpmix2 libpmix-bin equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
      if [ $distribution_architecture == 'arm64' ]; then
        echo "%_arch arm64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-arm64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi xz-utils unzip xorriso
        apt-get install libpmix-dev libpmix2 libpmix-bin equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
    fi
    if [ "$distribution_version" == "12" ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        echo "%_arch x86_64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-amd64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi xz-utils unzip xorriso
        # Possibly missing python3-mysqldb libmysqld-dev
        apt-get install libpmix-dev libpmix2 libpmix-bin equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
      if [ $distribution_architecture == 'arm64' ]; then
        echo "%_arch arm64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-arm64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi xz-utils unzip xorriso
        apt-get install libpmix-dev libpmix2 libpmix-bin equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
    fi
    if [ "$distribution_version" == "13" ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        echo "%_arch x86_64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-amd64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi xz-utils unzip xorriso
        # Possibly missing python3-mysqldb libmysqld-dev
        apt-get install libpmix-dev libpmix2 libpmix-bin equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
      if [ $distribution_architecture == 'arm64' ]; then
        echo "%_arch arm64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-arm64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi xz-utils unzip xorriso
        apt-get install libpmix-dev libpmix2 libpmix-bin equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
    fi

  elif [ "$distribution" == 'Ubuntu' ]; then
    if [ "$distribution_version" == "20.04" ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        echo "%_arch x86_64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-amd64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi unzip xorriso
        # Possibly missing python3-mysqldb libmysqld-dev
        apt-get install equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
      if [ $distribution_architecture == 'arm64' ]; then
        echo "%_arch arm64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-arm64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi unzip xorriso
        apt-get install equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
    fi
    if [ "$distribution_version" == "22.04" ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        echo "%_arch x86_64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-amd64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi unzip xorriso
        # Possibly missing python3-mysqldb libmysqld-dev
        apt-get install equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
      if [ $distribution_architecture == 'arm64' ]; then
        echo "%_arch arm64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-arm64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi unzip xorriso
        apt-get install equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
    fi
    if [ "$distribution_version" == "24.04" ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        echo "%_arch x86_64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-amd64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi unzip xorriso
        # Possibly missing python3-mysqldb libmysqld-dev
        apt-get install equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
      if [ $distribution_architecture == 'arm64' ]; then
        echo "%_arch arm64" > ~/.rpmmacros
        apt-get update
        export DEBIAN_FRONTEND=noninteractive
        apt-get install -y libdbus-1-dev python3-pip bison flex  liblzma-dev mkisofs rpm alien grub-efi-arm64 libpopt-dev libblkid-dev munge libmunge-dev libmunge2  libreadline-dev libextutils-makemaker-cpanfile-perl libpam0g-dev mariadb-common mariadb-server libmariadb-dev libmariadb-dev-compat zlib1g-dev libssl-dev python3-setuptools bc rsync build-essential git wget libfreeipmi-dev freeipmi-common freeipmi unzip xorriso
        apt-get install equivs build-essential fakeroot devscripts libmunge-dev libncurses-dev po-debconf python3 libgtk2.0-dev libpam0g-dev libperl-dev liblua5.3-dev libhwloc-dev dh-exec librrd-dev libipmimonitoring-dev hdf5-helpers libfreeipmi-dev libhdf5-dev man2html-base libcurl4-openssl-dev libpmix-dev libhttp-parser-dev libyaml-dev libjson-c-dev libjwt-dev liblz4-dev bash-completion libdbus-1-dev librdkafka-dev -y
      fi
    fi

  elif [ "$distribution" == 'RedHat' ]; then
    if [ $distribution_version -eq 8 ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        dnf install 'dnf-command(config-manager)' -y
        dnf install dnf-plugins-core -y
        # dnf install gcc-toolset-11* -y
        dnf install kernel-headers dbus-devel make rpm-build genisoimage xz xz-devel automake autoconf python36 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-x64-modules gcc mariadb mariadb-devel dnf-plugins-core curl-devel net-snmp-devel wget bc rsync xorriso unzip -y
        dnf config-manager --set-enabled powertools
        dnf install freeipmi-devel -y
        dnf groupinstall 'Development Tools' -y
      fi
      if [ $distribution_architecture == 'aarch64' ]; then
        dnf install 'dnf-command(config-manager)' -y
        dnf install dnf-plugins-core -y
        # dnf install gcc-toolset-11* -y
        dnf install kernel-headers make dbus-devel rpm-build genisoimage xz xz-devel automake autoconf python36 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-aa64-modules gcc mariadb mariadb-devel dnf-plugins-core curl-devel net-snmp-devel wget bc rsync xorriso unzip -y
        dnf config-manager --set-enabled powertools
        dnf install freeipmi-devel -y
        dnf groupinstall 'Development Tools' -y
      fi
    fi
    if [ $distribution_version -eq 9 ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        dnf install 'dnf-command(config-manager)' -y
        dnf install dnf-plugins-core epel-release -y
        dnf install kernel-headers make dbus-devel rpm-build genisoimage xz xz-devel automake autoconf python3 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-x64-modules gcc mariadb dnf-plugins-core curl-devel net-snmp-devel wget bc rsync xorriso procps-ng python3-setuptools curl-devel libgenders-devel net-snmp-devel unzip -y 
        dnf config-manager --set-enabled crb
        dnf install freeipmi-devel mariadb-devel -y
        dnf groupinstall 'Development Tools' -y
        dnf reinstall genisoimage -y
      fi
      if [ $distribution_architecture == 'aarch64' ]; then
        dnf install 'dnf-command(config-manager)' -y
        dnf install dnf-plugins-core epel-release -y
        dnf install kernel-headers make dbus-devel rpm-build genisoimage xz xz-devel automake autoconf python3 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-aa64-modules gcc mariadb dnf-plugins-core curl-devel net-snmp-devel wget bc rsync xorriso procps-ng python3-setuptools curl-devel libgenders-devel net-snmp-devel unzip -y
        dnf config-manager --set-enabled crb
        dnf install freeipmi-devel mariadb-devel -y
        dnf groupinstall 'Development Tools' -y
        dnf reinstall genisoimage -y
      fi
    fi
    if [ $distribution_version -eq 10 ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        dnf install 'dnf-command(config-manager)' -y
        dnf install subscription-manager -y
        dnf config-manager --set-enabled crb
        dnf install dnf-plugins-core epel-release -y
        dnf install kernel-headers make dbus-devel rpm-build xz xz-devel automake autoconf python3 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-x64-modules gcc mariadb dnf-plugins-core curl-devel net-snmp-devel wget bc rsync xorriso procps-ng python3-setuptools curl-devel net-snmp-devel unzip munge munge-devel munge-libs -y
        dnf install freeipmi-devel mariadb-devel -y
        dnf groupinstall 'Development Tools' -y
      fi
      if [ $distribution_architecture == 'aarch64' ]; then
        dnf install 'dnf-command(config-manager)' -y
        dnf install subscription-manager -y
        dnf config-manager --set-enabled crb
        dnf install dnf-plugins-core epel-release -y
        dnf install kernel-headers make dbus-devel rpm-build xz xz-devel automake autoconf python3 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-aa64-modules gcc mariadb dnf-plugins-core curl-devel net-snmp-devel wget bc rsync xorriso procps-ng python3-setuptools curl-devel net-snmp-devel unzip munge munge-devel munge-libs -y
        dnf install freeipmi-devel mariadb-devel -y
        dnf groupinstall 'Development Tools' -y
      fi
    fi
    if [ $distribution_version -eq 7 ]; then
      if [ $distribution_architecture == 'x86_64' ]; then
        yum install make rpm-build genisoimage xz xz-devel automake autoconf python36 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-x64-modules gcc mariadb mariadb-devel wget git gcc-c++ python-setuptools python3-setuptools net-snmp-devel curl-devel freeipmi-devel bc rsync xorriso flex bison unzip -y
        yum install centos-release-scl -y
        yum install devtoolset-7 -y
      fi
      if [ $distribution_architecture == 'aarch64' ]; then
        yum install make rpm-build genisoimage xz xz-devel automake autoconf python36 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-aa64-modules gcc mariadb mariadb-devel wget git gcc-c++ python-setuptools python3-setuptools net-snmp-devel curl-devel freeipmi-devel bc rsync xorriso flex bison unzip -y
        yum install centos-release-scl -y
        yum install devtoolset-7 -y
      fi
    fi

  fi
  set +x
  exit 0
fi

if [ "$1" == "documentation" ]; then

  set -x

  pip3 install sphinx sphinx_rtd_theme

  rm -Rf $working_directory/build/documentation
  mkdir -p $working_directory/build/documentation
  cd $working_directory/build/documentation
  git clone https://github.com/bluebanquise/bluebanquise.git .
  cd resources/documentation/
  make html
  tar cvJf documentation.tar.xz _build/html
  cp documentation.tar.xz $working_directory/../

  set +x
  exit 0
fi

# # Sepcial loads
# if [ "$distribution" == 'RedHat' ]; then
#   if [ $distribution_version -eq 8 ]; then
# source /opt/rh/gcc-toolset-11/enable
#   fi
# fi

# Crash if anything wrong happens
set -e
if [ -z ${1+x} ] || [ -z ${2+x} ] || [ -z ${3+x} ]; then
  echo "Missing arguments, exiting"
else
  source $root_directory/$1/build.sh
fi
exit 0
