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

Name:     mll
Summary:  mll
Release:  1%{?dist}
Version:  %{_software_version}
License:  MIT
Group:    System Environment/Base
URL:      https://github.com/ivandavidov/minimal
Source:   https://bluebanquise.com/sources/mll-%{_software_version}.tar.gz
Packager: Benoit Leveugle <benoit.leveugle@gmail.com>

%define debug_package %{nil}

%description
MLL build for BlueBanquise PXE

%prep

%setup -q

%post
restorecon -Rv /var/www/html/pxe/MLL

%build

%install
# Populate binaries
mkdir -p $RPM_BUILD_ROOT/var/www/html/pxe/MLL/%{_architecture}/
cp kernel.xz rootfs.xz $RPM_BUILD_ROOT/var/www/html/pxe/MLL/%{_architecture}/

%files
%defattr(-,root,root,-)
/var/www/html/pxe/MLL/%{_architecture}/*

%changelog

* Wed Aug 11 2021 Benoit Leveugle <benoit.leveugle@gmail.com>
- Create
