%define is_ubuntu %(grep -i ubuntu /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)
%define is_opensuse_leap %(grep -i opensuse-leap /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)

# OpenSuse Leap 15.3:
%if %is_opensuse_leap
  %if %(grep '15.3' /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)
     %define dist .osl15.3
  %endif
%endif

# Ubuntu 20.04
%if %is_ubuntu
  %if %(grep '20.04' /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)
    %define dist ubuntu.20.04
  %endif
%endif

Name:     ansible-cmdb
Summary:  ansible-cmdb
Release:  1%{?dist}
Version:  %{_software_version}
License:  GPLv3
Group:    System Environment/Base
Source:   https://github.com/fboender/ansible-cmdb/releases/download/%{_software_version}/ansible-cmdb-%{_software_version}.tar.gz
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


