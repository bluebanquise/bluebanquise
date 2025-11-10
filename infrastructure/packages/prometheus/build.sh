set -x
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh


if [ $distribution_architecture == 'x86_64' ]; then
  prometheus_arch=amd64
elif [ $distribution_architecture == 'aarch64' ] || [ $distribution_architecture == 'arm64' ]; then
  prometheus_arch=arm64
fi

if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
  mkdir -p /root/debbuild/DEBS/noarch/
  mkdir -p /root/debbuild/DEBS/$distribution_architecture/
fi

rm -Rf $working_directory/build/prometheus
mkdir -p $working_directory/build/prometheus
cd $working_directory/build/prometheus


package_version=$prometheus_client_version
package_name=prometheus_client
package_native_architecture=noarch
package_no_os_name="true"
package_path_calc
if [ ! -f $package_path ]; then
  if [ ! -f $working_directory/sources/prometheus_client-$prometheus_client_version.tar.gz ]; then
    cd /tmp
    wget -nc -P $working_directory/sources/ https://github.com/prometheus/client_python/archive/v$prometheus_client_version.tar.gz
    mv $working_directory/sources/v$prometheus_client_version.tar.gz $working_directory/sources/prometheus_client-$prometheus_client_version.tar.gz
  fi
  cp $working_directory/sources/prometheus_client-$prometheus_client_version.tar.gz .
  tar xvzf prometheus_client-$prometheus_client_version.tar.gz
  cd client_python-$prometheus_client_version
  python3 setup.py bdist_rpm --spec-only
#  sed -i 's/\/bin\/bash/\/bin\/bash\nexit 0\n/' /usr/lib/rpm/brp-python-bytecompile
#  sed -i 's/setup.py/setup.py --no-compile/' dist/prometheus_client.spec
#  sed -i '1s/^/%undefine __brp_python_bytecompile\n/' dist/prometheus_client.spec 
  cd ..
  mv client_python-$prometheus_client_version prometheus_client-$prometheus_client_version
  tar cvzf prometheus_client-$prometheus_client_version.tar.gz prometheus_client-$prometheus_client_version
  rpmbuild -ta prometheus_client-$prometheus_client_version.tar.gz
  if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/noarch/prometheus_client-*
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    cd $working_directory/build/prometheus
  fi
fi

unset package_native_architecture
unset package_no_os_name
cd $working_directory/build/prometheus

package_version=$prometheus_version
package_name=prometheus
package_path_calc
if [ ! -f $package_path ]; then
  cp -a $root_directory/prometheus/prometheus $working_directory/build/prometheus/prometheus
  mv prometheus prometheus-$prometheus_version
  tar cvzf prometheus-$prometheus_version.linux-$prometheus_arch.tar.gz prometheus-$prometheus_version
  rpmbuild -ta prometheus-$prometheus_version.linux-$prometheus_arch.tar.gz --target=$distribution_architecture --define "_software_version $prometheus_version" --define "_software_architecture $prometheus_arch"
  if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/prometheus-*
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    cd $working_directory/build/prometheus
  fi
fi

package_version=$alertmanager_version
package_name=alertmanager
package_path_calc
if [ ! -f $package_path ]; then
  cp -a $root_directory/prometheus/alertmanager $working_directory/build/prometheus/alertmanager
  mv alertmanager alertmanager-$alertmanager_version
  tar cvzf alertmanager-$alertmanager_version.linux-$prometheus_arch.tar.gz alertmanager-$alertmanager_version
  rpmbuild -ta alertmanager-$alertmanager_version.linux-$prometheus_arch.tar.gz --target=$distribution_architecture --define "_software_version $alertmanager_version" --define "_software_architecture $prometheus_arch"
  if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/alertmanager-*
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    cd $working_directory/build/prometheus
  fi
fi

package_version=$node_exporter_version
package_name=node_exporter
package_path_calc
if [ ! -f $package_path ]; then
  cp -a $root_directory/prometheus/node_exporter $working_directory/build/prometheus/node_exporter
  mv node_exporter node_exporter-$node_exporter_version
  tar cvzf node_exporter-$node_exporter_version.linux-$prometheus_arch.tar.gz node_exporter-$node_exporter_version
  rpmbuild -ta node_exporter-$node_exporter_version.linux-$prometheus_arch.tar.gz --target=$distribution_architecture --define "_software_version $node_exporter_version" --define "_software_architecture $prometheus_arch"
  if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/node_exporter-*
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    cd $working_directory/build/prometheus
  fi
fi

package_version=$ipmi_exporter_version
package_name=ipmi_exporter
package_path_calc
if [ ! -f $package_path ]; then
  cp -a $root_directory/prometheus/ipmi_exporter $working_directory/build/prometheus/ipmi_exporter
  mv ipmi_exporter ipmi_exporter-$ipmi_exporter_version
  tar cvzf ipmi_exporter-$ipmi_exporter_version.linux-$prometheus_arch.tar.gz ipmi_exporter-$ipmi_exporter_version
  rpmbuild -ta ipmi_exporter-$ipmi_exporter_version.linux-$prometheus_arch.tar.gz --target=$distribution_architecture --define "_software_version $ipmi_exporter_version" --define "_software_architecture $prometheus_arch"
  if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/ipmi_exporter-*
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    cd $working_directory/build/prometheus
  fi
fi

package_version=$snmp_exporter_version
package_name=snmp_exporter
package_path_calc
if [ ! -f $package_path ]; then
  cp -a $root_directory/prometheus/snmp_exporter $working_directory/build/prometheus/snmp_exporter
  mv snmp_exporter snmp_exporter-$snmp_exporter_version
  tar cvzf snmp_exporter-$snmp_exporter_version.linux-$prometheus_arch.tar.gz snmp_exporter-$snmp_exporter_version
  rpmbuild -ta snmp_exporter-$snmp_exporter_version.linux-$prometheus_arch.tar.gz --target=$distribution_architecture --define "_software_version $snmp_exporter_version" --define "_software_architecture $prometheus_arch"
  if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/snmp_exporter-*
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    cd $working_directory/build/prometheus
  fi
fi

package_version=$karma_version
package_name=karma
package_path_calc
if [ ! -f $package_path ]; then
  cp -a $root_directory/prometheus/karma $working_directory/build/prometheus/karma
  mv karma karma-$karma_version
  tar cvzf karma-linux-$prometheus_arch.tar.gz karma-$karma_version
  rpmbuild -ta karma-linux-$prometheus_arch.tar.gz --target=$distribution_architecture --define "_software_version $karma_version" --define "_software_architecture $prometheus_arch"
  if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    cd /root
    alien --to-deb --scripts /root/rpmbuild/RPMS/$distribution_architecture/karma-*
    mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    cd $working_directory/build/prometheus
  fi
fi

cd $CURRENT_DIR