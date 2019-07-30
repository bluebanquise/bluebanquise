Name:     prometheus
Summary:  prometheus
Release:  1%{?dist}
Version:  2.11.1
License:  apache-2.0
Group:    System Environment/Base
Source:   https://github.com/prometheus/prometheus/releases/download/v2.11.1/prometheus-2.11.1.tar.gz
URL:      https://github.com/prometheus
Packager: Oxedions <oxedions@gmail.com>

Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel

%define debug_package %{nil}

%description
Prometheus and related tools for the BlueBanquise stack
%prep

%setup -q

%build

%install

# Download files (binaries)
wget https://github.com/prometheus/prometheus/releases/download/v2.11.1/prometheus-2.11.1.linux-amd64.tar.gz

# Extract
tar xvzf prometheus-2.11.1.linux-amd64.tar.gz

# Populate binaries
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/
cp -a prometheus-2.11.1.linux-amd64/prometheus $RPM_BUILD_ROOT/usr/local/bin/
cp -a prometheus-2.11.1.linux-amd64/promtool $RPM_BUILD_ROOT/usr/local/bin/

# Add services
mkdir -p $RPM_BUILD_ROOT/etc/systemd/system/
cp -a services/prometheus.service $RPM_BUILD_ROOT/etc/systemd/system/

%pre
/usr/bin/getent group prometheus || /usr/sbin/groupadd -r prometheus
/usr/bin/getent passwd prometheus || /usr/sbin/useradd -r --no-create-home --shell /bin/false prometheus -g prometheus

%preun

%post
systemctl daemon-reload
mkdir -p $RPM_BUILD_ROOT/etc/prometheus

%postun
systemctl daemon-reload
/usr/sbin/userdel prometheus

%files
%defattr(-,root,root,-)
/usr/local/bin/prometheus
/usr/local/bin/promtool
/etc/systemd/system/prometheus.service
