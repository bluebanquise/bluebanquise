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

Name:          alpine
Summary:       alpine
Version:       %{_software_version}
Release:       1%{?dist}
License:       GPL
Group:         System Environment/Libraries
Source:        https://www.alpinelinux.org/alpine.tar.gz
URL:           https://www.alpinelinux.org
Packager:      oxedions <oxedions@gmail.com>
%define debug_package %{nil}

%description
License: GPL-2.0 (https://www.alpinelinux.org)

Alpine Live

%prep
%setup -q

%build

%install
mkdir -p $RPM_BUILD_ROOT/%{http_path}/pxe/tools/alpine/x86_64/
mkdir -p $RPM_BUILD_ROOT/%{http_path}/pxe/tools/alpine/aarch64/
cp boot.ipxe $RPM_BUILD_ROOT/%{http_path}/pxe/tools/alpine/
rm -Rf boot
tar xvzf alpine-netboot-aarch64.tar.gz
cd boot/
mv initramfs-lts modloop-lts vmlinuz-lts $RPM_BUILD_ROOT/%{http_path}/pxe/tools/alpine/aarch64/
chmod 644 $RPM_BUILD_ROOT/%{http_path}/pxe/tools/alpine/aarch64/*
cd ../
rm -Rf boot
tar xvzf alpine-netboot-x86_64.tar.gz
cd boot/
mv initramfs-lts modloop-lts vmlinuz-lts $RPM_BUILD_ROOT/%{http_path}/pxe/tools/alpine/x86_64/
chmod 644 $RPM_BUILD_ROOT/%{http_path}/pxe/tools/alpine/x86_64/*
cd ../
rm -Rf boot

%files
%defattr(-,root,root,-)
%{http_path}/pxe/tools/alpine/aarch64/initramfs-lts
%{http_path}/pxe/tools/alpine/aarch64/modloop-lts
%{http_path}/pxe/tools/alpine/aarch64/vmlinuz-lts
%{http_path}/pxe/tools/alpine/x86_64/initramfs-lts
%{http_path}/pxe/tools/alpine/x86_64/modloop-lts
%{http_path}/pxe/tools/alpine/x86_64/vmlinuz-lts
%{http_path}/pxe/tools/alpine/boot.ipxe

