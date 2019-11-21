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
echo
echo " Detecting distribution..."
distribution=$(grep ^NAME /etc/os-release | awk -F '"' '{print $2}')
distribution_version=$(grep ^VERSION_ID /etc/os-release | awk -F '"' '{print $2}')
echo " Found $distribution $distribution_version"
working_directory=/root/bbbuilder
echo " Working directory: $working_directory"

set -x
echo "Cleaning"
#rm -Rf $working_directory/build
mkdir -p $working_directory/build
mkdir $working_directory/sources

echo " Installing needed packages... may take some time."
dnf install rpm-build genisoimage xz xz-devel automake autoconf python36 bzip2-devel openssl-devel zlib-devel readline-devel pam-devel perl-ExtUtils-MakeMaker grub2-tools-extra grub2-efi-x64-modules gcc -y


mkdir $working_directory/sources/bluebanquise
cd $working_directory/sources/bluebanquise
if [ ! -f $working_directory/sources/bluebanquise/README.md ]; then
  git clone https://github.com/oxedions/bluebanquise.git .
fi
git pull

# iPXE
mkdir $working_directory/sources/ipxe/
cd $working_directory/sources/ipxe/
if [ ! -f $working_directory/sources/ipxe/README.md ]; then
  git clone https://github.com/ipxe/ipxe.git .
fi
git pull
mkdir $working_directory/build/ipxe/
cd $working_directory/build/ipxe/
rm -Rf $working_directory/build/ipxe/*
cp -a $working_directory/sources/ipxe/* .
cp $working_directory/sources/bluebanquise/resources/packages/ipxe-bluebanquise-1.0.5/bluebanquise_standard.ipxe src/
cp $working_directory/sources/bluebanquise/resources/packages/ipxe-bluebanquise-1.0.5/bluebanquise_dhcpretry.ipxe src/
cp $working_directory/sources/bluebanquise/resources/packages/ipxe-bluebanquise-1.0.5/grub2-efi-autofind.cfg .
cp $working_directory/sources/bluebanquise/resources/packages/ipxe-bluebanquise-1.0.5/grub2-shell.cfg . 

grub2-mkstandalone -O x86_64-efi -o grub2-efi-autofind.img "boot/grub/grub.cfg=grub2-efi-autofind.cfg"
grub2-mkstandalone -O x86_64-efi -o grub2-shell.img "boot/grub/grub.cfg=grub2-shell.cfg"
cd src
sed -i 's/#undef\	DOWNLOAD_PROTO_HTTPS/#define\	DOWNLOAD_PROTO_HTTPS/g' config/general.h
sed -i 's/\/\/#define\	CONSOLE_FRAMEBUFFER/#define\  CONSOLE_FRAMEBUFFER/g' config/console.h
make -j 4 bin-x86_64-efi/ipxe.efi EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin/undionly.kpxe EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin-x86_64-efi/snponly.efi EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin-x86_64-efi/snp.efi EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin/ipxe.iso EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin/ipxe.usb EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb

mkdir $working_directory/build/ipxe/bin/x86_64/ -p

mv bin-x86_64-efi/ipxe.efi $working_directory/build/ipxe/bin/x86_64/standard_ipxe.efi
mv bin-x86_64-efi/snponly.efi $working_directory/build/ipxe/bin/x86_64/standard_snponly_ipxe.efi
mv bin-x86_64-efi/snp.efi $working_directory/build/ipxe/bin/x86_64/standard_snp_ipxe.efi
mv bin/undionly.kpxe $working_directory/build/ipxe/bin/x86_64/standard_undionly.kpxe
mv bin/ipxe.iso $working_directory/build/ipxe/bin/x86_64/standard_pcbios.iso
mv bin/ipxe.usb $working_directory/build/ipxe/bin/x86_64/standard_pcbios.usb
rm -Rf /dev/shm/efiiso/efi/boot
mkdir -p /dev/shm/efiiso/efi/boot
cp bin-x86_64-efi/ipxe.efi /dev/shm/efiiso/efi/boot/bootx64.efi
mkisofs -o standard_efi.iso -J -r /dev/shm/efiiso
cp standard_efi.iso $working_directory/build/ipxe/bin/x86_64/standard_efi.iso

# Doing dhcpretry
make -j 4 bin-x86_64-efi/ipxe.efi EMBED=bluebanquise_dhcpretry.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin/undionly.kpxe EMBED=bluebanquise_dhcpretry.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin-x86_64-efi/snponly.efi EMBED=bluebanquise_dhcpretry.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin-x86_64-efi/snp.efi EMBED=bluebanquise_dhcpretry.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin/ipxe.iso EMBED=bluebanquise_dhcpretry.ipxe DEBUG=intel,dhcp,vesafb
make -j 4 bin/ipxe.usb EMBED=bluebanquise_dhcpretry.ipxe DEBUG=intel,dhcp,vesafb

mv bin-x86_64-efi/ipxe.efi $working_directory/build/ipxe/bin/x86_64/dhcpretry_ipxe.efi
mv bin-x86_64-efi/snponly.efi $working_directory/build/ipxe/bin/x86_64/dhcpretry_snponly_ipxe.efi
mv bin-x86_64-efi/snp.efi $working_directory/build/ipxe/bin/x86_64/dhcpretry_snp_ipxe.efi
mv bin/undionly.kpxe $working_directory/build/ipxe/bin/x86_64/dhcpretry_undionly.kpxe
mv bin/ipxe.iso $working_directory/build/ipxe/bin/x86_64/dhcpretry_pcbios.iso
mv bin/ipxe.usb $working_directory/build/ipxe/bin/x86_64/dhcpretry_pcbios.usb
rm -Rf /dev/shm/efiiso/efi/boot
mkdir -p /dev/shm/efiiso/efi/boot
cp bin-x86_64-efi/ipxe.efi /dev/shm/efiiso/efi/boot/bootx64.efi
mkisofs -o dhcpretry_efi.iso -J -r /dev/shm/efiiso
cp dhcpretry_efi.iso $working_directory/build/ipxe/bin/x86_64/dhcpretry_efi.iso



exit

rpmbuild -ta --buildroot $working_directory/build $working_directory/sources/bluebanquise_ipxe-1.0.2.tar.gz

# Atftp
if [ ! -f $working_directory/sources/atftp-0.7.2.tar.gz ]; then
  wget -P $working_directory/sources/ https://freefr.dl.sourceforge.net/project/atftp/atftp-0.7.2.tar.gz 
fi
cd $working_directory/sources/
tar xvzf atftp-0.7.2.tar.gz
/usr/bin/cp -f $working_directory/sources/bluebanquise/resources/packages/atftp-0.7.2/* atftp-0.7.2/
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
