set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh

package_path_calc

alpine_version=$package_version

if [ ! -f $package_path ]; then

    set -x
    if [ ! -f $working_directory/sources/alpine-netboot-$alpine_version-aarch64.tar.gz ]; then
        wget -P $working_directory/sources/ https://dl-cdn.alpinelinux.org/alpine/v$alpine_major_version/releases/aarch64/alpine-netboot-$alpine_version-aarch64.tar.gz
    fi
    if [ ! -f $working_directory/sources/alpine-netboot-$alpine_version-x86_64.tar.gz ]; then
        wget -P $working_directory/sources/ https://dl-cdn.alpinelinux.org/alpine/v$alpine_major_version/releases/x86_64/alpine-netboot-$alpine_version-x86_64.tar.gz
    fi
    rm -Rf $working_directory/build/alpine
    mkdir -p $working_directory/build/alpine
    cd $working_directory/build/alpine
    mkdir alpine-$alpine_version
    cp $working_directory/sources/alpine-netboot-$alpine_version-aarch64.tar.gz alpine-$alpine_version/alpine-netboot-aarch64.tar.gz
    cp $working_directory/sources/alpine-netboot-$alpine_version-x86_64.tar.gz alpine-$alpine_version/alpine-netboot-x86_64.tar.gz 
    $(which cp) -af $root_directory/alpine/* alpine-$alpine_version/
    sed -i "s/ALPINE_VERSION/$alpine_version/" alpine-$alpine_version/boot.ipxe
    sed -i "s/ALPINE_MAJOR_VERSION/$alpine_major_version/" alpine-$alpine_version/boot.ipxe
    tar cvzf alpine.tar.gz alpine-$alpine_version
    rpmbuild -ta alpine.tar.gz --target=noarch --define "_software_version $alpine_version"

    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        cd /root
        alien --to-deb --scripts /root/rpmbuild/RPMS/noarch/alpine-*
        mkdir -p /root/debbuild/DEBS/noarch/
        mv *.deb /root/debbuild/DEBS/noarch/
    fi

fi
