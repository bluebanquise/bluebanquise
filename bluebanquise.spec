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

# Define content of roles/<role>/vars/ as configuration
find roles/{core,advanced-core} -type f -path 'roles/*/vars/*' \
 | xargs -l1 -i{} echo '%config %{_sysconfdir}/%{name}/{}' > rolesfiles.txt

# Define content of roles/<role>/{files,templates}/ as non replaceable configuration
find roles/{core,advanced-core} -type f -path 'roles/*/files/*' \
 | xargs -l1 -i{} echo '%config(noreplace) %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

find roles/{core,advanced-core} -type f -path 'roles/*/templates/*' \
 | xargs -l1 -i{} echo '%config(noreplace) %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# Define readme.rst as documentation
find roles/{core,advanced-core} -type f -name readme.rst \
 | xargs -l1 -i{} echo '%doc %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# Manage the directories
find roles/{core,advanced-core} -type d \
 | xargs -l1 -i{} echo '%dir %{_sysconfdir}/%{name}/{}' >> rolesfiles.txt

# All other files in roles subdirectory are standard
find roles/{core,advanced-core} -type f ! -name readme.rst \
 ! -path 'roles/*/templates/*' ! -path 'roles/*/files/*' ! -path 'roles/*/vars/*' \
 | xargs -l1 -i{} echo %{_sysconfdir}/%{name}/{} >> rolesfiles.txt


%build


%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles
cp -a ansible.cfg %{buildroot}%{_sysconfdir}/%{name}/
cp -a roles/core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -a roles/advanced-core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -a roles/addons %{buildroot}%{_sysconfdir}/%{name}/roles/
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles/customs


%files -f rolesfiles.txt
%defattr(-,root,root,-)
%license LICENSE
%doc README.md resources/documentation/ resources/examples/
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/ansible.cfg
%{_sysconfdir}/%{name}/roles/customs/


# Create subpackages for each addon role
%{lua:
local name = rpm.expand("%{name}")
local version = rpm.expand("%{version}")
local sysconfdir = rpm.expand("%{_sysconfdir}")
local addonspath = sysconfdir .. "/" .. name .. "/"

for i,role in ipairs(posix.dir("roles/addons"))
do
  local rolepath = "roles/addons/" .. role
  if (posix.stat(rolepath, 'type') == 'directory') and (role:match('[^.]')) then
    print("%package addons-" .. role .. "\n")
    print("Summary: Addon " .. role .. " for BlueBanquise\n")
    print("Requires: " .. name .. " == " .. version .. "\n")
    print("%description addons-" .. role .. "\n")
    print("%files addons-" .. role .. "\n")
    print("%doc " .. addonspath .. rolepath .. "/readme.rst\n")
    print(addonspath .. rolepath .. "/\n")
  end
end}


%changelog
* Sun Feb  2 2020 Bruno Travouillon <devel@travouillon.fr>
- 
