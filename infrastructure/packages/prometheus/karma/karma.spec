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

Name:     karma
Summary:  karma
Release:  1%{?dist}
Version:  %{_software_version}
License:  apache-2.0
Group:    System Environment/Base
Source:   https://github.com/prymitive/karma/releases/download/v%{_software_version}/karma-linux-%{_software_architecture}.tar.gz
URL:      https://github.com/prymitive
Packager: Oxedions <oxedions@gmail.com>

%define debug_package %{nil}

%description
karma for the BlueBanquise stack
%prep

%setup -q

%build

%install

# Download files (binaries)
cd /tmp
wget -nc --timeout=10 --tries=5 --retry-connrefused --waitretry=30 https://github.com/prymitive/karma/releases/download/v%{_software_version}/karma-linux-%{_software_architecture}.tar.gz

# Extract
tar xvzf karma-linux-%{_software_architecture}.tar.gz

# Populate binaries
mkdir -p $RPM_BUILD_ROOT/bin/
cp -a karma-linux-%{_software_architecture} $RPM_BUILD_ROOT/bin/karma

%pre

%preun

%post

%postun

%files
%defattr(-,root,root,-)
/bin/karma
