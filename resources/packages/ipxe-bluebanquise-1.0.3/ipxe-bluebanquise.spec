Name:     ipxe-bluebanquise
Summary:  ipxe-bluebanquise
Release:  el8
Version:  1.0.3
License:  GPL
Group:    System Environment/Base
Source:   https://github.com/oxedions/bluebanquise/ipxe-bluebanquise-1.0.3.tar.gz
URL:      https://github.com/ipxe/ipxe
Packager: Oxedions <oxedions@gmail.com>


%define debug_package %{nil}

%description
iPXE roms or iso for the BlueBanquise stack
Grub2 auto EFI system image
%prep

%setup -q

%build

%install

# x86_64
mkdir -p $RPM_BUILD_ROOT/var/www/html/preboot_execution_environment/bin/x86_64
cp /root/build/bin/http/x86_64/grub2_efi_autofind.img $RPM_BUILD_ROOT/var/www/html/preboot_execution_environment/bin/x86_64/grub2_efi_autofind.img
cp /root/build/bin/http/x86_64/grub2_shell.img $RPM_BUILD_ROOT/var/www/html/preboot_execution_environment/bin/x86_64/grub2_shell.img
cp /root/build/bin/http/x86_64/ipxe_efi.iso $RPM_BUILD_ROOT/var/www/html/preboot_execution_environment/bin/x86_64/ipxe_efi.iso
cp /root/build/bin/http/x86_64/ipxe_legacy.iso $RPM_BUILD_ROOT/var/www/html/preboot_execution_environment/bin/x86_64/ipxe_legacy.iso
cp /root/build/bin/http/x86_64/ipxe.usb $RPM_BUILD_ROOT/var/www/html/preboot_execution_environment/bin/x86_64/ipxe.usb

mkdir -p $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64
cp /root/build/bin/tftp/x86_64/standard_ipxe.efi $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64/standard_ipxe.efi
cp /root/build/bin/tftp/x86_64/standard_undionly.kpxe $RPM_BUILD_ROOT/var/lib/tftpboot/x86_64/standard_undionly.kpxe

# arm64
# need a cpu

%files
%defattr(-,root,root,-)
/var/www/html/preboot_execution_environment/bin/x86_64/grub2_efi_autofind.img
/var/www/html/preboot_execution_environment/bin/x86_64/grub2_shell.img
/var/www/html/preboot_execution_environment/bin/x86_64/ipxe_efi.iso
/var/www/html/preboot_execution_environment/bin/x86_64/ipxe_legacy.iso
/var/www/html/preboot_execution_environment/bin/x86_64/ipxe.usb
/var/lib/tftpboot/x86_64/standard_ipxe.efi
/var/lib/tftpboot/x86_64/standard_undionly.kpxe


