set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh

package_path_calc

loki_version=$package_version

if [ ! -f $package_path ]; then

    if [ $distribution_architecture == 'x86_64' ]; then
      loki_arch=amd64
    elif [ $distribution_architecture == 'aarch64' ] || [ $distribution_architecture == 'arm64' ]; then
      loki_arch=arm64
    fi

    rm -Rf $working_directory/build/loki
    mkdir -p $working_directory/build/loki
    cd $working_directory/build/loki
    mkdir loki-$loki_version
    $(which cp) -af $root_directory/loki/loki/* loki-$loki_version/
    tar cvzf loki.tar.gz loki-$loki_version

    rpmbuild -ta loki.tar.gz --target=$distribution_architecture --define "_software_version $loki_version" --define "_software_architecture $loki_arch"

    rm -Rf $working_directory/build/promtail
    mkdir -p $working_directory/build/promtail
    cd $working_directory/build/promtail
    mkdir promtail-$loki_version
    $(which cp) -af $root_directory/loki/promtail/* promtail-$loki_version/
    tar cvzf promtail.tar.gz promtail-$loki_version

    rpmbuild -ta promtail.tar.gz --target=$distribution_architecture --define "_software_version $loki_version" --define "_software_architecture $loki_arch"

    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        cd /root
        alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/loki-*
        alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/promtail-*
        mkdir -p /root/debbuild/DEBS/$distribution_architecture/
        mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    fi

fi