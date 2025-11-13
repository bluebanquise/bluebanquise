%define debug_package %{nil}

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

Name:     loki
Release:  1%{?dist}
Version:  %{_software_version}
Summary:  Loki
Group:    Grafana
License:  Apache License 2.0
URL:      https://github.com/grafana/loki
Packager: Oxedions <oxedions@gmail.com>
Source: https://github.com/grafana/loki/releases/download/loki.tar.gz

%description
Loki is a horizontally-scalable, highly-available, multi-tenant log aggregation system inspired by Prometheus. It is designed to be very cost effective and easy to operate. It does not index the contents of the logs, but rather a set of labels for each log stream.

%prep

%build

%install

# Download files (binaries)
cd /tmp
wget -nc --timeout=10 --tries=5 --retry-connrefused --waitretry=30 https://github.com/grafana/loki/releases/download/v%{_software_version}/loki-linux-%{_software_architecture}.zip

# Extract
unzip -o loki-linux-%{_software_architecture}.zip

# Populate binaries
mkdir -p $RPM_BUILD_ROOT/usr/bin/
cp -a loki-linux-%{_software_architecture} $RPM_BUILD_ROOT/usr/bin/loki

%pre

%post

%preun

%postun

%files
%defattr(-,root,root,-)
/usr/bin/loki

