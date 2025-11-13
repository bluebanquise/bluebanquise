Name:     fbtftp-server
Summary:  fbtftp-server
Release:  1%{?dist}
Version:  %{_software_version}
License:  MIT
Group:    System Environment/Base
URL:      https://github.com/bluebanquise/
Source:   https://bluebanquise.com/sources/fbtftp-server-%{_software_version}.tar.gz
Packager: Benoit Leveugle <benoit.leveugle@gmail.com>

Requires: fbtftp

%define debug_package %{nil}

%description
Facebook tftp simple implementation, based on server example from 
https://github.com/facebook/fbtftp/tree/master/examples

%prep

%setup -q

%post
systemctl daemon-reload

%build

%install
# Populate binaries
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/
cp -a fbtftp-server.py $RPM_BUILD_ROOT/usr/local/bin/

# Add services
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system/
cp -a services/fbtftp-server.service $RPM_BUILD_ROOT/usr/lib/systemd/system/

%files
%defattr(-,root,root,-)
/usr/local/bin/fbtftp-server.py
/usr/lib/systemd/system/fbtftp-server.service

%changelog

* Wed Oct 07 2020 Benoit Leveugle <benoit.leveugle@gmail.com>
- Create
