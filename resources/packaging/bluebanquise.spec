%{!?version: %define version 1.3.0}

%define roles_addons clone clustershell diskless grafana nic_nmcli ofed \
ofed_sm openldap_client openldap_server powerman prometheus_client \
prometheus_server report root_password slurm sssd users_basic Lmod

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

The stack is using Ansible, and relies heavily on inventory merge
hash_behaviour and groups.


%prep
%autosetup

# Delete CICD files
find roles/{core,advanced-core,addons} -maxdepth 2 \( -name 'molecule' -o -name '.ansible-lint' -o -name '.yamllint' \) -print0 \
 | xargs -0 rm -rf

# Define content of roles/<role>/vars/ as configuration
find -L roles/{core,advanced-core,addons} -type f -path 'roles/*/vars/*' \
 | xargs -l1 -i{} echo '%config %{_sysconfdir}/%{name}/{}' > rolesfiles.txt

# Define content of roles/<role>/{files,templates}/ as non replaceable configuration
find -L roles/{core,advanced-core,addons} -type f -path 'roles/*/files/*' \
 | xargs -l1 -i{} echo '%config(noreplace) %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

find -L roles/{core,advanced-core,addons} -type f -path 'roles/*/templates/*' \
 | xargs -l1 -i{} echo '%config(noreplace) %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# Define readme.rst as documentation
find roles/{core,advanced-core,addons} -type f -name readme.rst \
 | xargs -l1 -i{} echo '%doc %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# Manage the directories
find roles/{core,advanced-core,addons,macros} -type d \
 | xargs -l1 -i{} echo '%dir %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# All other files in roles subdirectory are standard
find roles/{core,advanced-core,addons,macros} -type f ! -name readme.rst \
 ! -path 'roles/*/templates/*' ! -path 'roles/*/files/*' ! -path 'roles/*/vars/*' \
 | xargs -l1 -i{} echo %{_sysconfdir}/%{name}/{} >> rolesfiles.txt

# Build list of files for each addon role
ROLES_ADDONS="%{roles_addons}"
for role in ${ROLES_ADDONS//$'\n'/}; do
    grep "roles/addons/${role}/" rolesfiles.txt > rolesfiles.addons.${role} ;
done

# Build list of files for other roles
grep -v 'roles/addons/' rolesfiles.txt > rolesfiles.cores

# Workaround 1.2.0: remove execution mod to skip brp-mangle-shebangs
chmod -x roles/addons/clone/files/clone.ipxe roles/addons/clone/files/deploy_clone.ipxe


%build


%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles
cp -a ansible.cfg %{buildroot}%{_sysconfdir}/%{name}/
cp -aL internal %{buildroot}%{_sysconfdir}/%{name}/
cp -aL roles/core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -aL roles/advanced-core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -aL roles/addons %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -aL roles/macros %{buildroot}%{_sysconfdir}/%{name}/roles/
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles/customs
mkdir -p %{buildroot}%{_sbindir}
cp -a tools/bluebanquise-playbook %{buildroot}%{_sbindir}/


%files -f rolesfiles.cores
%defattr(-,root,root,-)
%license LICENSE
%doc CHANGELOG.md README.md resources/documentation/ resources/examples/
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/ansible.cfg
%config %{_sysconfdir}/%{name}/internal/
%{_sysconfdir}/%{name}/roles/customs/
%attr(750,root,root) %{_sbindir}/bluebanquise-playbook


# Create subpackages for each addon role
%{lua:
local name = rpm.expand("%{name}")
local version = rpm.expand("%{version}")

for role in string.gmatch(rpm.expand("%{roles_addons}"), "[%w_-]+")
do
  print("%package addons-" .. role .. "\n")
  print("Summary: Addon " .. role .. " for BlueBanquise\n")
  print("Requires: " .. name .. " == " .. version .. "\n")
  print("%description addons-" .. role .. "\n")
  print("%files addons-" .. role .. " -f rolesfiles.addons." .. role .. "\n")
end}


%changelog
* Sun Feb  2 2020 Bruno Travouillon <devel@travouillon.fr>
* Tue Apr 14 2020 strus38 <indigoping4cgmi@gmail.com>
- 
