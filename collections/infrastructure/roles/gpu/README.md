# GPU

## Description

This role installs NVIDIA or AMD GPU drivers, and optionally CUDA (NVIDIA) or ROCm (AMD).

Packages come from the vendors repositories (or local mirrors of them), which must be configured
before running the role, using the `repositories` role (see [Repositories](#repositories) below).

Supported distributions:

| Distribution | NVIDIA driver | CUDA | AMD driver | ROCm |
|--------------|---------------|------|------------|------|
| RHEL 9 | yes (open or proprietary kernel modules) | yes | yes | yes |
| RHEL 10 | yes (open kernel modules) | yes | yes | yes |
| Ubuntu 22.04, 24.04 | yes (open kernel modules) | yes | yes | yes |
| Ubuntu 26.04 | yes (open kernel modules) | yes | yes | no (not supported by AMD) |
| Debian 12, 13 | yes (open kernel modules) | yes | yes (Debian 13: Instinct MI300X and newer only) | same as driver |
| openSUSE Leap 15, 16 | yes (open kernel modules) | yes | no (not supported by AMD) | no |

When AMD is requested on a distribution AMD does not support, the role fails with an explicit message.

The role cannot be tested without GPUs: package names and repositories follow the vendors
documentations at the time of writing ([NVIDIA driver installation guide](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/index.html),
[AMD ROCm installation guide](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/),
[AMD GPU driver installation guide](https://instinct.docs.amd.com/projects/amdgpu-docs/en/latest/)).

## Instructions

Set `gpu_vendor` to `nvidia` or `amd`, usually in the hardware group (`hw_*`) of the GPU hosts.
If `gpu_vendor` is not set, the role does nothing.

The role installs the kernel headers and development packages of the running kernel (drivers are built
with DKMS), then the driver. A reboot is needed after the first driver installation: set
`gpu_reboot: true` to let the role reboot hosts when the driver was installed or updated.

### NVIDIA

```yaml
gpu_vendor: nvidia
gpu_nvidia_install_cuda: true   # Optional, also install the CUDA toolkit
gpu_reboot: true
```

NVIDIA provides two flavors of kernel modules:

* `open` (default): NVIDIA open kernel modules, for Turing and newer GPUs (T4, A100, H100, and later).
  This is the flavor documented by NVIDIA for all distributions.
* `proprietary`: needed for older GPUs (V100, P100, etc.). Only available on RHEL 8 and 9 (DNF module
  stream `nvidia-driver:latest-dkms`).

```yaml
gpu_nvidia_kernel_modules: proprietary
```

The role also enables `nvidia-persistenced`, and starts it once the driver is loaded.

### AMD

```yaml
gpu_vendor: amd
gpu_amd_install_rocm: true   # Default, set to false to install the driver only
gpu_reboot: true
```

Users running ROCm workloads must be members of the `render` and `video` groups.

## Repositories

The role does not configure repositories: they must be defined in `bb_repositories`, and configured
by the `repositories` role first. The examples below use the vendors public repositories; on clusters
without internet access, mirror these repositories on the management host (`dnf reposync
--download-metadata`, `apt-mirror`, etc.) and use the local URLs instead, keeping repositories
metadata as is (do not recreate it with `createrepo`, this would destroy NVIDIA DNF module streams).

Note that the format of `bb_repositories` entries depends on the distribution (see the `repositories`
role README). Versions in URLs are examples: use the versions matching your hardware.

### NVIDIA repositories

The NVIDIA repository URL is `https://developer.download.nvidia.com/compute/cuda/repos/<distribution>/x86_64/`
(`sbsa` instead of `x86_64` for arm64), with `<distribution>`:

| Distribution | `<distribution>` |
|--------------|------------------|
| RHEL 9, 10 | `rhel9`, `rhel10` |
| Ubuntu 22.04, 24.04, 26.04 | `ubuntu2204`, `ubuntu2404`, `ubuntu2604` |
| Debian 12, 13 | `debian12`, `debian13` |
| openSUSE Leap 15, 16 | `opensuse15`, `suse16` |

**RHEL 9/10.** The DKMS package comes from EPEL, which also needs the CodeReady Builder repository.
The GPG key file is listed at the root of the repository (`CDF6BA43.pub` for `rhel10` at the time of writing):

```yaml
bb_repositories:
  - name: cuda
    baseurl: https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64
    gpgcheck: true
    gpgkey: https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64/CDF6BA43.pub
  - name: epel
    baseurl: https://dl.fedoraproject.org/pub/epel/10/Everything/x86_64
```

**Ubuntu and Debian 12.** NVIDIA repositories are "flat" repositories (`/` instead of a suite and
components). The signing key is provided by NVIDIA `cuda-keyring` package
(`<repository URL>/cuda-keyring_1.1-1_all.deb`), installed as `/usr/share/keyrings/cuda-archive-keyring.gpg`:

```yaml
bb_repositories:
  - repo: deb [signed-by=/usr/share/keyrings/cuda-archive-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/ /
```

On Debian, the `contrib` component of Debian repositories must also be enabled.

**Debian 13** (deb822 format):

```yaml
bb_repositories:
  - name: cuda
    uris: https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64/
    suites: /
    signed_by: /usr/share/keyrings/cuda-archive-keyring.gpg
```

**openSUSE Leap:**

```yaml
bb_repositories:
  - name: cuda
    repo: https://developer.download.nvidia.com/compute/cuda/repos/suse16/x86_64/
```

### AMD repositories

AMD provides three repositories, signed with the key `https://repo.radeon.com/rocm/rocm.gpg.key`:

* `amdgpu`: the GPU kernel driver (`amdgpu-dkms`), with its own version numbers (for example `31.60`).
* `rocm` and `graphics`: ROCm, with ROCm version numbers (for example `7.2.4`).

Check [AMD compatibility matrix](https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html)
for the driver version matching a ROCm version.

**RHEL 9/10.** ROCm also needs EPEL and CodeReady Builder. For RHEL 9, the `graphics` repository
URL uses the minor version (`el/9.6`, `el/9.7`, etc.):

```yaml
bb_repositories:
  - name: amdgpu
    baseurl: https://repo.radeon.com/amdgpu/31.60/el/10/main/x86_64
    gpgcheck: true
    gpgkey: https://repo.radeon.com/rocm/rocm.gpg.key
  - name: rocm
    baseurl: https://repo.radeon.com/rocm/el10/7.2.4/main
    gpgcheck: true
    gpgkey: https://repo.radeon.com/rocm/rocm.gpg.key
  - name: amdgraphics
    baseurl: https://repo.radeon.com/graphics/7.2.4/el/10/main/x86_64
    gpgcheck: true
    gpgkey: https://repo.radeon.com/rocm/rocm.gpg.key
```

**Ubuntu 22.04/24.04/26.04 and Debian 12.** The key must be available as `/etc/apt/keyrings/rocm.gpg`
(dearmored `rocm.gpg.key`). Use the Ubuntu codename (`jammy`, `noble`, `resolute`); AMD documents the
`jammy` repositories for Debian 12. Ubuntu 26.04 only has the `amdgpu` repository (no ROCm):

```yaml
bb_repositories:
  - repo: deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/amdgpu/31.60/ubuntu noble main
  - repo: deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/7.2.4 noble main
  - repo: deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/graphics/7.2.4/ubuntu noble main
```

AMD also recommends pinning its packages (`/etc/apt/preferences.d/rocm-pin-600`), so they take
precedence over distribution packages of the same name:

```
Package: *
Pin: release o=repo.radeon.com
Pin-Priority: 600
```

**Debian 13** (deb822 format): AMD documents the Ubuntu `noble` repositories for Debian 13:

```yaml
bb_repositories:
  - name: amdgpu
    uris: https://repo.radeon.com/amdgpu/31.60/ubuntu
    suites: noble
    components: main
    signed_by: /etc/apt/keyrings/rocm.gpg
  - name: rocm
    uris: https://repo.radeon.com/rocm/apt/7.2.4
    suites: noble
    components: main
    signed_by: /etc/apt/keyrings/rocm.gpg
  - name: amdgraphics
    uris: https://repo.radeon.com/graphics/7.2.4/ubuntu
    suites: noble
    components: main
    signed_by: /etc/apt/keyrings/rocm.gpg
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `gpu_vendor` | not set | GPU vendor: `nvidia` or `amd`. Nothing is done if not set. |
| `gpu_nvidia_kernel_modules` | `open` | NVIDIA kernel modules: `open`, or `proprietary` (RHEL 8/9 only). |
| `gpu_nvidia_install_cuda` | `false` | Also install the CUDA toolkit (NVIDIA). |
| `gpu_amd_install_rocm` | `true` | Also install ROCm (AMD). |
| `gpu_reboot` | `false` | Reboot hosts after driver installation or update. |
| `gpu_reboot_timeout` | `600` | Reboot timeout, in seconds. |
| `gpu_enable_services` | `bb_enable_services`, else `true` | Enable `nvidia-persistenced` (NVIDIA). |
| `gpu_start_services` | `bb_start_services`, else `true` | Start `nvidia-persistenced` once the driver is loaded (NVIDIA). |
