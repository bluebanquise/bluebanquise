set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh

package_path_calc

atftp_version=$atftp_remote_version

if [ ! -f $package_path ]; then

    if [[ ! -f /usr/bin/aclocal-1.16 ]]; then ln -s /usr/bin/aclocal /usr/bin/aclocal-1.16; fi
    if [[ ! -f /usr/bin/autoconf-1.16 ]]; then ln -s /usr/bin/autoconf /usr/bin/autoconf-1.16; fi
    if [[ ! -f /usr/bin/automake-1.16 ]]; then ln -s /usr/bin/automake /usr/bin/automake-1.16; fi

    rm -Rf $working_directory/build/atftp
    mkdir -p $working_directory/build/atftp/

    if [ ! -f $working_directory/sources/atftp-$atftp_version.tar.gz ]; then
        wget --no-check-certificate -P $working_directory/sources/ https://freefr.dl.sourceforge.net/project/atftp/atftp-$atftp_version.tar.gz
    fi

    # If Debian 12, patch brp-compress
    if [ "$distribution" == 'Debian' ]; then
      if [ "$distribution_version" == "12" ]; then
    sed -i '1 s/^.*$/#!\/bin\/bash/' /usr/lib/rpm/brp-compress
      fi
      if [ "$distribution_version" == "13" ]; then
    sed -i '1 s/^.*$/#!\/bin\/bash/' /usr/lib/rpm/brp-compress
      fi
    fi

    cd $working_directory/build/atftp/
    cp $working_directory/sources/atftp-$atftp_version.tar.gz $working_directory/build/atftp/
    tar xvzf atftp-$atftp_version.tar.gz
    eval $(which cp) -f $root_directory/atftp/* atftp-$atftp_version/
    cd atftp-$atftp_version/
    ./autogen.sh
    cd ../
    rm -f atftp-$atftp_version/redhat/atftp.spec
    mv atftp-$atftp_version bluebanquise-atftp-$bluebanquise_atftp_version
    tar cvzf atftp.tar.gz bluebanquise-atftp-$bluebanquise_atftp_version
    rpmbuild -ta atftp.tar.gz --target=$distribution_architecture --define "_software_version $bluebanquise_atftp_version" --define "_lto_cflags %{nil}"

    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        cd /root
        alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/bluebanquise-atftp-*
        mkdir -p /root/debbuild/DEBS/$distribution_architecture/
        mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    fi

fi
