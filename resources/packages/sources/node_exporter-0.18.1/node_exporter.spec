Name:     node_exporter
Summary:  node_exporter
Release:  1%{?dist}
Version:  0.18.1
License:  apache-2.0
Group:    System Environment/Base
Source:   https://github.com/prometheus/node_exporter/releases/download/v0.18.1/node_exporter-0.18.1.tar.gz
URL:      https://github.com/prometheus
Packager: Oxedions <oxedions@gmail.com>

Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel

%define debug_package %{nil}

%description
Node_exporter for the BlueBanquise stack
%prep

%setup -q

%build

%install

# Download files (binaries)
wget https://github.com/prometheus/node_exporter/releases/download/v0.18.1/node_exporter-0.18.1.linux-amd64.tar.gz

# Extract
tar xvzf node_exporter-0.18.1.linux-amd64.tar.gz

# Populate binaries
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/
cp -a node_exporter-0.18.1.linux-amd64/node_exporter $RPM_BUILD_ROOT/usr/local/bin/

# Add services
mkdir -p $RPM_BUILD_ROOT/etc/systemd/system/
cp -a services/node_exporter.service $RPM_BUILD_ROOT/etc/systemd/system/

%pre
/usr/bin/getent group node_exporter || /usr/sbin/groupadd -r node_exporter
/usr/bin/getent passwd node_exporter || /usr/sbin/useradd -r --no-create-home --shell /bin/false node_exporter -g node_exporter

%preun

%post
systemctl daemon-reload
mkdir -p $RPM_BUILD_ROOT/etc/node_exporter

%postun
systemctl daemon-reload
/usr/sbin/userdel node_exporter

%files
%defattr(-,root,root,-)
/usr/local/bin/node_exporter
/etc/systemd/system/node_exporter.service
