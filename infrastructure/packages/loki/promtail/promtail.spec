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

Name:     promtail
Release:  1%{?dist}
Version:  %{_software_version}
Summary:  Promtail agent
Group:    Grafana
License:  Apache License 2.0
URL:      https://github.com/grafana/loki
Packager: Oxedions <oxedions@gmail.com>
Source: https://github.com/grafana/loki/releases/download/promtail.tar.gz

%description
Promtail is an agent which ships the contents of local logs to a private Loki
instance or Grafana Cloud. It is usually
deployed to every machine that has applications needed to be monitored.

It primarily:

1. Discovers targets
2. Attaches labels to log streams
3. Pushes them to the Loki instance.

Currently, Promtail can tail logs from two sources: local log files and the
systemd journal.

%prep

%build

%install

# Download files (binaries)
cd /tmp
wget -nc --timeout=10 --tries=5 --retry-connrefused --waitretry=30 https://github.com/grafana/loki/releases/download/v%{_software_version}/promtail-linux-%{_software_architecture}.zip

# Extract
unzip -o promtail-linux-%{_software_architecture}.zip

# Populate binaries
mkdir -p $RPM_BUILD_ROOT/usr/bin/
cp -a promtail-linux-%{_software_architecture} $RPM_BUILD_ROOT/usr/bin/promtail

%pre

%post

%preun

%postun

%files
%defattr(-,root,root,-)
/usr/bin/promtail
