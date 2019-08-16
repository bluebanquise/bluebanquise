Name:     bluebanquise_ipxe
Summary:  bluebanquise_ipxe
Release:  1%{?dist}
Version:  1.0.1
License:  GPL
Group:    System Environment/Base
Source:   https://github.com/oxedions/blue-banquise/bluebanquise_ipxe-1.0.1.tar.gz
URL:      https://github.com/ipxe/ipxe
Packager: Oxedions <oxedions@gmail.com>


%define debug_package %{nil}

%description
iPXE roms or iso for the BlueBanquise stack
%prep

%setup -q

%build

%install

mkdir ipxe
git clone https://github.com/ipxe/ipxe.git ipxe/.

cp bluebanquise_standard.ipxe ipxe/src/bluebanquise_standard.ipxe

cd ipxe/src

sed -i 's/#undef\	DOWNLOAD_PROTO_HTTPS/#define\	DOWNLOAD_PROTO_HTTPS/g' config/general.h
sed -i 's/\/\/#define\	CONSOLE_FRAMEBUFFER/#define\  CONSOLE_FRAMEBUFFER/g' config/console.h

mkdir -p $RPM_BUILD_ROOT/var/lib/tftpboot/
#make -j 2 DEBUG=intel,dhcp

#make -j 2 bin-x86_64-efi/ipxe.efi DEBUG=intel,dhcp
#make -j 2 bin/undionly.kpxe DEBUG=intel,dhcp
#cp bin-x86_64-efi/ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/ipxe.efi
#cp bin/undionly.kpxe $RPM_BUILD_ROOT/var/lib/tftpboot/undionly.kpxe

make -j 2 bin-x86_64-efi/ipxe.efi EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
make -j 2 bin/undionly.kpxe EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp,vesafb
cp bin-x86_64-efi/ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/bluebanquise_standard_ipxe.efi
cp bin/undionly.kpxe $RPM_BUILD_ROOT/var/lib/tftpboot/bluebanquise_standard_undionly.kpxe

# Need to install syslinux-nonlinux syslinux-tftpboot syslinux
make -j 2 EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp bin/ipxe.iso
make -j 2 EMBED=bluebanquise_standard.ipxe DEBUG=intel,dhcp bin/ipxe.usb
cp bin/ipxe.iso $RPM_BUILD_ROOT/var/lib/tftpboot/ipxe.iso
cp bin/ipxe.usb $RPM_BUILD_ROOT/var/lib/tftpboot/ipxe.usb

%files
%defattr(-,root,root,-)
/*


