%define is_ubuntu %(grep -i ubuntu /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)
%define is_debian %(grep -i debian /etc/os-release >/dev/null; if test $? -gt 0; then echo 0; else echo 1; fi)

%if %is_ubuntu
  %define _unitdir /usr/lib/systemd/system
%endif
%if %is_debian
  %define _unitdir /usr/lib/systemd/system
%endif

Name:		conman
Version:	%{_software_version}
Release:  7%{?dist}

Summary:	ConMan: The Console Manager
Group:		Applications/System
License:	GPLv3+
URL:		https://dun.github.io/conman/
Source0:	https://github.com/dun/conman/releases/download/%{name}-%{version}/%{name}-%{version}.tar.xz

#BuildRequires:	freeipmi-devel >= 1.0.4
#BuildRequires:	tcp_wrappers-devel
#BuildRequires:	systemd
Requires:	expect, freeipmi
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
ConMan is a serial console management program designed to support a large
number of console devices and simultaneous users.

Supported console types:
- Local serial devices
- Remote terminal servers (via the telnet protocol)
- IPMI Serial-Over-LAN (via FreeIPMI's libipmiconsole)
- External processes (e.g., Expect)
- Unix domain sockets

Features:
- Mapping symbolic names to console devices
- Logging (and optionally timestamping) console output to file
- Connecting to a console in monitor (R/O) or interactive (R/W) mode
- Connecting to multiple consoles for broadcasting (W/O) client output
- Sharing a console session amongst multiple simultaneous clients
- Allowing clients to share or steal console "write" privileges
- Executing Expect scripts across multiple consoles in parallel

%prep
%setup -q

%build
%configure
make %{?_smp_mflags}

%install
rm -rf "%{buildroot}"
mkdir -p "%{buildroot}"
make install DESTDIR="%{buildroot}"
rm -f %{buildroot}/%{_sysconfdir}/init.d/conman
rm -f %{buildroot}/%{_sysconfdir}/default/conman
rm -f %{buildroot}/%{_sysconfdir}/sysconfig/conman

%clean
rm -rf "%{buildroot}"

%post
%systemd_post conman.service

%preun
%systemd_preun conman.service

%postun
%systemd_postun_with_restart conman.service

%files
%license COPYING
%doc AUTHORS
%doc DISCLAIMER.LLNS
%doc DISCLAIMER.UC
%doc FAQ
%doc NEWS
%doc README
%doc THANKS
%config(noreplace) %{_sysconfdir}/conman.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/conman
%{_bindir}/conman
%{_bindir}/conmen
%{_sbindir}/conmand
%{_datadir}/conman
%{_mandir}/man1/conman.1*
%{_mandir}/man5/conman.conf.5*
%{_mandir}/man8/conmand.8*
%{_unitdir}/conman.service
