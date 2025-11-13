set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh

if [ ! -f $working_directory/sources/colour_text-$colour_text_version-py2.py3-none-any.whl ]; then
    wget -P $working_directory/sources/ $colour_text_version_url
fi
rm -Rf $working_directory/build/colour_text
mkdir -p $working_directory/build/colour_text
cd $working_directory/build/colour_text
mkdir python3-colour_text-$colour_text_version
cp $working_directory/sources/colour_text-$colour_text_version-py2.py3-none-any.whl python3-colour_text-$colour_text_version/
$(which cp) -af $root_directory/colour_text/colour_text.spec python3-colour_text-$colour_text_version/
tar cvzf python3-colour_text-$colour_text_version.tar.gz python3-colour_text-$colour_text_version
rpmbuild -ta python3-colour_text-$colour_text_version.tar.gz --define "_software_version $colour_text_version"

if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/x86_64/python3-colour_text-*
    mkdir -p /root/debbuild/DEBS/noarch/
    mv *.deb /root/debbuild/DEBS/noarch/
fi


set +x
