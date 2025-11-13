set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh

if [ ! -f $working_directory/sources/ssh_wait-$ssh_wait_version-py2.py3-none-any.whl ]; then
    wget -P $working_directory/sources/ $ssh_wait_version_url
fi
rm -Rf $working_directory/build/ssh-wait
mkdir -p $working_directory/build/ssh-wait
cd $working_directory/build/ssh-wait
mkdir python3-ssh-wait-$ssh_wait_version
cp $working_directory/sources/ssh_wait-$ssh_wait_version-py2.py3-none-any.whl python3-ssh-wait-$ssh_wait_version/
$(which cp) -af $root_directory/ssh-wait/ssh-wait.spec python3-ssh-wait-$ssh_wait_version/
tar cvzf python3-ssh-wait-$ssh_wait_version.tar.gz python3-ssh-wait-$ssh_wait_version
rpmbuild -ta python3-ssh-wait-$ssh_wait_version.tar.gz --define "_software_version $ssh_wait_version"

if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/x86_64/python3-ssh-wait-*
    mkdir -p /root/debbuild/DEBS/noarch/
    mv *.deb /root/debbuild/DEBS/noarch/
fi

set +x
