set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
#source $CURRENT_DIR/version.sh
        
rm -Rf $working_directory/build/bluebanquise-tools
mkdir -p $working_directory/build/bluebanquise-tools
cd $working_directory/build/bluebanquise-tools
git clone https://github.com/bluebanquise/tools.git .
./packages.sh

if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/noarch/bluebanquise-*
    mkdir -p /root/debbuild/DEBS/noarch/
    mv *.deb /root/debbuild/DEBS/noarch/
fi

set +x
