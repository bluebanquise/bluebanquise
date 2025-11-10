%define is_ubuntu %(grep -i ubuntu /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)
%define is_opensuse_leap %(grep -i opensuse-leap /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)

# SUSE 12.5
%if 0%{?sle_version} == 120500
  %define dist .sl125
%endif
# SUSE 15.1:
%if 0%{?sle_version} == 150100
  %define dist .sl15
%endif
# SUSE 15.2:
%if 0%{?sle_version} == 150200
  %define dist .sl15
%endif
# SUSE 15.3:
%if 0%{?sle_version} == 150300
  %define dist .sl15
%endif
%if 0%{?sle_version} == 150400
  %define dist .sl15
%endif
%if 0%{?sle_version} == 150500
  %define dist .sl15
%endif

# Ubuntu 20.04
%if %is_ubuntu
  %if %(grep '20.04' /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)
    %define dist u20
  %endif
  %if %(grep '22.04' /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)
    %define dist u22
  %endif
%endif

%if 0%{?sle_version} 
  %define tftp_path /srv/tftpboot/
  %define http_path /srv/www/htdocs/
%else
  %define tftp_path /var/lib/tftpboot/
  %define http_path /var/www/html/
%endif

Name:          clonezilla
Summary:       clonezilla
Version:       %{_software_version}
Release:       1%{?dist}
License:       GPL
Group:         System Environment/Libraries
Source:        https://clonezilla.org/clonezilla.tar.gz
URL:           https://clonezilla.org
Packager:      oxedions <oxedions@gmail.com>
%define debug_package %{nil}

%description
License: GPL-2.0 (https://clonezilla.org)

Clonezilla Live

%prep
%setup -q

%build

%install
mkdir -p $RPM_BUILD_ROOT/%{http_path}/pxe/tools/clonezilla/
cp live/initrd.img $RPM_BUILD_ROOT/%{http_path}/pxe/tools/clonezilla/
cp live/vmlinuz $RPM_BUILD_ROOT/%{http_path}/pxe/tools/clonezilla/
cp live/filesystem.squashfs $RPM_BUILD_ROOT/%{http_path}/pxe/tools/clonezilla/

%files
%defattr(-,root,root,-)
%{http_path}/pxe/tools/clonezilla/initrd.img
%{http_path}/pxe/tools/clonezilla/vmlinuz
%{http_path}/pxe/tools/clonezilla/filesystem.squashfs
