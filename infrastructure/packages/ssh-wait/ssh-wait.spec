Name:     python3-ssh-wait
Summary:  python3-ssh-wait
Release:  1%{?dist}
Version:  %{_software_version}
License:  Apache-2.0 License
Group:    System Environment/Base
URL:      https://github.com/barry-scott/CLI-tools
Source:   https://bluebanquise.com/sources/python3-ssh-wait-%{_software_version}.tar.gz
Packager: Benoit Leveugle <benoit.leveugle@gmail.com>

%define debug_package %{nil}

Requires: python3-colour_text

%description
ssh-wait python module for BlueBanquise

%prep

%setup -q

%build

%install
pip3 install --no-deps --target=$RPM_BUILD_ROOT/%{python3_sitelib}/ ssh_wait-%{_software_version}-py2.py3-none-any.whl

%files
%defattr(-,root,root,-)
%{python3_sitelib}/ssh_wait*
%exclude %{python3_sitelib}/colour*

%changelog
* Thu Oct 7 2021 Benoit Leveugle <benoit.leveugle@gmail.com>
- Create
