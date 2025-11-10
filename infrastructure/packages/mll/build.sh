set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
#source $CURRENT_DIR/version.sh

rm -Rf $working_directory/build/MLL
mkdir -p $working_directory/build/MLL
cd $working_directory/build/MLL
git clone https://github.com/ivandavidov/minimal.git .
cd src
sed -i 's/^OVERLAY_BUNDLES.*$/OVERLAY_BUNDLES=dhcp,dropbear,coreutils,static_get,util_linux/' .config
sed -i 's/^NCURSES_SOURCE_URL.*$/NCURSES_SOURCE_URL=https:\/\/ftp.gnu.org\/pub\/gnu\/ncurses\/ncurses-5.9.tar.gz/' minimal_overlay/bundles/ncurses/.config
sed -i 's/^cd\ \$DEST_DIR\/usr\/lib/cd\ \$DEST_DIR\/usr\/lib64/' minimal_overlay/bundles/ncurses/02_build.sh
export FORCE_UNSAFE_CONFIGURE=1
./build_minimal_linux_live.sh
kernelversion=$(ls -l source/ | grep -i '\ linux-' | awk -F 'linux-' '{print $2}' | awk -F '.tar.xz' '{print $1}')
cd $working_directory/build/MLL/
mkdir mll-$kernelversion
isoinfo -i $working_directory/build/MLL/src/minimal_linux_live.iso -x '/boot/rootfs.xz;1' > mll-$kernelversion/rootfs.xz
isoinfo -i $working_directory/build/MLL/src/minimal_linux_live.iso -x '/boot/kernel.xz;1' > mll-$kernelversion/kernel.xz
cp -a $root_directory/mll mll-$kernelversion/
tar cvzf mll-$kernelversion.tar.gz mll-$kernelversion
rpmbuild -ta mll-$kernelversion.tar.gz --define "_software_version $kernelversion" --define "_architecture $(uname -m)"

if [ $distribution == "Ubuntu" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/x86_64/mll-*
    mkdir -p /root/debbuild/DEBS/noarch/
    mv *.deb /root/debbuild/DEBS/noarch/
fi

set +x
