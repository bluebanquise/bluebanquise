set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh

if [ ! -f $working_directory/sources/ansible-cmdb-$ansible_cmdb_version.tar.gz ]; then
    wget -P $working_directory/sources/ https://github.com/fboender/ansible-cmdb/releases/download/$ansible_cmdb_version/ansible-cmdb-$ansible_cmdb_version.tar.gz
fi
rm -Rf $working_directory/build/ansible-cmdb
mkdir -p $working_directory/build/ansible-cmdb
cd $working_directory/build/ansible-cmdb
cp $working_directory/sources/ansible-cmdb-$ansible_cmdb_version.tar.gz $working_directory/build/ansible-cmdb/
tar xvzf ansible-cmdb-$ansible_cmdb_version.tar.gz
$(which cp) -af $root_directory/ansible-cmdb/* ansible-cmdb-$ansible_cmdb_version/
tar cvzf ansible-cmdb-$ansible_cmdb_version.tar.gz ansible-cmdb-$ansible_cmdb_version
rpmbuild -ta ansible-cmdb-$ansible_cmdb_version.tar.gz --target=$distribution_architecture --define "_software_version $ansible_cmdb_version"

if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/ansible-cmdb-*
    mkdir -p /root/debbuild/DEBS/$distribution_architecture/
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
fi

set +x