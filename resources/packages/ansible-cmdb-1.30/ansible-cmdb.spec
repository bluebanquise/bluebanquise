Name:     ansible-cmdb
Summary:  ansible-cmdb
Release:  1%{?dist}
Version:  1.30
License:  GPLv3
Group:    System Environment/Base
Source:   https://github.com/fboender/ansible-cmdb/releases/download/1.30/ansible-cmdb-1.30.tar.gz
URL:      https://github.com/fboender/ansible-cmdb/
Packager: Oxedions <oxedions@gmail.com>
%define __spec_install_post %{nil}
%define debug_package %{nil}
%define _missing_doc_files_terminate_build 0

%description
Ansible-CMDB tool for bluebanquise stack
%prep

%setup -q

%build

%install
umask 0022 && mkdir -p $RPM_BUILD_ROOT/usr/local/lib/ansible-cmdb
umask 0022 && mkdir -p $RPM_BUILD_ROOT/usr/local/man/man1
umask 0022 && cp -a * $RPM_BUILD_ROOT/usr/local/lib/ansible-cmdb/
cp -a ansible-cmdb.man.1 $RPM_BUILD_ROOT/usr/local/man/man1/ansible-cmdb.1
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/
ln -s /usr/local/lib/ansible-cmdb/ansible-cmdb $RPM_BUILD_ROOT/usr/local/bin/ansible-cmdb

%files
%defattr(-,root,root,-)
/*


