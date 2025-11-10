        set -x
        if [ ! -f $working_directory/sources/ara-$ara_version.tar.gz ]; then
            wget -P $working_directory/sources/ https://files.pythonhosted.org/packages/$ara_link/ara-$ara_version.tar.gz
        fi
        rm -Rf $working_directory/build/ara
        mkdir -p $working_directory/build/ara
        cd $working_directory/build/ara
        cp $working_directory/sources/ara-$ara_version.tar.gz .
        tar xvzf ara-$ara_version.tar.gz
	cd ara-$ara_version
        python3 setup.py bdist_rpm --spec-only	
	cd ../
        tar cvzf ara-$ara_version.tar.gz ara-$ara_version
        rpmbuild -ta ara-$ara_version.tar.gz
        if [ $distribution == "Ubuntu" ]; then
           cd /dev/shm
           alien --to-deb --scripts /root/rpmbuild/RPMS/noarch/ara-*
           mkdir -p /root/debbuild/DEBS/noarch/
           mv *.deb /root/debbuild/DEBS/noarch/
        fi
        set +x