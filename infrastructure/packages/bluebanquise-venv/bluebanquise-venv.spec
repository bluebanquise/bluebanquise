Name:          bluebanquise-venv
Summary:       bluebanquise-venv
Version:       %{_software_version}
Release:       1%{?dist}
License:       MIT
Group:         System Environment/Libraries
Source:        https://www.bluebanquise.com/bluebanquise-venv.tar.gz
URL:           https://www.bluebanquise.com
Packager:      oxedions <oxedions@gmail.com>
%define debug_package %{nil}
%define __brp_mangle_shebangs /usr/bin/true

%description
Bluebanquise stack python virtual environment

%prep
%setup -q

%build

%install
rm -Rf /usr/lib/share/bluebanquise_venv/
mkdir -p /usr/lib/share/bluebanquise_venv/
python3 -m venv /usr/lib/share/bluebanquise_venv/
source /usr/lib/share/bluebanquise_venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install setuptools setuptools_rust
pip3 install ansible netaddr clustershell jmespath jinja2 "ara[server]" rabbitmq celery flask flask-restapi ssh-wait colour_text

mkdir -p $RPM_BUILD_ROOT/usr/lib/share/bluebanquise_venv/
cp -a /usr/lib/share/bluebanquise_venv/* $RPM_BUILD_ROOT/usr/lib/share/bluebanquise_venv/
rm -Rf /usr/lib/share/bluebanquise_venv/

%files
%defattr(-,root,root,-)
/usr/lib/share/bluebanquise_venv
/usr/lib/share/bluebanquise_venv/*
