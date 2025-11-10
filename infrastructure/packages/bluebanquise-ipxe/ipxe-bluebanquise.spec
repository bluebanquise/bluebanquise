Name:     ipxe-bluebanquise
Summary:  ipxe-bluebanquise
Release:  1%{dist}
Version:  1.0.5
License:  MIT and GPL
Group:    System Environment/Base
Source:   https://github.com/oxedions/bluebanquise/ipxe-bluebanquise-1.0.5.tar.gz
URL:      https://github.com/oxedions/
Packager: Oxedions <oxedions@gmail.com>


%define debug_package %{nil}

%description
License:
 - iPXE source code is under GPL license (http://ipxe.org/)
 - BlueBanquise source code is under MIT license (https://github.com/oxedions/bluebanquise)

Description:
 - iPXE roms/iso/usb_image for the BlueBanquise stack
 - Grub2 auto EFI/shell system image

%prep

%setup -q

%build

%install

# x86_64
mkdir -p $RPM_BUILD_ROOT/var/www/html/pxe/bin/x86_64
cp /root/build/bin/http/x86_64/grub2_efi_autofind.img $RPM_BUILD_ROOT/var/www/html/pxe/bin/x86_64/grub2_efi_autofind.img
cp /root/build/bin/http/x86_64/grub2_shell.img $RPM_BUILD_ROOT/var/www/html/pxe/bin/x86_64/grub2_shell.img
cp /root/build/bin/http/x86_64/ipxe_efi.iso $RPM_BUILD_ROOT/var/www/html/pxe/bin/x86_64/ipxe_efi.iso
cp /root/build/bin/http/x86_64/ipxe_legacy.iso $RPM_BUILD_ROOT/var/www/html/pxe/bin/x86_64/ipxe_legacy.iso
cp /root/build/bin/http/x86_64/ipxe.usb $RPM_BUILD_ROOT/var/www/html/pxe/bin/x86_64/ipxe.usb

mkdir -p $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64
cp /root/build/bin/tftp/x86_64/standard_ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64/standard_ipxe.efi
cp /root/build/bin/tftp/x86_64/standard_undionly.kpxe $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64/standard_undionly.kpxe
cp /root/build/bin/tftp/x86_64/standard_snponly_ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64/standard_snponly_ipxe.efi
cp /root/build/bin/tftp/x86_64/standard_snp_ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64/standard_snp_ipxe.efi

# arm64
mkdir -p $RPM_BUILD_ROOT/var/lib/tftpboot/arm64
cp /root/build/bin/tftp/arm64/standard_ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/arm64/standard_ipxe.efi
cp /root/build/bin/tftp/arm64/standard_snponly_ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/arm64/standard_snponly_ipxe.efi
cp /root/build/bin/tftp/arm64/standard_snp_ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/arm64/standard_snp_ipxe.efi


%files
%defattr(-,root,root,-)
/var/www/html/pxe/bin/x86_64/grub2_efi_autofind.img
/var/www/html/pxe/bin/x86_64/grub2_shell.img
/var/www/html/pxe/bin/x86_64/ipxe_efi.iso
/var/www/html/pxe/bin/x86_64/ipxe_legacy.iso
/var/www/html/pxe/bin/x86_64/ipxe.usb
/var/lib/tftpboot/x86_64/standard_ipxe.efi
/var/lib/tftpboot/x86_64/standard_undionly.kpxe
/var/lib/tftpboot/x86_64/standard_snponly_ipxe.efi
/var/lib/tftpboot/x86_64/standard_snp_ipxe.efi
/var/lib/tftpboot/arm64/standard_ipxe.efi
/var/lib/tftpboot/arm64/standard_snponly_ipxe.efi
/var/lib/tftpboot/arm64/standard_snp_ipxe.efi


