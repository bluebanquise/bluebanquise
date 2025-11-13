        if [ -z $4 ]
        then
          echo "Error, please add a tag"
        else
          bb_tag=$4
        fi
        source $root_directory/bluebanquise/build.sh


set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
#source $CURRENT_DIR/version.sh
        
rm -Rf $working_directory/build/bluebanquise
mkdir -p $working_directory/build/bluebanquise
echo "Tag to checkout will be asked."
echo "Tag will be used as version for rpm."
cd $working_directory/build/bluebanquise
mkdir bluebanquise
cd bluebanquise
git clone https://github.com/bluebanquise/bluebanquise.git .
git fetch --all --tags
git checkout tags/$bb_tag -b build
cd ../
mv bluebanquise bluebanquise-$bb_tag
tar cvzf bluebanquise-$bb_tag.tar.gz bluebanquise-$bb_tag
rpmbuild -ta bluebanquise-$bb_tag.tar.gz --define "version $bb_tag"

set +x
