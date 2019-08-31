set -x
echo "Cleaning"
rm -Rf build

yum install rpm-build genisoimage xz xz-devel automake autoconf python36 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker -y

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
wget https://github.com/SchedMD/slurm/archive/slurm-18-08-8-1.tar.gz
wget https://github.com/dun/munge/releases/download/munge-0.5.13/munge-0.5.13.tar.xz

rpmbuild -ta munge-0.5.13.tar.xz
tar xvzf slurm-18-08-8-1.tar.gz
mv slurm-slurm-18-08-8-1 slurm-18.08.8
tar cvjf slurm-18.08.8.tar.bz2 slurm-18.08.8
rpmbuild -ta slurm-18-08-8-1.tar.gz

# Prometheus
tar cvzf alertmanager-0.18.0.tar.gz ../alertmanager-0.18.0
rpmbuild -ta alertmanager-0.18.0.tar.gz
tar cvzf node_exporter-0.18.1.tar.gz ../node_exporter-0.18.1
rpmbuild -ta node_exporter-0.18.1.tar.gz
tar cvzf prometheus-2.11.1.tar.gz ../prometheus-2.11.1
rpmbuild -ta prometheus-2.11.1.tar.gz
