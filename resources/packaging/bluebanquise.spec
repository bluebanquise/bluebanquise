%{!?version: %define version 1.5.0}

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

%if 0%{?el8}
Requires:       python36
Requires:       python3-clustershell
Requires:       python3-jmespath
Requires:       python3-netaddr
%else
Requires:       python3 >= 3.6
Requires:       python36-clustershell
Requires:       python2-jmespath
Requires:       python-netaddr
%endif

%description
BlueBanquise is an opensource project, based on the wish to provide a simple
but flexible stack to deploy and manage cluster of servers or workstations.

The stack is using Ansible, and relies heavily on variables precedence and groups.


%prep
%autosetup

# Delete CICD files
find roles/{core,advanced_core} -maxdepth 2 \( -name 'molecule' -o -name '.ansible-lint' -o -name '.yamllint' \) -print0 \
 | xargs -0 rm -rf

# Define content of roles/<role>/vars/ as configuration
find -L roles/{core,advanced_core} -type f -path 'roles/*/vars/*' \
 | xargs -l1 -i{} echo '%config %{_sysconfdir}/%{name}/{}' > rolesfiles.txt

# Define content of roles/<role>/{files,templates}/ as non replaceable configuration
find -L roles/{core,advanced_core} -type f -path 'roles/*/files/*' \
 | xargs -l1 -i{} echo '%config(noreplace) %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

find -L roles/{core,advanced_core} -type f -path 'roles/*/templates/*' \
 | xargs -l1 -i{} echo '%config(noreplace) %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# Define readme.rst as documentation
find roles/{core,advanced_core} -type f -name readme.rst \
 | xargs -l1 -i{} echo '%doc %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# Manage the directories
find roles/{core,advanced_core} -type d \
 | xargs -l1 -i{} echo '%dir %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# All other files in roles subdirectory are standard
find roles/{core,advanced_core} -type f ! -name readme.rst \
 ! -path 'roles/*/templates/*' ! -path 'roles/*/files/*' ! -path 'roles/*/vars/*' \
 | xargs -l1 -i{} echo %{_sysconfdir}/%{name}/{} >> rolesfiles.txt

# Build list of files for other roles
grep -v 'roles/addons/' rolesfiles.txt > rolesfiles.cores

%build


%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles
cp -a ansible.cfg %{buildroot}%{_sysconfdir}/%{name}/
cp -aL internal %{buildroot}%{_sysconfdir}/%{name}/
cp -aL roles/core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -aL roles/advanced_core %{buildroot}%{_sysconfdir}/%{name}/roles/
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles/custom
mkdir -p %{buildroot}%{_sbindir}
cp -a tools/bluebanquise-playbook %{buildroot}%{_sbindir}/


%files -f rolesfiles.cores
%defattr(-,root,root,-)
%license LICENSE
%doc CHANGELOG.md README.md resources/documentation/ resources/examples/
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/ansible.cfg
%config %{_sysconfdir}/%{name}/internal/
%{_sysconfdir}/%{name}/roles/custom/
%attr(750,root,root) %{_sbindir}/bluebanquise-playbook

%changelog
* Thu Feb 25 2021 Benoit Leveugle <benoit.leveugle@gmail.com>
* Tue Apr 14 2020 strus38 <indigoping4cgmi@gmail.com>
* Sun Feb  2 2020 Bruno Travouillon <devel@travouillon.fr>
-
