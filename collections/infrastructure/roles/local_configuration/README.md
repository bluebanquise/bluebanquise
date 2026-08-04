# local_configuration

## Description

This role consolidates all local host configuration tasks into a single unified role. It covers:

- **Hostname** — sets the static hostname (always applied)
- **Security** — access control (SELinux / AppArmor), root/sudo password, sudoers
- **System** — kernel parameters, sysctl, kernel version lock, kernel modules, PAM limits, cron jobs, packages, services, files, folders, templates, lineinfile
- **Storage** — partitioning, LVM, filesystems, mount points

Each of the three configuration sections (security, system, storage) is activated only when its corresponding dict variable is defined in inventory. Within each section, subtasks are also individually conditional: only the subtasks whose variables are defined are executed, keeping playbook runs fast.

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## Instructions

### Hostname

The hostname task always runs. By default an FQDN hostname is set using `inventory_hostname` and the domain name.

```yaml
local_configuration_hostname_fqdn: true        # set FQDN hostname (default: true)
local_configuration_hostname_domain_name:      # overrides bb_domain_name if set
```

The FQDN is built as `inventory_hostname + '.' + domain`, where the domain falls back to
`bb_domain_name`, then to `cluster.local`.

Set `local_configuration_hostname_fqdn: false` to use a plain (non-FQDN) hostname.

> **Note:** Setting the hostname identifies the host. Do not use this role when building a diskless golden image.

---

### Security (`local_configuration_security`)

The security subtasks run when `local_configuration_security` is defined **or** when
`os_access_control` **or** `os_admin_password_sha512` is defined (global BlueBanquise
equipment-profile variables).

#### Access control

Ensures the host access control status complies with the configured state. Uses SELinux on
RedHat family systems and AppArmor on Ubuntu, Debian, and Suse family systems.

The effective state is resolved in this order of precedence:
1. `local_configuration_security.access_control`
2. `os_access_control` (global equipment-profile variable)
3. `local_configuration_access_control_os_access_control` (default: `enforcing`)

Accepted values:

| Value | RedHat (SELinux) | Debian / Ubuntu / Suse (AppArmor) |
|---|---|---|
| `enforcing` | SELinux enforcing | AppArmor started, all profiles enforced |
| `permissive` or `complain` | SELinux permissive | AppArmor started, all profiles set to complain |
| `disabled` | SELinux disabled | AppArmor stopped and disabled |

Example — set per equipment profile using the global variable:

```yaml
os_access_control: enforcing
```

Example — set inside the role dict (takes precedence over `os_access_control`):

```yaml
local_configuration_security:
  access_control: permissive
```

#### Root / sudo password

Sets the password for the root user or for the configured sudo user.

The effective password is resolved in this order of precedence:
1. `local_configuration_security.admin_password_sha512`
2. `os_admin_password_sha512` (global equipment-profile variable)

By default the password is applied to the sudo user (`bluebanquise`), not root.
To apply it directly to root set `local_configuration_root_password_enable_root: true`.

```yaml
local_configuration_root_password_enable_root: false   # default
local_configuration_root_password_sudo_user: bluebanquise  # default
```

To generate a SHA-512 password hash (Python ≥ 3.3):

```
python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'
```

Example — set per equipment profile using the global variable:

```yaml
os_admin_password_sha512: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
```

Example — set inside the role dict (takes precedence over `os_admin_password_sha512`):

```yaml
local_configuration_security:
  admin_password_sha512: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
```

No default value is provided for security reasons.

#### Sudoers

Manages sudoers entries. Acts as a wrapper around the
[community.general.sudoers](https://docs.ansible.com/ansible/latest/collections/community/general/sudoers_module.html)
module. The `name` key is mandatory for each entry.

```yaml
local_configuration_security:
  sudoers:
    # Grant 'manu' passwordless sudo for all commands
    - name: manu
      user: manu
      nopassword: true
      commands: ALL
    # Grant 'techs' group passwordless sudo for a single command
    - name: techs_group
      group: techs
      commands: /usr/local/bin/backup
  sudoers_logging: false   # set to true to enable sudo logging (default: false)
```

See the [community.general.sudoers module documentation](https://docs.ansible.com/ansible/latest/collections/community/general/sudoers_module.html)
for the full list of available parameters.

---

### System (`local_configuration_system`)

The system subtasks run when `local_configuration_system` is defined **or** when any of the
following global variables is defined: `os_kernel_parameters`, `hw_kernel_parameters`,
`os_sysctl`.

#### Kernel command line parameters

Applies kernel command line parameters to the default kernel entry.

The effective values are resolved in this order of precedence:
1. `local_configuration_system.kernel_parameters` / `local_configuration_system.hw_kernel_parameters`
2. `os_kernel_parameters` / `hw_kernel_parameters` (global equipment-profile / hardware variables)

On **RHEL**, `grubby` is used to add parameters to the default kernel. Parameters already
present are skipped (idempotent).

On **Ubuntu, Debian, and OpenSuse**, parameters are merged into `GRUB_CMDLINE_LINUX_DEFAULT`
in `/etc/default/grub`, deduplicated, sorted, and the appropriate grub update command is run.

`hw_console` (global hardware variable) is also merged into the grub command line on
non-RHEL systems when defined.

Example — using global variables (typical equipment-profile / hardware group_vars):

```yaml
os_kernel_parameters: "quiet splash"
hw_kernel_parameters: "iommu=pt intel_iommu=on"
hw_console: "console=tty0 console=ttyS0,115200n8"
```

Example — using the role dict (takes precedence over global variables):

```yaml
local_configuration_system:
  kernel_parameters: "quiet splash"
  hw_kernel_parameters: "iommu=pt intel_iommu=on"
```

#### sysctl

Applies sysctl parameters. The effective value is resolved in this order of precedence:
1. `local_configuration_system.sysctl`
2. `os_sysctl` (global equipment-profile variable)

```yaml
local_configuration_system:
  sysctl:
    kernel.panic: 10
    vm.swappiness: 5
```

To prevent sysctl reload after applying changes:

```yaml
local_configuration_kernel_config_sysctl_reload: false
```

#### Kernel version lock

Pins the running kernel to a specific version and prevents package managers from upgrading
it away, using `dnf versionlock` on RHEL family systems and `apt-mark hold` on Debian and
Ubuntu. **Not supported on OpenSuse** — the role fails with a clear message if
`os_kernel_version` is set on a Suse family host.

The effective values are resolved in this order of precedence:
1. `local_configuration_system.kernel_version` / `local_configuration_system.kernel_version_allow_reboot`
2. `os_kernel_version` / `os_kernel_version_allow_reboot` (global equipment-profile variables)

```yaml
os_kernel_version: "5.14.0-427.24.1.el9_4.x86_64"   # exact `uname -r` value
os_kernel_version_allow_reboot: false               # default: false
```

`os_kernel_version` must be the **exact `uname -r` string** for the target kernel (e.g.
`5.14.0-427.24.1.el9_4.x86_64` on RHEL, `6.8.0-31-generic` on Ubuntu, `6.1.0-21-amd64` on
Debian). This is the same format `ansible_facts.kernel` reports and the same format the
`cluster_management` role's dynamic state daemon gathers via `uname -r` (formerly the separate
`cluster_state` role) — see the "Cluster state" note below.

On each run:
1. The running kernel (`ansible_facts.kernel`) is compared to `os_kernel_version`.
2. **If it already matches**, no package is installed and no reboot happens — the role only
   (re)applies the lock, so a missing or stale lock is repaired even when the version is
   already correct.
3. **If it does not match**, the existing lock/hold on the kernel family is removed, the
   target version is installed, the bootloader default entry is switched to it, and the lock
   is re-applied.
4. A reboot is triggered **only** when a version change actually happened **and**
   `os_kernel_version_allow_reboot: true`. With the default `false`, the new kernel is
   installed and locked but the host keeps running on the old one until rebooted manually
   (or by another mechanism, e.g. a maintenance-window playbook).

**RHEL family**: the whole installed kernel package family is discovered dynamically
(`kernel`, `kernel-core`, `kernel-modules`, `kernel-modules-core`, `kernel-modules-extra` —
whichever are present) and locked/installed together at the target version-release, so
`dnf update` cannot drift `kernel-core` and `kernel-modules` to different versions. The
bootloader default is set directly via `grubby --set-default=/boot/vmlinuz-<version>`.

**Debian / Ubuntu**: the versioned packages currently installed for the running kernel
(`linux-image-<version>`, `linux-headers-<version>`, `linux-modules-<version>`, etc. —
whichever are present) are discovered, renamed to the target version, and installed. The
rolling meta-packages (`linux-image-generic` on Ubuntu, `linux-image-amd64` on Debian, etc.
— see `local_configuration_kernel_version_meta_packages`) are held too: holding only the
versioned package is not enough, since `apt upgrade` can still pull a newer kernel through
the meta-package's own dependency. The bootloader default is switched by setting
`GRUB_DEFAULT=saved` and pointing `grub-set-default` at the target kernel's GRUB menu entry
id (parsed out of the regenerated `grub.cfg`).

```yaml
local_configuration_kernel_version_meta_packages:   # override per OS family as needed
  - linux-image-generic     # Ubuntu default
  - linux-headers-generic
  - linux-generic
  - linux-modules-extra-generic
```

> **Known limitation:** the default Debian meta-package names (`linux-image-amd64`,
> `linux-headers-amd64`) assume x86_64. On arm64 Debian hosts, override
> `local_configuration_kernel_version_meta_packages` to the `-arm64` equivalents — it cannot
> be derived automatically from `ansible_facts.architecture` (`aarch64`), which does not
> match Debian's own arch naming (`arm64`).

**Cluster state**: when `os_kernel_version` is set, the `cluster_management` role writes it to
`static_cluster_state.yml` under the `kernel` key — the same key its dynamic state daemon
already populates in `dynamic_cluster_state.yml` from a live `uname -r`, so
`bluebanquise-cluster state` diffs expected vs actual kernel version for free.

#### Kernel modules (modprobe)

Loads or unloads kernel modules. Wrapper around the
[community.general.modprobe](https://docs.ansible.com/ansible/latest/collections/community/general/modprobe_module.html)
module.

```yaml
local_configuration_system:
  modprobe:
    - name: 8021q
      state: present
    - name: dummy
      state: present
      params: 'numdummies=2'
```

#### PAM limits

Sets custom PAM limits (ulimit). Wrapper around the
[community.general.pam_limits](https://docs.ansible.com/ansible/latest/collections/community/general/pam_limits_module.html)
module.

```yaml
local_configuration_system:
  pam_limits:
    - domain: joe
      limit_type: soft
      limit_item: nofile
      value: 64000
    - domain: smith
      limit_type: hard
      limit_item: fsize
      value: 1000000
      use_max: true
    - domain: james
      limit_type: '-'
      limit_item: memlock
      value: unlimited
      comment: unlimited memory lock for james
```

#### Cron jobs

Manages cron jobs. Wrapper around the
[ansible.builtin.cron](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/cron_module.html)
module.

```yaml
local_configuration_system:
  cron_jobs:
    - name: "check dirs"
      minute: "0"
      hour: "5,2"
      job: "ls -alh > /dev/null"
    - name: yum autoupdate
      weekday: "2"
      minute: "0"
      hour: "12"
      user: root
      job: "YUMINTERACTIVE=0 /usr/sbin/yum-autoupdate"
      cron_file: ansible_yum-autoupdate
```

#### Packages

Installs or removes packages. Each entry can be a plain package name string or a dict with
`name`, `state`, and optionally `use` keys.

```yaml
local_configuration_system:
  packages:
    - htop
    - vim
    - name: "{{ apache }}"
      state: absent
    - name: openmpi
      state: present
```

#### Services

Manages service state and enablement. Wrapper around the
[ansible.builtin.service](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html)
module.

```yaml
local_configuration_system:
  services:
    - name: httpd
      state: started
      enabled: true
    - name: network
      state: restarted
      arguments: eth0
```

#### Folders

Creates or manages directories. Wrapper around
[ansible.builtin.file](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html).
`state` defaults to `directory` if not specified.

```yaml
local_configuration_system:
  folders:
    - path: /etc/some_directory
      mode: '0755'
    - path: /opt/myapp
      owner: myapp
      group: myapp
      mode: '0750'
```

#### Files

Creates, removes, or modifies files and symlinks. Wrapper around
[ansible.builtin.file](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html).

```yaml
local_configuration_system:
  files:
    - path: /etc/foo.conf
      owner: foo
      group: foo
      mode: '0644'
      state: touch
    - src: /file/to/link/to
      path: /path/to/symlink
      state: link
```

#### Templates

Renders inline templates to files on the target host. The `template` key holds the Jinja2
template content; all other keys map to
[ansible.builtin.template](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html)
parameters.

```yaml
local_configuration_system:
  templates:
    - template: |
        This is a template to render
        {% for stuff in customlist %}
           {{ stuff }}
        {% endfor %}
      dest: /etc/file.conf
      owner: bin
      group: wheel
      mode: '0644'
```

#### Lineinfile

Edits lines in files. Wrapper around
[ansible.builtin.lineinfile](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html).

```yaml
local_configuration_system:
  lineinfile:
    - path: /etc/selinux/config
      regexp: '^SELINUX='
      line: SELINUX=enforcing
    - path: /etc/hosts
      regexp: '^127\.0\.0\.1'
      line: 127.0.0.1 localhost
      owner: root
      group: root
      mode: '0644'
```

---

### Storage (`local_configuration_storage`)

The storage subtasks run when `local_configuration_storage` is defined. Subtasks execute
in dependency order: **parted → lvm → filesystem → mount**.

#### Partitioning (parted)

Creates or removes disk partitions. Wrapper around the
[community.general.parted](https://docs.ansible.com/ansible/latest/collections/community/general/parted_module.html)
module.

```yaml
local_configuration_storage:
  parted:
    # Create a new primary partition for LVM
    - device: /dev/sdb
      number: 1
      flags: [ lvm ]
      state: present
    # Create a new ext4 primary partition
    - device: /dev/sdc
      number: 1
      state: present
      fs_type: ext4
    # Remove a partition
    - device: /dev/sdd
      number: 1
      state: absent
```

#### LVM

Configures LVM Physical Volumes, Volume Groups, and Logical Volumes. Uses the
[community.general.lvg](https://docs.ansible.com/ansible/latest/collections/community/general/lvg_module.html)
and
[community.general.lvol](https://docs.ansible.com/ansible/latest/collections/community/general/lvol_module.html)
modules.

```
  +---------+
  |   pv1   +-----+
  +---------+     |                         +---------+
                  |                    +--->+   lv1   |
                  |                    |    +---------+
  +---------+     |    +---------+     |
  |   pv2   +--------->+   vg1   +-----+
  +---------+     |    +---------+     |
                  |                    |    +---------+
                  |                    +--->+   lv2   |
  +---------+     |                         +---------+
  |   pv3   +-----+
  +---------+
```

```yaml
local_configuration_storage:
  lvm:
    vgs:
      - vg: data
        pvs:
          - /dev/sdb
          - /dev/sdc
      - vg: colors
        pvs:
          - /dev/sde
    lvs:
      - lv: data_lv
        size: 10G
        vg: data
      - lv: blue
        size: 100M
        vg: colors
      # Mirrored logical volume
      - lv: mirror_lv
        size: 200M
        vg: data
        opts: -m 1
```

All options from `lvg` (at `vgs` level) and `lvol` (at `lvs` level) are supported.

#### Filesystems

Creates filesystems on block devices. Wrapper around the
[community.general.filesystem](https://docs.ansible.com/ansible/latest/collections/community/general/filesystem_module.html)
module.

```yaml
local_configuration_storage:
  filesystem:
    - fstype: ext4
      dev: /dev/data/data_lv
    - fstype: xfs
      dev: /dev/sdc1
      opts: -f
    - dev: /dev/sdd1
      state: absent
```

#### Mount points

Manages mount points and `/etc/fstab` entries. Wrapper around the
[ansible.posix.mount](https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html)
module.

```yaml
local_configuration_storage:
  mount:
    # Mount a local filesystem
    - path: /data
      src: /dev/data/data_lv
      fstype: ext4
      state: mounted
    # Mount DVD read-only
    - path: /mnt/dvd
      src: /dev/sr0
      fstype: iso9660
      opts: ro,noauto
      state: present
    # Bind mount
    - path: /system/new_volume/boot
      src: /boot
      opts: bind
      state: mounted
      fstype: none
    # NFS mount
    - src: 192.168.1.100:/nfs/ssd/shared_data
      path: /mnt/shared_data
      opts: rw,sync,hard,intr
      state: mounted
      fstype: nfs
```

---

## Complete inventory example

```yaml
# Hostname
local_configuration_hostname_fqdn: true
local_configuration_hostname_domain_name: hpc.example.com

local_configuration_security:
  access_control: enforcing
  admin_password_sha512: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
  sudoers:
    - name: manu
      user: manu
      nopassword: true
      commands: ALL

local_configuration_system:
  kernel_parameters: "quiet splash"
  kernel_version: "5.14.0-427.24.1.el9_4.x86_64"
  kernel_version_allow_reboot: false
  sysctl:
    vm.swappiness: 5
    kernel.panic: 10
  modprobe:
    - name: 8021q
      state: present
  pam_limits:
    - domain: '*'
      limit_type: hard
      limit_item: nofile
      value: 65536
  cron_jobs:
    - name: backup
      minute: "0"
      hour: "2"
      job: /usr/local/bin/backup.sh
  packages:
    - htop
    - vim
  services:
    - name: chronyd
      state: started
      enabled: true
  folders:
    - path: /opt/myapp
      mode: '0755'
  lineinfile:
    - path: /etc/ssh/sshd_config
      regexp: '^#?PermitRootLogin'
      line: 'PermitRootLogin no'

local_configuration_storage:
  parted:
    - device: /dev/sdb
      number: 1
      flags: [ lvm ]
      state: present
  lvm:
    vgs:
      - vg: data
        pvs:
          - /dev/sdb1
    lvs:
      - lv: data_lv
        size: 100%FREE
        vg: data
  filesystem:
    - fstype: ext4
      dev: /dev/data/data_lv
  mount:
    - path: /data
      src: /dev/data/data_lv
      fstype: ext4
      state: mounted
```
