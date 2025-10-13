


- **os_preserve_efi_first_boot_device**: Force grub to keep first entry in boot order (EFI systems). Available values: ``['true', 'false']``



IPXE settings
-------------

This is very specific, and you should be good to go without setting these parameters.

However, it happens that on some networks or for some specific hardware, you will need to tune IPXE settings to make PXE boot work properly.

There are 3 settings to manipulate the rom to be used.

* ``hw_ipxe_driver``: set ipxe driver to use. Available values: ``['default', 'snp', 'snponly']``. If not set, default will be snponly.
* ``hw_ipxe_platform``: set ipxe platform if need to be forced. Available values: ``['pcbios', 'efi']``. If not set, system will auto-detect platform.
* ``hw_ipxe_embed``: set ipxe embed BlueBanquise script. Available values: ``['standard', 'dhcpretry']``. If not set, default will be dhcpretry.
