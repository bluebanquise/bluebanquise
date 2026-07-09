# kernel_config

## Description

These settings apply and updates kernel parameters and sysctl parameters.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

### Kernel command line parameters

These settings read `os_kernel_parameters` and `hw_kernel_parameters` inventory variables and applies them to the kernel command line.

On **RHEL**, these settings use `grubby` to add parameters to the default kernel entry. Parameters are only added if not already present.

On **Ubuntu, Debian, and OpenSuse**, these settings merge parameters into `GRUB_CMDLINE_LINUX_DEFAULT` in `/etc/default/grub`, deduplicates them, and runs the appropriate grub update command.

Example inventory variables (typically set in `os_*` or `hw_*` group_vars):

```yaml
os_kernel_parameters: "quiet splash"
hw_kernel_parameters: "iommu=pt intel_iommu=on"
hw_console: "console=tty0 console=ttyS0,115200n8"
```

### sysctl

Sysctl parameters are defined in the `os_sysctl` variable. As an `os_*` variable, it should be set per equipment profile, not at host level.

```yaml
os_sysctl:
  kernel.panic: 10
  vm.swappiness: 5
```

To prevent sysctl reload after applying changes, set:

```yaml
kernel_config_sysctl_reload: false
```
