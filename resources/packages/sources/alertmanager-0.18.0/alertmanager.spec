Name:     alertmanager
Summary:  alertmanager
Release:  1%{?dist}
Version:  0.18.0
License:  apache-2.0
Group:    System Environment/Base
Source:   https://github.com/prometheus/alertmanager/releases/download/v0.18.0/alertmanager-0.18.0.tar.gz
URL:      https://github.com/prometheus
Packager: Oxedions <oxedions@gmail.com>

Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel

%define debug_package %{nil}

%description
Alertmanager and related tools for the BlueBanquise stack
%prep

%setup -q

%build

%install

# Download files (binaries)
wget https://github.com/prometheus/alertmanager/releases/download/v0.18.0/alertmanager-0.18.0.linux-amd64.tar.gz

# Extract
tar xvzf alertmanager-0.18.0.linux-amd64.tar.gz

# Populate binaries
mkdir -p $RPM_BUILD_ROOT/usr/local/bin/
cp -a alertmanager-0.18.0.linux-amd64/alertmanager $RPM_BUILD_ROOT/usr/local/bin/
cp -a alertmanager-0.18.0.linux-amd64/amtool $RPM_BUILD_ROOT/usr/local/bin/

# Add services
mkdir -p $RPM_BUILD_ROOT/etc/systemd/system/
cp -a services/alertmanager.service $RPM_BUILD_ROOT/etc/systemd/system/

%pre
/usr/bin/getent group alertmanager || /usr/sbin/groupadd -r alertmanager
/usr/bin/getent passwd alertmanager || /usr/sbin/useradd -r --no-create-home --shell /bin/false alertmanager -g alertmanager

%preun

%post
systemctl daemon-reload
mkdir -p $RPM_BUILD_ROOT/etc/alertmanager

%postun
systemctl daemon-reload
/usr/sbin/userdel alertmanager

%files
%defattr(-,root,root,-)
/usr/local/bin/alertmanager
/usr/local/bin/amtool
/etc/systemd/system/alertmanager.service
