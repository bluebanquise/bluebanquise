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

Name:          nyancat
Summary:       nyancat
Version:       %{_software_version}
Release:       1%{?dist}
License:       GPL
Group:         System Environment/Libraries
Source:        https://github.com/klange/nyancat.tar.gz
URL:           https://github.com/oxedions/
Packager:      oxedions <oxedions@gmail.com>
%define debug_package %{nil}

%description
License: GPL (https://github.com/klange/nyancat)

Nyancat for fun

%prep
%setup -q

%build

%install
make
mkdir -p $RPM_BUILD_ROOT/usr/bin
cp src/nyancat $RPM_BUILD_ROOT/usr/bin

%files
%defattr(-,root,root,-)
/usr/bin/nyancat
