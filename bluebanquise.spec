%{!?version: %define version 1.2.0}

Name:           bluebanquise
Version:        %{version}
Release:        1%{?dist}
Summary:        Ansible based cluster stack

License:        MIT
URL:            https://www.bluebanquise.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
# BuildRequires:  
Requires:       ansible
Requires:       python >= 3.6

%description
BlueBanquise is an opensource project, based on the wish to provide a simple
but flexible stack to deploy and manage cluster of servers or workstations.

The stack is using Ansible, and relies heavily on inventory merge
hash_behaviour and groups.


%prep
%autosetup


%build


%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles
cp -a roles/core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -a roles/advanced-core %{buildroot}%{_sysconfdir}/%{name}/roles/
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles/customs


%files
%license LICENSE
%doc README.md
%dir %{_sysconfdir}/%{name}/
%{_sysconfdir}/%{name}/roles/core/
%{_sysconfdir}/%{name}/roles/advanced-core/
%{_sysconfdir}/%{name}/roles/customs/


%changelog
* Sun Feb  2 2020 Bruno Travouillon <devel@travouillon.fr>
- 
