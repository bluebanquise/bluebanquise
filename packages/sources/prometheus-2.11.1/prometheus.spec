Name:     prometheus
Summary:  prometheus
Release:  1%{?dist}
Version:  2.11.1
License:  apache-2.0
Group:    System Environment/Base
Source:   https://github.com/prometheus/prometheus/releases/download/v2.11.1/prometheus-2.11.1.tar.gz
URL:      https://github.com/prometheus
Packager: Oxedions <oxedions@gmail.com>


%define debug_package %{nil}

%description
Prometheus and related tools (node_exporter and alertmanager) for the BlueBanquise stack
%prep

%setup -q

%build

%install

# Download files (binaries)
wget https://github.com/prometheus/prometheus/releases/download/v2.11.1/prometheus-2.11.1.linux-amd64.tar.gz
#wget https://github.com/prometheus/node_exporter/releases/download/v0.18.1/node_exporter-0.18.1.linux-amd64.tar.gz
#wget https://github.com/prometheus/alertmanager/releases/download/v0.18.0/alertmanager-0.18.0.linux-amd64.tar.gz

# Extract
tar xvzf prometheus-2.11.1.linux-amd64.tar.gz
#tar xvzf node_exporter-0.18.1.linux-amd64.tar.gz
#tar xvzf alertmanager-0.18.0.linux-amd64.tar.gz

# Create needed folders
mkdir -p $RPM_BUILD_ROOT/etc/prometheus
mkdir -p $RPM_BUILD_ROOT/etc/node_exporter
mkdir -p $RPM_BUILD_ROOT/etc/alertmanager

# Populate binaries
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/
cp -a prometheus-2.11.1.linux-amd64/prometheus $RPM_BUILD_ROOT/usr/local/bin/
cp -a prometheus-2.11.1.linux-amd64/promtool $RPM_BUILD_ROOT/usr/local/bin/
#cp -a node_exporter-0.18.1.linux-amd64/node_exporter $RPM_BUILD_ROOT/usr/local/bin/
#cp -a alertmanager-0.18.0.linux-amd64/alertmanager $RPM_BUILD_ROOT/usr/local/bin/
#cp -a alertmanager-0.18.0.linux-amd64/amtool $RPM_BUILD_ROOT/usr/local/bin/

# Add services
mkdir -p $RPM_BUILD_ROOT/etc/systemd/system/
cp -a services/* $RPM_BUILD_ROOT/etc/systemd/system/

%files
%defattr(-,root,root,-)
/*

