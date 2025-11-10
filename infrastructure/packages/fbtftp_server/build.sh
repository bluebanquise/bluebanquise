       set -x
       if [ ! -f $working_directory/sources/fbtftp-$fbtftp_version.tar.gz ]; then
           cd $working_directory/sources/
           rm -Rf fbtftp-$fbtftp_version
           mkdir fbtftp-$fbtftp_version
           cd fbtftp-$fbtftp_version
           git clone https://github.com/facebook/fbtftp.git .
           cd ../
           tar cvzf fbtftp-$fbtftp_version.tar.gz fbtftp-$fbtftp_version
       fi
       rm -Rf $working_directory/build/fbtftp
       mkdir -p $working_directory/build/fbtftp
       cd $working_directory/build/fbtftp
       cp $working_directory/sources/fbtftp-$fbtftp_version.tar.gz .
       tar xvzf fbtftp-$fbtftp_version.tar.gz
       cd fbtftp-$fbtftp_version
       python3 setup.py bdist_rpm --spec-only
       cd ..
       tar cvzf fbtftp-$fbtftp_version.tar.gz fbtftp-$fbtftp_version
       rpmbuild -ta fbtftp-$fbtftp_version.tar.gz

       cp -a $root_directory/fbtftp_server fbtftp-server-$fbtftp_server_version
       tar cvzf fbtftp-server-$fbtftp_server_version.tar.gz fbtftp-server-$fbtftp_server_version
       rpmbuild -ta fbtftp-server-$fbtftp_server_version.tar.gz --define "_software_version $fbtftp_server_version" --target=noarch
      
       if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
	   cd /dev/shm
           alien --to-deb --scripts /root/rpmbuild/RPMS/noarch/fbtftp-*
	   mkdir -p /root/debbuild/DEBS/noarch/
	   mv *.deb /root/debbuild/DEBS/noarch/
       fi 
       set +x