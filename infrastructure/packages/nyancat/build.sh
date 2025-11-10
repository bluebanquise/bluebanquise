set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh

package_path_calc

if [ ! -f $package_path ]; then

    if [ ! -f $working_directory/sources/nyancat-$package_version.tar.gz ]; then
        wget -P $working_directory/sources/ https://github.com/klange/nyancat/archive/$package_version.tar.gz
        mv $working_directory/sources/$package_version.tar.gz $working_directory/sources/nyancat-$package_version.tar.gz
    fi
    rm -Rf $working_directory/build/nyancat
    mkdir -p $working_directory/build/nyancat
    cd $working_directory/build/nyancat
    cp $working_directory/sources/nyancat-$package_version.tar.gz .
    tar xvzf nyancat-$package_version.tar.gz
    $(which cp) -af $root_directory/nyancat/* nyancat-$package_version/
    tar cvzf nyancat.tar.gz nyancat-$package_version
    rpmbuild -ta nyancat.tar.gz --target=$distribution_architecture --define "_software_version $package_version"

    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        cd /root
        alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/nyancat-*
        mkdir -p /root/debbuild/DEBS/$distribution_architecture/
        mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    fi

fi
