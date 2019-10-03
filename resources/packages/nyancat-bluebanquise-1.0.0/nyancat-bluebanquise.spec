Name:          nyancat-bluebanquise
Summary:       nyancat-bluebanquise
Version:       1.0.0
Release:       1%{dist}
License:       GPL
Group:         System Environment/Libraries
Source:        https://github.com/oxedions/bluebanquise/nyancat-bluebanquise-1.0.0.tar.gz
URL:           https://github.com/oxedions/
Packager:      oxedions <oxedions@gmail.com>
%define debug_package %{nil}

%description
License: GPL (https://github.com/klange/nyancat)

Nyancat for fun

%prep
%setup -q

%build

%install
make
mkdir -p $RPM_BUILD_ROOT/usr/bin
cp src/nyancat $RPM_BUILD_ROOT/usr/bin

%files
%defattr(-,root,root,-)
/usr/bin/nyancat
