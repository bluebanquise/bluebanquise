%define name python3-lxml
%define version 4.2.6
%define unmangled_version 4.2.6
%define unmangled_version 4.2.6
%define release 1

Summary: Powerful and Pythonic XML processing library combining libxml2/libxslt with the ElementTree API.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: BSD
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Vendor: lxml dev team <lxml-dev@lxml.de>
Url: http://lxml.de/

Requires: libxml2
Requires: libxslt

%description
lxml is a Pythonic, mature binding for the libxml2 and libxslt libraries.  It
provides safe and convenient access to these libraries using the ElementTree
API.

It extends the ElementTree API significantly to offer support for XPath,
RelaxNG, XML Schema, XSLT, C14N and much more.

To contact the project, go to the `project home page
<http://lxml.de/>`_ or see our bug tracker at
https://launchpad.net/lxml

In case you want to use the current in-development version of lxml,
you can get it from the github repository at
https://github.com/lxml/lxml .  Note that this requires Cython to
build the sources, see the build instructions on the project home
page.  To the same end, running ``easy_install lxml==dev`` will
install lxml from
https://github.com/lxml/lxml/tarball/master#egg=lxml-dev if you have
an appropriate version of Cython installed.


After an official release of a new stable series, bug fixes may become
available at
https://github.com/lxml/lxml/tree/lxml-4.2 .
Running ``easy_install lxml==4.2bugfix`` will install
the unreleased branch state from
https://github.com/lxml/lxml/tarball/lxml-4.2#egg=lxml-4.2bugfix
as soon as a maintenance branch has been established.  Note that this
requires Cython to be installed at an appropriate version for the build.

4.2.6 (2019-01-02)
==================

Bugs fixed
----------

* LP#1799755: Fix a DeprecationWarning in Py3.7+.

* Import warnings in Python 3.6+ were resolved.




%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
env CFLAGS="$RPM_OPT_FLAGS" python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
