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
cp -a ansible.cfg %{buildroot}%{_sysconfdir}/%{name}/
cp -a roles/core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -a roles/advanced-core %{buildroot}%{_sysconfdir}/%{name}/roles/
cp -a roles/addons %{buildroot}%{_sysconfdir}/%{name}/roles/
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/roles/customs


%files
%license LICENSE
%doc README.md resources/documentation/ resources/examples/
%dir %{_sysconfdir}/%{name}/
%{_sysconfdir}/%{name}/ansible.cfg
%{_sysconfdir}/%{name}/roles/core/
%{_sysconfdir}/%{name}/roles/advanced-core/
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
