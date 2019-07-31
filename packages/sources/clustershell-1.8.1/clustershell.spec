%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitelib: %global python2_sitelib %{python_sitelib}}
%{!?__python: %global __python python}
%{!?__python2: %global __python2 %{__python}}

%if 0%{?fedora} >= 22
%{!?python2_pkgversion: %global python2_pkgversion 2}
%global python2_pkgprefix python%{python2_pkgversion}
%else
%global python2_pkgprefix python
%endif

%if 0%{?rhel}
%{!?python3_pkgversion: %global python3_pkgversion 34}
%else
%{!?python3_pkgversion: %global python3_pkgversion 3}
%endif
%global python3_pkgprefix python%{python3_pkgversion}

# Undefined in SUSE
%{!?__python3: %global __python3 python3}
%{!?python3_shortver: %global python3_shortver %(%{__python3} -c 'import sys; print(str(sys.version_info.major) + "." + str(sys.version_info.minor))')}

%global srcname ClusterShell

Name:           clustershell
Version:        1.8.1
Release:        1%{?dist}
Summary:        Python framework for efficient cluster administration

%if 0%{?suse_version}
License:        LGPL-2.1
%else
License:        LGPLv2+
%endif
%if 0%{?suse_version}
Group:          Productivity/Clustering/Computing
%else if 0%{?rhel}
Group:          System Environment/Base
%endif
URL:            http://cea-hpc.github.io/clustershell/
Source0:        https://files.pythonhosted.org/packages/source/C/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3-%{name} = %{version}-%{release}
%if 0%{?rhel} >= 7 || 0%{?fedora}
Requires:       vim-filesystem
%else if 0%{?suse_version}
Requires:       vim
BuildRequires:  vim
%else
Requires:       vim-common
%endif
Provides:       vim-clustershell = %{version}-%{release}
Obsoletes:      vim-clustershell < 1.7.81-4

%description
ClusterShell is a set of tools and a Python library to execute commands
on cluster nodes in parallel depending on selected engine and worker
mechanisms. Advanced node sets and node groups handling methods are provided
to ease and improve the daily administration of large compute clusters or
server farms. Command line utilities like clush, clubak and nodeset (or
cluset) allow traditional shell scripts to take benefit of the features
offered by the library.


%package -n %{python3_pkgprefix}-%{name}
Summary:        ClusterShell module for Python 3
BuildRequires:  %{python3_pkgprefix}-devel
BuildRequires:  %{python3_pkgprefix}-setuptools
Requires:       %{python3_pkgprefix}-PyYAML
Requires:       %{python3_pkgprefix}-setuptools
%{?python_provide:%python_provide %{python3_pkgprefix}-%{srcname}}

%description -n %{python3_pkgprefix}-%{name}
ClusterShell Python 3 module and related command line tools.


%prep
%setup -q -n %{srcname}-%{version}

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install -O1 --skip-build --root %{buildroot}

pushd %{buildroot}%{_bindir}
for i in clubak cluset clush nodeset; do
  mv $i $i-%{python3_shortver}
done
popd

# move config dir away from default setuptools /usr prefix (if rpm-building as user)
[ -d %{buildroot}/usr/etc ] && mv %{buildroot}/usr/etc %{buildroot}/%{_sysconfdir}

%if 0%{?rhel} && 0%{?rhel} <= 6
# old versions of rpm (el5 and el6) requires that a file/link exists in buildroot
# even when ghosted, but it is not installed at the end...
ln -s conf/groups.d/local.cfg %{buildroot}/%{_sysconfdir}/clustershell/groups
%endif

# man pages
install -d %{buildroot}/%{_mandir}/{man1,man5}
install -p -m 0644 doc/man/man1/clubak.1 %{buildroot}/%{_mandir}/man1/
install -p -m 0644 doc/man/man1/cluset.1 %{buildroot}/%{_mandir}/man1/
install -p -m 0644 doc/man/man1/clush.1 %{buildroot}/%{_mandir}/man1/
install -p -m 0644 doc/man/man1/nodeset.1 %{buildroot}/%{_mandir}/man1/
install -p -m 0644 doc/man/man5/clush.conf.5 %{buildroot}/%{_mandir}/man5/
install -p -m 0644 doc/man/man5/groups.conf.5 %{buildroot}/%{_mandir}/man5/

# vim addons
%if 0%{?suse_version}
%define vimdatadir %{_datadir}/vim/site
%else
%define vimdatadir %{_datadir}/vim/vimfiles
%endif

install -d %{buildroot}/%{vimdatadir}/{ftdetect,syntax}
install -p -m 0644 doc/extras/vim/ftdetect/clustershell.vim %{buildroot}/%{vimdatadir}/ftdetect/
install -p -m 0644 doc/extras/vim/syntax/clushconf.vim %{buildroot}/%{vimdatadir}/syntax/
install -p -m 0644 doc/extras/vim/syntax/groupsconf.vim %{buildroot}/%{vimdatadir}/syntax/

%if 0%{?rhel}
%clean
rm -rf %{buildroot}
%endif

%files -n %{python3_pkgprefix}-%{name}
%if 0%{?rhel}
%defattr(-,root,root,-)
%endif
%{_bindir}/clubak-%{python3_shortver}
%{_bindir}/cluset-%{python3_shortver}
%{_bindir}/clush-%{python3_shortver}
%{_bindir}/nodeset-%{python3_shortver}
%{python3_sitelib}/ClusterShell/
%{python3_sitelib}/ClusterShell-*-py?.?.egg-info

%files
%if 0%{?rhel}
%defattr(-,root,root,-)
%endif
%doc ChangeLog COPYING.LGPLv2.1 README.md
%doc doc/examples
%doc doc/sphinx
%{_mandir}/man1/clubak.1*
%{_mandir}/man1/cluset.1*
%{_mandir}/man1/clush.1*
%{_mandir}/man1/nodeset.1*
%{_mandir}/man5/clush.conf.5*
%{_mandir}/man5/groups.conf.5*
%dir %{_sysconfdir}/clustershell
%dir %{_sysconfdir}/clustershell/groups.d
%dir %{_sysconfdir}/clustershell/groups.conf.d
%config(noreplace) %{_sysconfdir}/clustershell/clush.conf
%config(noreplace) %{_sysconfdir}/clustershell/groups.conf
%ghost %{_sysconfdir}/clustershell/groups
%config(noreplace) %{_sysconfdir}/clustershell/groups.d/local.cfg
%doc %{_sysconfdir}/clustershell/groups.conf.d/README
%doc %{_sysconfdir}/clustershell/groups.conf.d/*.conf.example
%doc %{_sysconfdir}/clustershell/groups.d/README
%doc %{_sysconfdir}/clustershell/groups.d/*.yaml.example
%doc %{_sysconfdir}/clustershell/topology.conf.example
%{vimdatadir}/ftdetect/clustershell.vim
%{vimdatadir}/syntax/clushconf.vim
%{vimdatadir}/syntax/groupsconf.vim

%changelog
* Fri Nov  2 2018 Stephane Thiell <sthiell@stanford.edu> 1.8.1-1
- update to 1.8.1

* Mon Oct 23 2017 Stephane Thiell <sthiell@stanford.edu> 1.8-1
- update to 1.8

* Sat Oct 14 2017 Stephane Thiell <sthiell@stanford.edu> 1.7.91-1
- update to 1.7.91 (1.8 RC1)

* Mon Oct  2 2017 Stephane Thiell <sthiell@stanford.edu> 1.7.82-1
- update to 1.7.82 (1.8 beta2)

* Sun Sep  3 2017 Stephane Thiell <sthiell@stanford.edu> 1.7.81-4
- move vim extensions into the clustershell package
- use Requires: vim-filesystem instead of vim-common
- define upgrade path for vim-clustershell

* Sat Sep  2 2017 Stephane Thiell <sthiell@stanford.edu> 1.7.81-3
- use `python2-` prefix in *Requires if available

* Sat Sep  2 2017 Stephane Thiell <sthiell@stanford.edu> 1.7.81-2
- create separate packages for python2 and python3 modules

* Fri Sep  1 2017 Stephane Thiell <sthiell@stanford.edu> 1.7.81-1
- update to 1.7.81 (1.8 beta1)

* Wed Dec 21 2016 Stephane Thiell <sthiell@stanford.edu> 1.7.3-1
- update to 1.7.3

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Mon Jun 20 2016 Stephane Thiell <sthiell@stanford.edu> 1.7.2-1
- update to 1.7.2

* Mon Feb 29 2016 Stephane Thiell <sthiell@stanford.edu> 1.7.1-1
- update to 1.7.1

* Tue Nov 10 2015 Stephane Thiell <sthiell@stanford.edu> 1.7-1
- update to 1.7

* Sat Jul 19 2014 Stephane Thiell <stephane.thiell@cea.fr> - 1.6-4
- Rebuilt for EPEL 7

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Apr 08 2012 Stephane Thiell <stephane.thiell@cea.fr> 1.6-1
- update to 1.6

* Thu Jun 09 2011 Stephane Thiell <stephane.thiell@cea.fr> 1.5.1-1
- update to 1.5.1

* Wed Jun 08 2011 Stephane Thiell <stephane.thiell@cea.fr> 1.5-1
- update to 1.5

* Sat Mar 19 2011 Stephane Thiell <stephane.thiell@cea.fr> 1.4.3-1
- update to 1.4.3

* Tue Mar 15 2011 Stephane Thiell <stephane.thiell@cea.fr> 1.4.2-1
- update to 1.4.2

* Sun Feb 13 2011 Stephane Thiell <stephane.thiell@cea.fr> 1.4.1-1
- update to 1.4.1

* Sat Jan 15 2011 Stephane Thiell <stephane.thiell@cea.fr> 1.4-1
- update to 1.4

* Wed Oct 20 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3.3-1
- update to 1.3.3

* Fri Sep 10 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3.2-1
- renamed Vim subpackage to vim-clustershell
- update to 1.3.2

* Sun Sep 05 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3.1-2
- added -vim subpackage for .vim files

* Fri Sep 03 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3.1-1
- removed -n from setup line
- own clustershell config directory for proper uninstall
- install vim syntax addons in vimfiles, thus avoiding vim version detection
- update to 1.3.1

* Sun Aug 22 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3-4
- fixed BuildRoot tag in accordance with EPEL guidelines
- python_sitelib definition: prefer global vs define
- preserve timestamps and fix permissions when installing files

* Sat Aug 21 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3-3
- use a full URL to the package in Source0

* Fri Aug 20 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3-2
- various improvements per first review request

* Thu Aug 19 2010 Stephane Thiell <stephane.thiell@cea.fr> 1.3-1
- initial build candidate for Fedora
