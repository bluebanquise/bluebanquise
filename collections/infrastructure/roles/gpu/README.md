# GPU

## Description

These settings install GPU-related drivers and tools.

Supported distributions: RHEL 9/10. Ubuntu, Debian, and OpenSuse support is not yet implemented.

## Instructions

Set `gpu_vendor` to the target vendor:

* `nvidia`
* `amd`

Refer to each vendor section below for details.

### Variables

| Variable | Default | Description |
|---|---|---|
| `gpu_vendor` | | GPU vendor: `nvidia` or `amd` |
| `gpu_nvidia_install_cuda` | `false` | Also install CUDA (Nvidia only) |
| `gpu_reboot` | `false` | Reboot host after AMD driver install if packages changed |
| `gpu_reboot_timeout` | `600` | Reboot timeout in seconds (AMD only) |

### Nvidia

These settings install Nvidia drivers using the `@nvidia-driver:latest-dkms` module group and optionally CUDA.

Nvidia packages must be available in a configured repository on the hosts. Beware not to recreate repodata with `createrepo` on Nvidia's repository - this will destroy the package groups.

You can download drivers at https://www.nvidia.com/Download/index.aspx?lang=en-us and CUDA at https://developer.nvidia.com/cuda-downloads.

Ensure the driver and CUDA toolkit versions are compatible before adding them to your repositories.

Set `gpu_nvidia_install_cuda: true` to also install CUDA:

```yaml
gpu_vendor: nvidia
gpu_nvidia_install_cuda: true
```

### AMD

These settings install `amdgpu-dkms` and `rocm` packages and optionally reboots the host.

AMD packages must be available in a configured repository on the hosts. Compatible repository URLs:

- amdgpu: `https://repo.radeon.com/amdgpu/<VERSION>/el/el9/main/x86_64`
- rocm: `https://repo.radeon.com/rocm/el9/<VERSION>/main/`

Use the same `<VERSION>` for both repositories.

To mirror these repositories to a local server, use `dnf reposync`. First install `yum-utils` and create temporary repo files:

```bash
dnf install -y yum-utils
```

```ini
# /etc/yum.repos.d/amdgpu-tmp.repo
[amdgpu]
name=AMDGPU repository
baseurl=https://repo.radeon.com/amdgpu/6.3.3/el/el9/main/x86_64
enabled=0
gpgcheck=0
```

```ini
# /etc/yum.repos.d/rocm-tmp.repo
[rocm]
name=ROCm repository
baseurl=https://repo.radeon.com/rocm/el9/6.3.3/main/
enabled=0
gpgcheck=0
```

Then sync both repositories, keeping the original metadata:

```bash
dnf reposync --repoid amdgpu --download-metadata
dnf reposync --repoid rocm --download-metadata
```

Remove the temporary repo files afterward and upload the synced directories to your local HTTP repository server.

To trigger a reboot after driver installation (recommended for first install):

```yaml
gpu_vendor: amd
gpu_reboot: true
gpu_reboot_timeout: 600
```

Apply the `repositories` role first to ensure the AMD repository is available on target hosts before running these settings.
