set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh

package_path_calc

clonezilla_version=$package_version

if [ ! -f $package_path ]; then
    set -x
    if [ ! -f $working_directory/sources/$clonezilla_iso ]; then
        wget -P $working_directory/sources/ $clonezilla_iso_url
    fi

    rm -Rf $working_directory/build/clonezilla
    mkdir -p $working_directory/build/clonezilla
    cd $working_directory/build/clonezilla
    mkdir clonezilla-$clonezilla_version

    osirrox -indev $working_directory/sources/$clonezilla_iso -extract /live clonezilla-$clonezilla_version/live/
    $(which cp) -af $root_directory/clonezilla/* clonezilla-$clonezilla_version/
    tar cvzf clonezilla.tar.gz clonezilla-$clonezilla_version
    rpmbuild -ta clonezilla.tar.gz --target=noarch --define "_software_version $clonezilla_version"

    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        cd /root
        alien --to-deb --scripts /root/rpmbuild/RPMS/noarch/clonezilla-*
        mkdir -p /root/debbuild/DEBS/noarch/
        mv *.deb /root/debbuild/DEBS/noarch/
    fi
    
fi

