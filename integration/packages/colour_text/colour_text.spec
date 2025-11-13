Name:     python3-colour_text
Summary:  python3-colour_text
Release:  1%{?dist}
Version:  %{_software_version}
License:  Apache-2.0 License
Group:    System Environment/Base
URL:      https://github.com/barry-scott/CLI-tools
Source:   https://bluebanquise.com/sources/python3-colour_text-%{_software_version}.tar.gz
Packager: Benoit Leveugle <benoit.leveugle@gmail.com>

%define debug_package %{nil}

%description
colour_text python module for BlueBanquise

%prep

%setup -q

%build

%install
pip3 install --no-deps --target=$RPM_BUILD_ROOT/%{python3_sitelib}/ colour_text-%{_software_version}-py2.py3-none-any.whl


%files
%defattr(-,root,root,-)
%{python3_sitelib}/colour*

%changelog
* Thu Oct 7 2021 Benoit Leveugle <benoit.leveugle@gmail.com>
- Create
