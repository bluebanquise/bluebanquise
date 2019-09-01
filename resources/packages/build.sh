set -x
echo "Cleaning"
rm -Rf build

yum install rpm-build genisoimage xz xz-devel automake autoconf python36 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-x64-modules gcc -y

mkdir build
cd build

# iPXE
#tar cvzf bluebanquise_ipxe-1.0.1.tar.gz ../bluebanquise_ipxe-1.0.1
#rpmbuild -ta bluebanquise_ipxe-1.0.1.tar.gz

# Atftp
#wget https://freefr.dl.sourceforge.net/project/atftp/atftp-0.7.2.tar.gz
#tar xvzf atftp-0.7.2.tar.gz
#/usr/bin/cp -f ../atftp-0.7.2/* atftp-0.7.2/
#rm -f atftp-0.7.2/redhat/atftp.spec
#tar cvzf atftp-0.7.2.tar.gz atftp-0.7.2
#rpmbuild -ta atftp-0.7.2.tar.gz

# Slurm
#wget https://github.com/SchedMD/slurm/archive/slurm-18-08-8-1.tar.gz
#wget https://github.com/dun/munge/releases/download/munge-0.5.13/munge-0.5.13.tar.xz

#rpmbuild -ta munge-0.5.13.tar.xz
#tar xvzf slurm-18-08-8-1.tar.gz
#mv slurm-slurm-18-08-8-1 slurm-18.08.8
#tar cvjf slurm-18.08.8.tar.bz2 slurm-18.08.8
#rpmbuild -ta slurm-18-08-8-1.tar.gz

# Prometheus
#tar cvzf alertmanager-0.18.0.tar.gz ../alertmanager-0.18.0
#rpmbuild -ta alertmanager-0.18.0.tar.gz
#tar cvzf node_exporter-0.18.1.tar.gz ../node_exporter-0.18.1
#rpmbuild -ta node_exporter-0.18.1.tar.gz
#tar cvzf prometheus-2.11.1.tar.gz ../prometheus-2.11.1
#rpmbuild -ta prometheus-2.11.1.tar.gz

# Report
wget https://github.com/fboender/ansible-cmdb/releases/download/1.30/ansible-cmdb-1.30.tar.gz
wget https://github.com/willthames/ansible-inventory-grapher/archive/v2.4.5.tar.gz
wget https://github.com/haidaraM/ansible-playbook-grapher/archive/v0.9.1.tar.gz

tar xvzf ansible-cmdb-1.30.tar.gz
/usr/bin/cp -af ../ansible-cmdb-1.30/* ansible-cmdb-1.30
tar cvzf ansible-cmdb-1.30.tar.gz ansible-cmdb-1.30
rpmbuild -ta ansible-cmdb-1.30.tar.gz

tar xvzf v2.4.5.tar.gz
/usr/bin/cp -af ../ansible-inventory-grapher-2.4.5/* ansible-inventory-grapher-2.4.5
tar cvzf ansible-inventory-grapher-2.4.5.tar.gz ansible-inventory-grapher-2.4.5
rpmbuild -ta ansible-inventory-grapher-2.4.5.tar.gz

tar xvzf v0.9.1.tar.gz
/usr/bin/cp -af ../ansible-playbook-grapher-0.9.1/* ansible-playbook-grapher-0.9.1
tar cvzf ansible-playbook-grapher-0.9.1.tar.gz ansible-playbook-grapher-0.9.1
rpmbuild -ta ansible-playbook-grapher-0.9.1.tar.gz
