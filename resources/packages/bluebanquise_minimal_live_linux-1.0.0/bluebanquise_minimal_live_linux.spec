Name:     bluebanquise_minimal_live_linux
Summary:  bluebanquise_minimal_live_linux
Release:  1%{?dist}
Version:  1.0.0
License:  GPL
Group:    System Environment/Base
Source:   https://github.com/oxedions/blue-banquise/bluebanquise_minimal_live_linux.tar.xz
URL:      https://github.com/
Packager: Oxedions <oxedions@gmail.com>


%define debug_package %{nil}

%description
Minimal Live Linux files for BlueBanquise
%prep

%setup -q

%build

%install

mkdir -p $RPM_BUILD_ROOT/var/www/html/preboot_execution_environment/bin/

cp 

#make -j 2 DEBUG=intel,dhcp

#make -j 2 bin-x86_64-efi/ipxe.efi DEBUG=intel,dhcp
#make -j 2 bin/undionly.kpxe DEBUG=intel,dhcp
#cp bin-x86_64-efi/ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/ipxe.efi
#cp bin/undionly.kpxe $RPM_BUILD_ROOT/var/lib/tftpboot/undionly.kpxe

make -j 2 bin-x86_64-efi/ipxe.efi EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
make -j 2 bin/undionly.kpxe EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
cp bin-x86_64-efi/ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/bluebanquise_standard_ipxe.efi
cp bin/undionly.kpxe $RPM_BUILD_ROOT/var/lib/tftpboot/bluebanquise_standard_undionly.kpxe

%files
%defattr(-,root,root,-)
/*


