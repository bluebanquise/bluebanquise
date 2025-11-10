set -x
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh

package_path_calc

powerman_version=$package_version

if [ ! -f $package_path ]; then

    set -x
    if [ ! -f $working_directory/sources/powerman-$powerman_version.tar.gz ]; then
        wget -P $working_directory/sources/ https://github.com/chaos/powerman/releases/download/v$powerman_version/powerman-$powerman_version.tar.gz
    fi
    rm -Rf $working_directory/build/powerman
    mkdir -p $working_directory/build/powerman
    cd $working_directory/build/powerman
    cp $working_directory/sources/powerman-$powerman_version.tar.gz .
    tar xvzf powerman-$powerman_version.tar.gz
    sed -i '/TODO/d' powerman-$powerman_version/examples/powerman_el72.spec
    sed -i '/tcp_wrappers-devel/d' powerman-$powerman_version/examples/powerman_el72.spec
    sed -i 's/--with-tcp-wrappers/--without-tcp-wrappers/' powerman-$powerman_version/examples/powerman_el72.spec
    tar cvzf powerman.tar.gz powerman-$powerman_version
    rpmbuild -ta powerman.tar.gz --target=$distribution_architecture --define "_software_version $powerman_version"

    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        cd /root
        alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/powerman-*
        mkdir -p /root/debbuild/DEBS/$distribution_architecture/
        mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    fi

    # Build success, tag it
    touch $tags_directory/powerman-$distribution-$distribution_version-$powerman_version-$(uname -p)

fi

set +x

