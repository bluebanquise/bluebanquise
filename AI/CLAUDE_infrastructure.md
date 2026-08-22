# CLAUDE_infrastructure.md

Context for working in the `infrastructure` repository that lives alongside `bluebanquise/`.
The infrastructure repo is at `/claude/infrastructure/` (sibling of `/claude/bluebanquise/`).

---

## What the infrastructure repo is

It contains tooling to validate BlueBanquise end-to-end on real (KVM) VMs.
The active work lives in `Validation/steps_v3/` (the older `steps/` and `steps_v2/` are legacy; ignore them).

---

## Validation V3 — purpose

For each of the four supported distributions (rhel9, rhel10, ubuntu24, debian13) in sequence:

1. PXE-deploy a cluster management VM from the permanent `mgt1` Ubuntu 24.04 bootstrap host.
2. Install BlueBanquise on the cluster management VM from a configurable GitHub branch.
3. Deploy a full cluster stack on the management VM (repositories, set_hostname, http_server, nic, hosts_file, dhcp_server, dns_server, clustershell, pxe_stack, time server, firewall, NFS server, Slurm controller, users).
4. Have the management VM PXE-deploy `login1`, `c001`, `c002`.
5. Configure each cluster node via Ansible from the management VM.
6. Create `testuser` (uid/gid 1500) and run `srun --nodes=2 --ntasks-per-node=1 hostname` from `login1` as `testuser`.
7. Destroy all cluster VMs. Move to the next distribution.

---

## Network topology

```
Internet
   │
   virbr0 (libvirt default, 192.168.122.0/24, DHCP managed by libvirt)
   │
  mgt1 (permanent Ubuntu 24.04, MAC 52:54:00:fa:12:01 on virbr0)
   │ enp1s0 = virbr0  │  enp2s0 = virbr1 (10.10.0.1)
   │
   virbr1 (private_network, bridge virbr1, no DHCP — mgt1 BlueBanquise provides DHCP)
   │
  mgmt_<distro> (10.10.0.21–24, MAC on virbr1 per common.sh)
   │ enp1s0 = virbr1  │  enp2s0 = virbr2 (10.20.0.1)
   │
   virbr2 (cluster_network, bridge virbr2, no DHCP — mgmt VM BlueBanquise provides DHCP)
   │
  login1 (10.20.0.2) / c001 (10.20.0.3) / c002 (10.20.0.4)
```

**Double-NAT gateway chain:**
- Cluster nodes → mgmt VM masquerades (10.20.0.0/16 → enp1s0) → virbr1
- virbr1 → mgt1 masquerades (10.10.0.0/16 → enp1s0) → virbr0 → internet

Both masquerade rules are set up in bash (`iptables -t nat -A POSTROUTING`), not persisted via netplan/firewalld, so they must be re-applied after reboots. The management stack playbook (`firewall` role) may reset iptables; step 12 re-applies the masquerade rule after Ansible runs.

---

## File layout

```
Validation/
  .gitignore                        # ignores http/ and .munge_key_b64
  launch_v3.sh                      # main orchestrator (entry point)
  values_v3.sh                      # tunables: BB_BRANCH, HOST_IP, DISTROS, STEP
  vms/
    private_network.xml             # virbr1 libvirt network definition
    cluster_network.xml             # virbr2 libvirt network definition
  http/
    meta-data                       # cloud-init meta-data (empty)
    user-data.template              # Ubuntu autoinstall template (SSH key appended at runtime)
  steps_v3/
    common.sh                       # all per-distro arrays (MACs, IPs, ISOs, variants, flags)
    functions/
      waitforssh.sh                 # SSH polling loop helper
    01_setup_networks.sh            # create/start virbr1 + virbr2
    02_start_http_server.sh         # Python3 HTTP server on HOST_HTTP_PORT
    03_bootstrap_mgt1.sh            # download Ubuntu ISO, cloud-init install mgt1
    04_deploy_bb_on_mgt1.sh         # bootstrap BB on mgt1, upload mgt1 inventory, run playbook
    inventories/
      mgt1_bootstrap/hosts          # mgt1 + all 4 mgmt VMs pre-declared
      cluster/
        rhel9/                      # hosts + group_vars/all/{repositories,nfs,slurm,users}.yml
        rhel10/
        ubuntu24/
        debian13/
    playbooks/
      managements_full.yml          # 15-role stack for the mgmt VM
      logins.yml                    # login node stack
      computes.yml                  # compute node stack
    per_distro/
      10_pxe_deploy_cluster_mgmt.sh
      11_bootstrap_bb_on_mgmt.sh
      12_deploy_management_stack.sh
      13_prepare_pxe_for_cluster.sh
      14_pxe_deploy_cluster_nodes.sh
      15_deploy_node_stacks.sh
      16_test_slurm.sh
      17_cleanup_distro.sh
```

---

## Key configuration values

### Fixed MAC addresses

| Host | Interface | MAC |
|------|-----------|-----|
| mgt1 | virbr0 | 52:54:00:fa:12:01 |
| mgt1 | virbr1 | 52:54:00:fa:12:02 |
| mgmt_rhel9 | virbr1 | 52:54:00:bb:09:01 |
| mgmt_rhel9 | virbr2 | 52:54:00:cc:09:01 |
| mgmt_rhel10 | virbr1 | 52:54:00:bb:10:01 |
| mgmt_rhel10 | virbr2 | 52:54:00:cc:10:01 |
| mgmt_ubuntu24 | virbr1 | 52:54:00:bb:24:01 |
| mgmt_ubuntu24 | virbr2 | 52:54:00:cc:24:01 |
| mgmt_debian13 | virbr1 | 52:54:00:bb:13:01 |
| mgmt_debian13 | virbr2 | 52:54:00:cc:13:01 |
| login1 | virbr2 | 52:54:00:cc:00:10 |
| c001 | virbr2 | 52:54:00:cc:00:11 |
| c002 | virbr2 | 52:54:00:cc:00:12 |

### Fixed IPs

| Host | Network | IP |
|------|---------|-----|
| mgt1 | virbr1 | 10.10.0.1 |
| mgmt_rhel9 | virbr1 | 10.10.0.21 |
| mgmt_rhel10 | virbr1 | 10.10.0.22 |
| mgmt_ubuntu24 | virbr1 | 10.10.0.23 |
| mgmt_debian13 | virbr1 | 10.10.0.24 |
| mgt (mgmt VM) | virbr2 | 10.20.0.1 |
| login1 | virbr2 | 10.20.0.2 |
| c001 | virbr2 | 10.20.0.3 |
| c002 | virbr2 | 10.20.0.4 |

### ISO files

| Distro | ISO | URL base |
|--------|-----|----------|
| rhel9 | Rocky-9-latest-x86_64-dvd.iso | download.rockylinux.org/pub/rocky/9/isos/x86_64/ |
| rhel10 | Rocky-10-latest-x86_64-dvd.iso | download.rockylinux.org/pub/rocky/10/isos/x86_64/ |
| ubuntu24 | ubuntu-24.04.4-live-server-amd64.iso | releases.ubuntu.com/24.04.4/ |
| debian13 | debian-testing-amd64-netinst.iso | cdimage.debian.org/cdimage/daily-builds/daily/arch-latest/amd64/iso-cd/ |

Note: The generic `ubuntu-24.04-live-server-amd64.iso` name is no longer available at releases.ubuntu.com; always use the specific point release (e.g. 24.04.4).

---

## Resume / step control

```bash
# Start fresh
./launch_v3.sh

# Resume from step 3 (mgt1 install) — steps 01 and 02 treated as done
STEP=2 ./launch_v3.sh

# Resume from step 11 for a specific distro — steps 01-10 treated as done
STEP=10 CURRENT_DISTRO=rhel9 ./launch_v3.sh
```

Step numbers:
- 1 = networks, 2 = HTTP server, 3 = mgt1 cloud-init install, 4 = BB on mgt1
- 10 = PXE deploy mgmt VM, 11 = BB bootstrap on mgmt VM
- 12 = management stack (Ansible), 13 = PXE prep for cluster nodes
- 14 = PXE deploy cluster nodes, 15 = node stacks (Ansible)
- 16 = Slurm job test, 17 = cleanup (always runs)

---

## BlueBanquise bootstrap approach

`online_bootstrap.sh` hardcodes the `master` branch. To install a different branch:

1. Run `online_bootstrap.sh --silent --skip_environment` (creates `bluebanquise` user + Python deps, stops before venv/collection).
2. `git clone -b $BB_BRANCH https://github.com/bluebanquise/bluebanquise.git`
3. `./bluebanquise/bootstrap/configure_environment.sh --bb_collections_local_path=.../collections/infrastructure`

The `BB_BRANCH` variable in `values_v3.sh` controls which branch is used.

**Critical:** Always set `export ANSIBLE_CONFIG=/var/lib/bluebanquise/bluebanquise/ansible.cfg` before running any Ansible command on a BB node. The `.bashrc` is not sourced in non-interactive SSH sessions.

---

## Munge key

Generated once on first run, stored in `Validation/.munge_key_b64` (gitignored).
Injected at runtime by step 11 into each distro's `cluster/group_vars/all/slurm.yml` as:
```
slurm_munge_key_b64: "<value>"
```

---

## SSH access chain

- Host → mgt1: `ssh bluebanquise@<mgt1_virbr0_ip>` (host pubkey injected during step 03)
- Host → mgmt VM: `ssh -J bluebanquise@<mgt1_ip> bluebanquise@<mgmt_virbr1_ip>` (host pubkey added during step 11)
- mgmt VM → cluster nodes: `ssh bluebanquise@login1` etc. (mgmt VM pubkey baked in via pxe_stack/os_admin_ssh_keys)

In `common.sh`, `setup_ssh_aliases <distro>` populates `$SSH_MGT1`, `$SSH_MGMT`, `$SCP_MGT1`, `$SCP_MGMT`.

---

## Repositories role configuration

The cluster nodes have no local mirror — they use direct internet access.
The `repositories` role uses the "advanced" format with explicit URLs:

- **RHEL**: `bb_repositories` list with `baseurl` entries (EPEL + BB el9/el10 repo), `gpgcheck: false`
- **Ubuntu/Debian**: `bb_repositories` list with `repo: "deb [trusted=yes] https://bluebanquise.com/..."` entries

The `repositories` role must run on ALL nodes (mgmt, login, compute) because BlueBanquise provides up-to-date Slurm packages.

---

## Known issues encountered and fixed

### virbr1/virbr2 not found (step 03 fails)

`virt-install` fails with `Cannot get interface MTU on 'virbr1': No such device`.

**Cause:** `virsh net-list --all` includes inactive (defined-but-not-started) networks. On a rerun after partial failure the network may be defined but not started, so the old code skipped `net-start`.

**Fix (already applied in `01_setup_networks.sh`):** Separate the existence check (`--all`) from the active check (without `--all`). Define if missing, start if inactive. Add `sleep 2` after starting to let the kernel create the bridge.

### Ubuntu ISO filename

`ubuntu-24.04-live-server-amd64.iso` is no longer available at `releases.ubuntu.com/24.04/`.
Use `ubuntu-24.04.4-live-server-amd64.iso` from `releases.ubuntu.com/24.04.4/`.
`common.sh` and `03_bootstrap_mgt1.sh` are already updated to 24.04.4.

### mgt1 installer RAM

The Ubuntu 24.04 autoinstall fails with 8 GB RAM. Use `--ram=12000` for the install/provisioning
boot. Briefly changed 2026-08-07 to also keep 12000M at runtime after install (host had plenty of
headroom); reverted 2026-08-09 (explicit request) back to provisioning-only — every VM this
validation creates (mgt1, every distro's mgmt VM, login1/c001/c002) now drops to 4000M via
`virsh setmem ... --config` before the post-install disk boot, matching the original intent that
12000M is only needed for the installer, not steady-state runtime.

---

## Playbooks reference

### `managements_full.yml` (run on the mgmt VM as `--limit mgt`)
Roles in order: `repositories`, `set_hostname`, `http_server`, `nic`, `hosts_file`, `dhcp_server`, `dns_server`, `clustershell`, `pxe_stack`, `time` (profile: server), `firewall`, `nfs` (profile: server), `slurm` (profile: controller), `users`

### `logins.yml` (run on `login1`)
Roles: `repositories`, `set_hostname`, `nic`, `hosts_file`, `dns_client`, `time` (profile: client), `firewall`, `nfs` (profile: client), `slurm` (profile: submitter), `users`

### `computes.yml` (run on `c001`, `c002`)
Roles: `repositories`, `set_hostname`, `nic`, `hosts_file`, `dns_client`, `time` (profile: client), `firewall`, `nfs` (profile: client), `slurm` (profile: compute), `users`

---

## Current test status (as of 2026-08-06, live run on a real remote host)

First real end-to-end run, on Oxedions' own remote host (not the sandbox). `BB_BRANCH` must be
`BB-UMMON-1` (not `master`) to validate the actual branch under development — `values_v3.sh` fixed
to match. Several environment-specific and script bugs found and fixed this session, all synced to
the remote already:

### Fixed this session

1. **`common.sh`**: RockyLinux ISOs replace AlmaLinux for rhel9/rhel10 (explicit request).
2. **`LIBVIRT_DEFAULT_URI` bug**: bare `virsh`/`virt-install` as a non-root user resolves to
   `qemu:///session` (libvirt picks system vs. session by UID, not group membership), spawning an
   unprivileged per-user libvirtd with no bridge capability — `virbr1`/`virbr2` creation failed with
   "Operation not permitted". Fixed by exporting `LIBVIRT_DEFAULT_URI=qemu:///system` at the top of
   `common.sh`. Not host-specific — will hit any fresh host unless something else already exports
   this globally.
3. **nic role self-reboot kills the whole orchestrator step, twice**: on Ubuntu/Debian, `nic`
   reboots to switch netplan to NetworkManager (`nic_allow_reboot` default true). Both mgt1 (step
   04) and the ubuntu24/debian13 mgmt VMs (`per_distro/12`) run this playbook against *themselves*
   via a `127.0.0.1 <alias>` loopback trick — so the reboot kills the whole VM, ansible-playbook
   process included, not just the inner Ansible-to-target SSH connection the reboot module knows how
   to ride out gracefully. Fixed in both places: run `--tags nic` alone first, tolerate the outer
   SSH session dying (expected, not a failure — harmless no-op on RHEL where nic never reboots),
   `sleep 15` + `waitforssh.sh`, then run the full stack (nic is then idempotent, no second reboot).
4. **Host firewall (`ufw`) blocking guest→host traffic**: got enabled on the remote host during
   unrelated maintenance, default-deny INPUT with only port 22 open. mgt1's autoinstall couldn't
   `wget` the ISO from the host's own port-8000 Python HTTP server — timed out and dropped to a
   busybox rescue shell (confirmed via `virsh screenshot`, since the kernel_args have no
   `console=ttyS0` so nothing reaches a serial log). Same-host curl worked fine (routes via `lo`,
   unconditionally accepted); guest traffic arrives via `virbr0`/`virbr1` and hit the default-deny.
   Fixed with `ufw allow from 192.168.122.0/24 to any port 8000 proto tcp` (+ the virbr1 /16 for
   symmetry, though mgmt VMs actually fetch their ISO through mgt1's own PXE stack, never directly
   from the validation host). **Environment-specific, not a script bug** — but worth checking first
   on any host if mgt1's install hangs at "Creating domain..." with near-zero CPU time for more than
   a couple minutes.
5. **`.ssh` directory never created before being written to**: step 04 (mgt1) and `per_distro/11`
   (mgmt VM) both do `cat .ssh/authorized_keys | sudo tee -a .../bluebanquise/.ssh/authorized_keys`
   right after `online_bootstrap.sh --skip_environment` — but that script (even without
   `--skip_environment`) never creates `~bluebanquise/.ssh`; only `configure_environment.sh` does
   (later, in the same step), and its own authorized_keys logic is written expecting the host's key
   to already be in the file by then (appends its own key rather than overwriting). Fixed by
   `mkdir -p`/`chown`/`chmod 700` the directory ourselves first, in both places.
6. **Stale `set_hostname` role reference in this repo's own playbooks**: `managements_full.yml`,
   `logins.yml`, and `computes.yml` (`Validation/steps_v3/playbooks/`) all still referenced
   `bluebanquise.infrastructure.set_hostname` — one of the 9 roles consolidated into
   `local_configuration` back in 2026-07 (see the bluebanquise repo's own CLAUDE.md). That sweep
   covered `resources/workflow/playbooks/`, `.github/workflows/`, and some docs, but not this
   separate `infrastructure` repo's validation playbooks. Ansible resolves every role in a play's
   `roles:` list at parse time regardless of `--tags` filtering, so this failed immediately
   ("role ... was not found in ...") even for the nic-only pass. Fixed: swapped to
   `bluebanquise.infrastructure.local_configuration` in all three files. Behaviorally equivalent
   here since none of `os_access_control`/`local_configuration_*` dict vars are set in the
   validation inventories, so the security/system/storage subtasks stay conditional no-ops (same
   "CI coverage gap" shape documented above) — only the hostname-setting behavior actually fires.

### Host key verification failed — root-caused and fixed (2026-08-07)

The blocker from the previous session end. Root cause (Oxedions' own diagnosis, confirmed):
`ansible.cfg` has default (strict) `host_key_checking`, and non-interactive SSH can't prompt — so
"unknown host" and "changed host" both fail identically as "Host key verification failed". This
means it isn't just a post-reboot problem: on a *completely fresh* mgt1 (empty `known_hosts`), even
the **first-ever** self-connection — the `--tags nic`-only pass itself — gets rejected before nic
ever runs, and the resulting cascading failure (the real reboot then firing mid-way through the
*full*, unwrapped second pass instead of the isolated first one) was mistaken initially for a
same-symptom repeat.

**Fix**: seed the trusted key twice, both in `04_deploy_bb_on_mgt1.sh` (mgt1) and `per_distro/12`
(ubuntu24/debian13 mgmt VMs) — once right before the nic-only pass, once again after the reboot:
```bash
ssh-keygen -f ~/.ssh/known_hosts -R <alias> 2>/dev/null
ssh-keygen -f ~/.ssh/known_hosts -R 127.0.0.1 2>/dev/null
ssh -o StrictHostKeyChecking=accept-new <alias> true
```
Clearing both the alias name and `127.0.0.1` covers SSH's `CheckHostIP` caching under either. A
no-op (harmless) on RHEL, where `nic` never reboots and the first pass already works cleanly.

### Two more real bugs found once past the host-key issue (2026-08-07)

Both are in this repo's own inventories, not BlueBanquise bugs — the roles were correctly enforcing
real requirements the validation inventories never satisfied:

1. **Missing `firewall_zone`**: the `firewall` role fails outright
   ("`Bailing out. This role requires networks[<name>]['firewall_zone'] to be set`") for any network
   assigned to an interface, if that network has no `firewall_zone` key — and `os_firewall` defaults
   to `true` when unset, so this always ran. Neither reference inventory
   (`resources/examples/simple_cluster`, `resources/workflow/inventory_standard`) sets this either;
   CI avoids it entirely via `os_firewall: false`. Since validating `firewall` for real is the whole
   point here, added `firewall_zone: internal` to every network instead of disabling the role: all 5
   inventory `hosts` files (`mgt1_bootstrap` + all 4 `cluster/<distro>`).
2. **Missing `slurm_partitions_list`/`slurm_controller_hostname` on mgt1's own inventory**: the
   `slurm` role (profile: controller) is part of `managements_full.yml` and runs on mgt1 itself
   during step 04, not just on the real per-distro mgmt VMs — but `mgt1_bootstrap/hosts` never had
   any `slurm_*` vars at all (unlike the per-distro `cluster/<distro>/group_vars/all/slurm.yml`
   files, which already had this right). This was almost certainly the *original* unidentified
   `managements_full.yml` failure from 2026-07 that started this whole investigation. Fixed by adding
   `slurm_controller_hostname=mgt1` and `slurm_partitions_list=[]` (empty — mgt1 has no real compute
   nodes of its own; `slurm_organize_equipments` tolerates an empty list cleanly, confirmed by reading
   the filter) to `mgt1_bootstrap/hosts`.
3. **Missing `slurm_munge_key_b64` on mgt1's own inventory, same shape as #2**: without it, the
   `slurm` role's munge task falls back to `copy: src: munge.key` — a static file the role doesn't
   ship, so it fails with "Could not find or access 'munge.key'". `per_distro/11` already injects
   `slurm_munge_key_b64` (from the shared `.munge_key_b64`) into the cluster inventories; step 04 had
   no equivalent for mgt1_bootstrap. Fixed by adding the same injection there.

**Result**: `mgt1 BB deployment: SUCCESS` — Phase 1 (mgt1 bootstrap + full management stack) passes
clean end to end for the first time this validation effort.

### Phase 2, rhel9: three more real bugs, one of them a genuine BlueBanquise-collection fix (2026-08-07)

**ISO download speed / prefetching**: `download.rockylinux.org` was slow and erratic for the ~15GB
Rocky-9 DVD ISO (fluctuating 400KB–7MB/s). Switched `DISTRO_ISO_URL` to `dl.rockylinux.org` (Rocky's
CDN-backed hostname) for rhel9/rhel10 — noticeably faster. Also added background ISO prefetching:
`per_distro/10` now kicks off `wget -nc` for every *other* distro's ISO not yet cached, right after
downloading its own, so later distros' downloads overlap with the current distro's cluster
deployment instead of happening serially only once their own turn comes up (Oxedions' suggestion).

**`pxe_stack` role never installs Flask, on any OS family — real BlueBanquise bug, fixed**:
`bluebanquise-pxe-stack-daemon` does `from flask import Flask...` but no `vars/<OS>.yml` in the role
lists `python3-flask` (or equivalent) in `pxe_stack_packages_to_install`. The daemon crash-looped
every 10s (RestartSec=10) from the moment mgt1 was first bootstrapped — `ModuleNotFoundError: No
module named 'flask'` — visible only as a cosmetic-looking "daemon is not responding" warning from
`bootset` that didn't block anything *until* a client actually needed the daemon (see below), so it
went unnoticed through an apparently-successful `managements_full.yml` run (Ansible's `service`
module only confirms the start command succeeded, not that the service stays up). Fixed by adding
the OS-appropriate Flask package to every `vars/<OS>.yml` in the role: `python3-flask` (Ubuntu,
Debian, Debian_13, RedHat_8/9/10), `python36-flask` (RedHat_7, matches its existing `python36`
naming), `python3-Flask` (Suse/Suse_12, openSUSE capitalization convention). Live-installed +
daemon restarted on mgt1 to unblock immediately. **Committed and pushed to `BB-UMMON-1` on
2026-08-09** (by Oxedions — this session confirmed the fix had regressed on mgt1's 2026-08-09
rebuild specifically *because* it was still uncommitted; a fresh `git clone -b BB-UMMON-1` doesn't
see local-only changes, only what's on GitHub).

**iPXE corrupts the initrd for any large (~200MB+) osdeploy install — real BlueBanquise bug, root-
caused and fixed**. Symptom chain, in the order actually encountered (each looked like a plausible
standalone cause until disproven):
1. mgmt_rhel9 sat idle at a bare **UEFI Shell** — Oxedions' correction: this means DHCP/PXE-boot-file
   fetch never even started, ruling out "the daemon is unreachable" (that would show an iPXE shell,
   not UEFI's). Root cause: `firewalld`'s `internal` zone (bound by `firewall_zone`, freshly working
   for the first time as of the previous fix) only ships `dhcpv6-client mdns samba-client ssh` by
   default — no `dhcp` (server-side v4), `tftp`, or `http`. Every previous validation run had died
   before `firewall` ever got far enough to matter; this was the first time it was actually applied.
2. Once past that, iPXE loaded and chained to `redhat_9.ipxe`, then timed out reaching
   `bluebanquise-pxe-stack-daemon` on port 7770 across the network (`Connection timed out`) — same
   root cause, one port further: `dhcp`/`tftp`/`http` are standard firewalld services, port 7770 is
   custom and needs its own `ports_enabled` rule. Added `dns` proactively too (needed once the
   installer itself starts resolving names). **Design point surfaced along the way** (Oxedions):
   BlueBanquise roles are *supposed* to self-register their own firewalld ports via
   `<role>_firewall_zone | default(bb_services_firewall_zone) | default('public')` — confirmed
   `dhcp_server`→`dhcp`, `dns_server`→`dns`, `http_server`→`http`, `pxe_stack`→`http`+`tftp`+its own
   port 7770 all already have this. The 4 per-distro `cluster/<distro>` inventories now use
   `os_firewall=true` + `bb_services_firewall_zone=internal` (the intended mechanism) instead of a
   manual `firewall_zones` list — this is also how the `os_firewall` default-inconsistency bug (see
   the bluebanquise repo's own CLAUDE.md) was actually caught in the first place, not just documented
   in the abstract. `mgt1_bootstrap`'s inventory deliberately kept the manual `firewall_zones`
   approach (Oxedions: "for mgt1, lets keep it like you did") — a live A/B of both mechanisms.
3. Past both firewall issues, the kernel panicked ~2s into boot: `Initramfs unpacking failed: invalid
   magic at start of compressed archive` → `Kernel panic - not syncing: VFS: Unable to mount root fs
   on unknown-block(0,0)`. Verified the download itself was byte-perfect first (iPXE's own reported
   MD5 of the fetched `initrd.img` matched the real file's MD5 exactly) — ruling out network/transfer
   corruption entirely; the corruption happens only at the final hand-off to the kernel. Tried
   switching rhel9/rhel10 from EFI to legacy BIOS boot (a plausible-looking fix targeting iPXE's
   `LINUX_EFI_INITRD_MEDIA_GUID` EFI-stub loading path) — **identical failure in BIOS mode too**,
   disproving that theory outright (BIOS mode uses a completely different iPXE build,
   `dhcpretry_undionly.kpxe` vs `dhcpretry_snponly_ipxe.efi` — a shared bug across both pointed at the
   shared `redhat_9.ipxe` template instead). A web search surfaced the real mechanism
   ([ipxe/ipxe#1724](https://github.com/ipxe/ipxe/discussions/1724)): iPXE bundles *every currently
   resident image in memory* into the kernel's initrd payload at boot time. The smoking gun was
   already sitting in our own capture — the template's own `imgstat` output listed a `stage_report :
   3 bytes` resident image alongside `vmlinuz`/`initrd.img`. `menu.ipxe.j2` calls `imgfetch
   .../stage_report?...` at every single boot-path branch (osdeploy, diskless, clonezilla×3, alpine,
   disk, memtest, next, custom) to report PXE stage progress to the daemon, but **never `imgfree`s
   it** — that leaked 3-byte image gets bundled in front of the real initrd, corrupting its start.
   Fixed by adding `imgfree stage_report || true` immediately after every one of the 11 `imgfetch
   .../stage_report...` call sites in `menu.ipxe.j2`. Confirmed working: mgmt_rhel9's Rocky 9 kickstart
   install completed **fully cleanly** — first-ever successful mgmt VM OS install in this validation
   effort's history. Reverted rhel9 to legacy BIOS as a deliberately-validated config; rhel10 restored
   to EFI (Oxedions: "now you found the issue for kernel panic, so we can validate EFI in the
   process") so both firmware paths get exercised. **Committed and pushed to `BB-UMMON-1` on
   2026-08-09.**
4. One more real, distinct issue once past the initrd bug: `nm-wait-online-initrd.service` hung
   indefinitely (dracut/NetworkManager waiting for *all* detected NICs to reach a terminal state).
   mgmt_rhel9 has two NICs — virbr1/net-admin (mgt1's DHCP, working fine, confirmed via repeated
   successful `kea-dhcp4` lease grants) and virbr2/net-cluster (no DHCP server exists there yet —
   this VM is meant to *provide* that itself, later, once BlueBanquise's own `nic`/`dhcp_server`
   roles configure it). The second NIC will never resolve during the VM's own install, so an
   unrestricted network-activation wait never terminates. Fixed with dracut's `ifname=eth0:<mac>
   ip=eth0:dhcp` kernel params, pinning activation to just the admin NIC — but getting that value
   onto the kernel command line needed new plumbing (below).

**New BlueBanquise feature, built collaboratively with Oxedions**: `bluebanquise-bootset` already
had an unwired `-e`/`--extra-parameters` CLI flag (parsed, never sent anywhere), and the daemon
already had a `dedicated_kernel_parameters` per-host state field (initialized empty at bootstrap,
already read and rendered into `set dedicated-kernel-parameters {}` in every host's generated iPXE
file — which is exactly what every osdeploy template's `${dedicated-kernel-parameters}` kernel-line
slot consumes) — but nothing ever *wrote* to it. Wired it end to end: `PUT
/host/<hostname>/menu-default` now optionally accepts a `dedicated_kernel_parameters` string
alongside `boot_queue` (omitted from the JSON body entirely when `-e` isn't passed — the CLI's
`"none"` sentinel means "leave it alone", not "set it to the literal string none", since that would
land verbatim on a kernel command line); `bootset -e` now sends it through the same call `-b`
already makes. Verified end to end: `bluebanquise-bootset -n mgmt_rhel9 -b osdeploy -e "ifname=eth0:
52:54:00:bb:09:01 ip=eth0:dhcp"` → confirmed in the daemon's JSON state → confirmed rendered
correctly in `GET /host/mgmt_rhel9.ipxe`'s `set dedicated-kernel-parameters` line. `per_distro/10`
now passes `-e "ifname=eth0:$MAC_VIRBR1 ip=eth0:dhcp"` for rhel9/rhel10 only (dracut-specific syntax
— Debian/Ubuntu use a different network-config subsystem, untested whether they hit the same
class of bug). **Committed and pushed to `BB-UMMON-1` on 2026-08-09** (`bluebanquise-bootset`,
`bluebanquise-pxe-stack-daemon`, both docstrings).

**Gotcha hit rebuilding mgt1 (2026-08-09): two separate on-disk collection copies, only one live**.
`configure_environment.sh` (step 04) does `git clone` into `/var/lib/bluebanquise/bluebanquise/` and
then `ansible-galaxy collection install --bb_collections_local_path=...`, which *copies* that clone's
`collections/infrastructure/` into `~/.ansible/collections/ansible_collections/bluebanquise/infrastructure/`
— a second, independent copy. `ansible-playbook` only ever reads the installed copy. Live-patching
role files in the raw git clone (to unblock mgt1 while these three fixes were still uncommitted, see
above) had **zero effect** on a live run — `ansible-playbook --tags pxe_stack` reported `changed=0`
against already-stale content — until `ansible-galaxy collection install <path> --force` was run to
resync the installed copy from the patched clone. Even after that, the already-running
`bluebanquise-pxe-stack-daemon` systemd process kept executing its old in-memory code (a copied file
on disk doesn't affect an already-forked Python process) until explicitly `systemctl restart`ed —
Ansible's own `service` task in the role didn't force this since the preceding `copy` task reported
no change on that *particular* invocation (the change had already landed one invocation earlier).
Net lesson for any future live-patch-before-commit situation: edit the git clone, `ansible-galaxy
collection install <path> --force`, re-run the role tag, **then** explicitly restart any daemon the
role manages — don't trust the role's own service task to notice a change that happened outside its
own copy task's most recent run.

**RAM bumped to 12000M everywhere, then reverted to provisioning-only** (2026-08-07, then reverted
2026-08-09, both explicit request): briefly kept 12000M at runtime instead of ballooning down after
install (host had plenty of headroom). Reverted 2026-08-09: 12000M is for the install/provisioning
boot only (`--ram=12000` on `virt-install`); every VM now drops to 4000M via `virsh setmem ...
--config` before the disk boot that follows install. `03_bootstrap_mgt1.sh`, `per_distro/10`,
`per_distro/14` all updated back to this pattern.

**Disk-space gap — fixed 2026-08-09**: mgt1's disk had hit 946MB free / 96% full, almost entirely the
~15GB Rocky-9 ISO downloaded onto mgt1 itself (`wget`'d from the host, then loop-mounted for the PXE
install tree — cleaned up only at per-distro step 17, so it sat there through all of rhel9's
remaining steps). Addressed two ways at session start: (1) deleted the stale rhel9 ISO copy from
mgt1 directly (freed it back to 16G avail / 27% full — safe because the mgmt-VM install that needed
it was already done; step 13 downloads its own separate ISO copy onto the mgmt VM itself, mgt1's copy
is only needed again if step 10 re-runs, which just re-fetches it quickly from the host's own cached
copy); (2) `03_bootstrap_mgt1.sh`'s disk size bumped `24`→`60` (explicit request — "if needed we can
redeploy it"), which meant destroying and rebuilding mgt1 from scratch via `03`+`04` rather than an
in-place resize.

**Real bug caught rebuilding mgt1 — virt-install silently ignores `--disk size=` on an existing
file**: the first rebuild attempt at 60GB "succeeded" (BB deployment: SUCCESS, no errors anywhere)
but `df` on mgt1 still showed the old 22GB filesystem. Root cause: `03_bootstrap_mgt1.sh`'s
destroy/undefine block never removed the old `/data/images/mgt1.qcow2` file — unlike `per_distro/10`
and `/14`, which already `rm -f` their qcow2 before `virt-install`. `virt-install --disk
path=...,size=60` only applies `size=` when *creating* a new file; given an existing file it reuses
it as-is at its old size, with no warning. Fixed by adding the same `sudo rm -f
/data/images/mgt1.qcow2` before `virt-install` in `03_bootstrap_mgt1.sh`. Worth generalizing: any
`virt-install --disk path=...,size=N` call in this repo needs an explicit `rm -f` of that path first
if the size is meant to take effect — a stale file from a previous run silently wins over the
requested size every time, and nothing in `virt-install`'s own output flags it.

**Two more real bugs hit resuming rhel9's `per_distro/10` for the first time (2026-08-09)**:

1. **`/tmp/waitforssh.sh` doesn't reliably survive a VM's own nic-role self-reboot.**
   `03_bootstrap_mgt1.sh` copied it to `/tmp` on mgt1 once, *before* step 04 runs (and step 04's own
   nic-only pass reboots mgt1 partway through) — same pattern in `per_distro/11` for the mgmt VM
   itself (ubuntu24/debian13 reboot via nic too, in `per_distro/12`). Observed missing from `/tmp`
   afterward on a live run — every later step that runs it via SSH (`per_distro/10`, `/11`, `/12`,
   `/14`, `/15`) got `bash: line 1: /tmp/waitforssh.sh: No such file or directory`, which — since
   none of these calls are wrapped to tolerate failure — hit `launch_v3.sh`'s top-level `set -e` and
   killed the *entire* run, not just that step. Root cause of the disappearance itself wasn't pinned
   down (mgt1's `/tmp` is ordinary disk-backed, not tmpfs, so it isn't the usual "tmpfs wiped on
   reboot" explanation) — but the observed behavior is reproducible enough to defend against
   regardless. Fixed properly (Oxedions' suggestion) rather than papering over it with a second
   defensive copy: install it to `/usr/local/bin/waitforssh.sh` instead of `/tmp` everywhere (both
   the mgt1 copy in `03_bootstrap_mgt1.sh` and the mgmt-VM copy in `per_distro/11`, plus every
   consuming call site in `per_distro/10`, `/11`, `/12`, `/14`, `/15`) — root-owned, world-executable,
   ordinary rootfs path, no reboot-survival question at all. The mgt1 copy has to stage through `/tmp`
   first and `sudo install -m 755` it into place, since it's written by the `generic` user *before*
   BlueBanquise (and thus `/var/lib/bluebanquise`) exists yet on a fresh mgt1 — `/usr/local/bin` was
   chosen specifically because it needs no such precondition on either host.
2. **`virt-install --pxe` only sets network-first boot for its own initial `--wait`ed install boot,
   not the domain's persisted boot order.** If that first boot fails before completing an install
   (e.g. it manages to PXE-boot but then hits a transient error and drops to an iPXE shell — this
   session's specific trigger was restarting `bluebanquise-pxe-stack-daemon` while the VM's chain
   request to it was in flight, giving it a "Connection reset"), the domain's XML is left with plain
   `<boot dev='hd'/>` — confirmed via `virsh dumpxml`. Any later `virsh start`/`virsh reset` boots
   straight to the (still-empty) disk: "Boot failed: not a bootable disk. No bootable device." — it
   never retries the network boot on its own, and nothing about this state is surfaced anywhere
   `launch_v3.sh` would notice (the script was still happily sitting in `waitforssh.sh`'s infinite
   retry loop waiting for an install that would never happen). No script fix applied for this one —
   the existing recovery path (destroy/undefine + fresh `virt-install --pxe`, i.e. just re-running
   `per_distro/10`) already handles it correctly by construction, so it's not a script bug on this
   codebase's side, just a gotcha worth recognizing fast if a VM's console shows "No bootable
   device" after any mid-boot interruption: don't `virsh start`/`reset` it, recreate it.

**mgt1's own internet-gateway masquerade doesn't survive the `firewall` role running — found and
fixed properly this time (2026-08-09).** Once `mgmt_rhel9` had `wget` (previous bullet), it still
couldn't resolve/reach anything (`Couldn't connect to server`, `No route to host`) — `mgt1`'s own
`iptables -t nat` `POSTROUTING` chain (set up manually in `03_bootstrap_mgt1.sh`) was completely
empty. Root cause: `04_deploy_bb_on_mgt1.sh` runs `managements_full.yml` (including the `firewall`
role) *after* `03`'s masquerade rule is set, and the `firewall` role's own firewalld setup wipes
plain `iptables` rules in that table — nothing ever re-applies it for mgt1 afterward (unlike
`per_distro/12`, which already does this re-apply for the per-distro mgmt VM's own masquerade).
Re-adding the raw `iptables` rule alone still weren't enough, either: firewalld's zone model treats
`enp1s0` (mgt1's WAN/virbr0-facing NIC, never declared in `network_interfaces` so BlueBanquise never
zones it) as living in the default `public` zone, while `internal`-zone-sourced traffic (10.10.0.0/16)
needs an explicit **firewalld policy** to forward into a *different* zone at all — masquerade and
`forward: yes` on a zone only govern same-zone traffic. `firewall-cmd --get-policies` showed only the
built-in `allow-host-ipv6`; nothing ships a general gateway-style policy by default. Fixed two ways,
kept deliberately separate:
- **Role-managed, persistent**: `firewall_zones`'s `internal` entry in `mgt1_bootstrap/hosts` now
  also sets `'masquerade':True` — the `firewall` role already supports this
  (`ansible.posix.firewalld`, `permanent: true`, in `firewalld.yml`'s "Define masquerade in firewall's
  zones" task), so this survives future `firewall`-role re-runs on its own, no re-apply step needed.
- **Harness-only workaround, not a BlueBanquise change**: a `firewall-cmd --new-policy
  internal-to-public` (ingress-zone `internal`, egress-zone `public`, target `ACCEPT`) added as a
  script step at the end of `04_deploy_bb_on_mgt1.sh`, since the `firewall` role has **no support for
  firewalld policies at all** — only zone-level services/ports/rich-rules/masquerade/icmp. Deliberately
  kept in the harness rather than extended into the role (Oxedions, 2026-08-09): mgt1 NAT-ing its own
  uplink to reach the real internet is an artifact of this validation harness's dual-NAT-hop topology
  (simulating an isolated network), not a shape a real BlueBanquise deployment normally needs. Whether
  `mgmt_rhel9`'s *own* gateway role (for `login1`/`c001`/`c002`, a much more realistic
  "management-node-gateways-its-cluster" pattern) can avoid this same policy requirement — e.g. by
  binding both of its interfaces to the same zone instead of relying on a cross-zone policy — is
  still open; deliberately deferred to be tested live against `per_distro/12` rather than guessed at,
  per Oxedions' explicit requirement that this case work "using only the firewall role."
- **Inventory-parsing trap, not a BlueBanquise/role bug**: first attempt used `'masquerade':true`
  (lowercase, JSON/YAML-style) and silently did nothing — no error anywhere, `firewall-cmd
  --query-masquerade` just kept returning `no`. This validation harness's inventories embed Python
  dict/list literals directly as INI `key=value` host_vars (`firewall_zones=[{...}]`) rather than
  proper YAML `group_vars`/`host_vars` files (contrast `resources/examples/simple_cluster`, which is
  BlueBanquise's own documented convention). Ansible's non-native Jinja templating auto-converts such
  strings back into real Python objects via `ast.literal_eval`, which demands *strict* Python literal
  syntax (`True`/`False`/`None`) — `true` isn't a valid Python token, so the whole literal silently
  fails to parse and `firewall_zones` is left as a plain unconverted string (confirmed via `ansible
  ... -m debug -a "var=firewall_zones"`: lowercase showed a single quoted string, capitalized showed
  a real structured list). Downstream `subelements`/`loop` filters on a plain string don't necessarily
  error loudly either — this can burn silent time on any boolean added to one of these harness
  inventories' embedded-literal vars, not just `masquerade`. Real YAML inventories don't have this
  failure mode at all, since YAML natively parses lowercase booleans.

**Two more environment-specific fixes found finishing `per_distro/11` for rhel9 (2026-08-09)**:
`wget` isn't installed on the minimal Rocky 9 DVD kickstart image, but `online_bootstrap.sh`'s
download (the very next command `per_distro/11` runs) uses it unconditionally — fixed by adding
`wget` to `DISTRO_PRE_BOOTSTRAP[rhel9]`/`[rhel10]`'s `dnf install` in `common.sh` (Ubuntu/Debian
images ship it already). Both this and the masquerade/policy fix above are pure validation-harness
environment gaps, not BlueBanquise bugs — surfaced only now because this is the first time a fresh
mgt1 rebuild's `managements_full.yml` run has gotten far enough, with `firewall_zone`s actually
enforced, to expose them.

**`per_distro/11`'s cluster-inventory upload path collided with BlueBanquise's own reserved runtime
directory — validation-harness bug, found and fixed (2026-08-09)**. First-ever `per_distro/12` run
for rhel9 got to `pxe_stack`'s `pxe_stack_daemon <|> Ensure cluster base and tmp directories exist`
task and failed: `"/var/lib/bluebanquise/cluster/hosts already exists as a file"`. Root cause:
`per_distro/11` did `scp -r "$INVENTORY_DIR" ... :/var/lib/bluebanquise/cluster` — since
`$INVENTORY_DIR` (`inventories/cluster/<distro>/`) itself contains a file literally named `hosts`
(the Ansible inventory) alongside `group_vars/`, the destination directory `cluster` ends up
*being* that inventory's contents verbatim. But `cluster_management`/`pxe_stack` reserve
`/var/lib/bluebanquise/cluster/hosts/<hostname>/...` as their own runtime cluster-state directory
(see "Cluster State System" above) — a plain naming coincidence between "the Ansible inventory file
called `hosts`" and "BlueBanquise's own per-host state directory called `hosts`" put an ordinary file
exactly where BlueBanquise needed to `mkdir` a directory. Fixed by uploading to
`/var/lib/bluebanquise/cluster_inventory` instead of `/var/lib/bluebanquise/cluster` — updated the
scp destination and both hardcoded path references in `per_distro/11`, and every `-i cluster` →
`-i cluster_inventory` in `per_distro/12`/`/15`'s `ansible-playbook` invocations. Not a BlueBanquise
bug: the collision is entirely a validation-harness directory-naming choice, and any real deployment
using a differently-named (or YAML group_vars/host_vars-based) inventory path would never hit it.

**Two more bugs hit resuming into `per_distro/12` after a break (2026-08-11)**:

1. **Validation-harness inventory bug**: `mgt`'s (the per-distro mgmt VM's) `net-cluster`
   `network_interfaces` entry in all 4 `inventories/cluster/<distro>/hosts` files was missing
   `'never_default4':'true'` — contrast `mgt1_bootstrap/hosts`'s own entry for mgt1, which already
   has it. Consequence: `net-cluster`'s `gateway4` (`10.20.0.1`) *is* the mgmt VM's own IP on that
   network (correct for `login1`/`c001`/`c002`, who should route through the mgmt VM) — but applied
   to the mgmt VM's *own* routing table by the `nic` role, with no `never_default4` to suppress it,
   it silently replaced the VM's real default route (via its other, DHCP-obtained `net-admin`
   interface toward mgt1 → internet) with a route via itself on `net-cluster`. Result: total loss of
   outbound connectivity the moment `per_distro/12`'s `nic` role ran, no error anywhere in the
   Ansible output — just a broken route (`ip route` showed `default via 10.20.0.1 dev enp2s0`,
   effectively routing to itself). Fixed by adding `'never_default4':'true'` to `mgt`'s entry in all
   4 cluster inventories, matching mgt1's own pattern.
2. **Firewalld policy masquerade, second half of the 2026-08-09 fix — the policy itself also needs
   `--add-masquerade`, not just the zone.** Even after (1)'s route fix, `mgmt_rhel9` still couldn't
   reach the internet through mgt1 — confirmed via `tcpdump` on mgt1's `enp1s0` that forwarded
   packets left with their original `10.10.0.21` source, unmasqueraded, silently dropped upstream
   (private source addresses aren't internet-routable, no error surfaces anywhere). Zone-level
   `masquerade: yes` (declared via `firewall_zones` on the `internal` zone) only NATs traffic whose
   *egress* interface is also in that same zone — cross-zone-forwarded traffic (exactly what the
   `internal-to-public` policy from 2026-08-09 exists for) needs masquerade declared **on the policy
   object itself**. Fixed by adding `sudo firewall-cmd --permanent --policy internal-to-public
   --add-masquerade` to `04_deploy_bb_on_mgt1.sh`'s policy-creation step. Also updated the
   bluebanquise repo's own `CLAUDE.md` firewall-policy future-task note with this second half of the
   gap, since it applies to any future policy-based BlueBanquise gateway design, not just this
   harness's mgt1 case.

Both fixed in the source scripts/inventories and hand-patched into the already-running `mgt1`/
`mgmt_rhel9` (confirmed: `ping 8.8.8.8` from `mgmt_rhel9` succeeds end to end through the full
mgt1 masquerade+policy chain).

**Operational gotcha, not a script bug: resuming with a `STEP` past 2 after `gabriel` itself
rebooted leaves the host's own ISO-serving HTTP server dead.** `02_start_http_server.sh` backgrounds
a plain `python3 -m http.server` process — it doesn't survive a host reboot, and nothing restarts it
automatically. Resuming with e.g. `STEP=11`/`STEP=12` (as this session did after the weekly-restart
pattern of stopping mid-session) skips step 02 entirely (`if (( STEP < 2 ))`), so the server stays
dead. Symptom: `per_distro/13`'s `wget` (fetching the cluster OS ISO onto the mgmt VM) just hangs —
the whole `launch_v3.sh` process eventually dies with no error text reaching the log at all (the SSH
heredoc's failure never gets flushed/captured before the process exit). Confirmed via `curl` to
`http://192.168.122.1:8000/` timing out. Fixed by hand each time so far (`cd Validation/http &&
python3 -m http.server 8000 &`, matching step 02 exactly) — worth remembering as a first check
whenever resuming a paused run with `STEP` set high enough to skip phase 1, especially right after a
host power cycle: `pgrep -af "http.server 8000"` on gabriel before assuming a per-distro step hang is
something else.

**State at end of session (2026-08-07), resumed and progressed 2026-08-09**: mgt1 running,
`mgmt_rhel9` shut off cleanly post-install at end of 2026-08-07 (that install was manual, not via
`launch_v3.sh`). Hypervisor host (`gabriel`) was then powered off; found rebooted (5 min uptime) at
the start of the 2026-08-09 session — both VMs were shut off, the two validation libvirt networks
were still up. This session: authenticated as `oxedions@192.168.1.23` (the sandbox's own SSH keypair
had rotated since the container was recreated, so the previously-trusted key no longer worked — the
`root@...` key failed, `oxedions` succeeded), started mgt1, found the disk-space issue reproduced
exactly as documented, fixed it as above, then rebuilt mgt1 at 60GB via a `phase1_only.sh` wrapper
(steps 01-04 only, stops short of the per-distro loop) run in the background on gabriel. See
"mgt1 installer RAM" and "RAM bumped to 12000M everywhere, then reverted" above for the same
session's RAM-policy reversion (12000M provisioning-only, 4000M steady-state), applied to this
rebuild. mgt1's rebuild finished cleanly on the second attempt (60GB disk confirmed, 45G free;
4000M runtime RAM confirmed). **Next**: `mgmt_rhel9`'s successful install from 2026-08-07 was still
via manual `virt-install` + `bootset`, not the orchestrator, so
`STEP=9 CURRENT_DISTRO=rhel9 ./launch_v3.sh` should be used to redo it — this exercises the *actual*
`per_distro/10` script path (including the `-e` kernel-parameter wiring and ISO prefetch logic) for
the first time, so treat that first resumed run as still worth watching closely rather than assuming
it's identical to the manual runs. Then continue through rhel9's remaining steps (BB bootstrap on
mgmt VM, management stack deploy, login1/c001/c002 PXE deploy, node stacks, Slurm test, cleanup) and
the rest of the per-distro loop.

### PXE installs were already air-gapped; migrated to the official tool anyway (2026-08-11)

When `login1`/`c001`/`c002`'s post-install `dnf update` started hitting real internet mirrors (see
the gateway/policy fixes above), it looked at first like the *kickstart install itself* might be
reaching the internet too — investigated and confirmed **it already wasn't**: `osdeploy/redhat_9.ipxe`
sets `inst.repo=`/`inst.addrepo=` to the local `pxe/netboots/.../iso/{BaseOS,AppStream}/` tree served
by the PXE host itself, and the kickstart template (`RedHat/kickstart.cfg.j2`) has no `url --url=`
of its own — repo sourcing is 100% controlled by those boot-time kernel parameters. Confirmed live:
`BaseOS/Packages` and `BaseOS/repodata` were genuinely populated and served locally; the mirror
errors were entirely from `per_distro/15`'s own post-install `dnf install -y epel-release && dnf
update -y` step (EPEL genuinely isn't on the Rocky DVD, needs real internet — expected, matches "we
will need later c001 and other hosts to reach the web").

Even so, `per_distro/10`/`/13` were doing this the *unofficial* way — a raw `mount` of the ISO
directly onto the netboot path — instead of using the collection's own shipped
`bluebanquise-netboots-installer` tool (`pxe_stack/files/`, installed to `/usr/bin/`). Migrated both
to the tool (Oxedions' explicit request): `sudo bluebanquise-netboots-installer install <netboot_id>
<arch> --netboot <local_iso_path> -q`, using the already-uploaded ISO via `--netboot` so the tool
never needs to download anything itself (still fully airgapped). `per_distro/17`'s cleanup now calls
`bluebanquise-netboots-installer uninstall <netboot_id> <arch> -q` (removing the tool's own managed
copy + extracted tree under `pxe/netboots/<os>/<version>/<arch>/`) followed by a manual `rm -f` of
the *separate* staging ISO copy at `/var/lib/bluebanquise/<iso>` that `per_distro/10` uploaded — the
tool's `install` action makes its own copy of whatever `--netboot` points at rather than referencing
it in place, so the two copies are genuinely distinct and both need cleaning up. `common.sh` gained
`DISTRO_NETBOOT_ID` (the `netboots_installer.yml` key per distro: `rhel_9`, `rhel_10`,
`ubuntu_24.04`, `debian_13`) and a fixed `DISTRO_NETBOOT_ARCH=x86_64`.

**Disk-usage note, not yet a problem but worth watching**: the tool's `install` (via `--netboot`)
copies the ISO into its managed directory *and* extracts its contents there — meaningfully more
transient disk usage per distro than the old bare-mount approach (which referenced the ISO in place,
no extra copy). Roughly: staging copy (`/var/lib/bluebanquise/<iso>`, unchanged) + the tool's own ISO
copy + the extracted tree, all live on mgt1 simultaneously until `per_distro/17` cleans up — for
rhel9's ~15GB ISO, on the order of 2-3x that transiently. Fit fine within mgt1's 60GB disk in
practice, but worth checking if a smaller disk is ever used.

**Transition gotcha, already handled**: `per_distro/17` now defensively `umount`s the old raw-mount
path before calling `uninstall`, since the tool's `rmtree`-based cleanup fails with "Device or
resource busy" against a directory that's still an active mount (exactly rhel9's state this session,
set up before this migration landed) — a one-time compatibility shim, harmless no-op for every future
distro once nothing is ever mounted there again.

### `firewall` role runs after `time` in our own playbooks — real bug, found live (2026-08-11)

`login1`'s very first `logins.yml` run failed at `time : firewalld <|> Add services to firewall's
zone` — `"firewall is not currently running, unable to perform immediate actions without a running
firewall daemon"`. `mgt1`/`mgmt_rhel9` never hit this in `managements_full.yml` purely by luck of role
order: several earlier roles there (`dhcp_server`, `dns_server`, `pxe_stack`) already touch firewalld
before `time` does, so by the time `time` runs, firewalld's already been started as a side effect.
`logins.yml`/`computes.yml` have no such earlier role — `time` is the *first* thing to touch
firewalld, and kickstart's `firewall --enabled` only enables the service for the *next* boot, it
doesn't start it immediately — so on a node's first-ever Ansible run, firewalld may not be active yet
at all.

**The real damage wasn't the failed task itself** (that alone would just fail cleanly) **— it was
what happened after.** The play aborted mid-`nic`-role-adjacent state, and networking was left up but
with firewalld now started (via systemd at some point) with **zero** BlueBanquise-managed zone
config — no `internal` zone services, nothing — leaving the node reachable for established/related
connections only. Rebooting to try to recover made it *worse*: every subsequent connection attempt
(`ping`, fresh SSH) was dropped outright (confirmed: `enp1s0` had the correct IP and was UP, per
`virsh qemu-agent-command ... guest-network-get-interfaces`, but `rx-dropped` was ~90% of
`rx-packets`). Could not diagnose further or fix in place — this host's `qemu-guest-agent` has
`guest-exec`/`guest-file-open` disabled at the libvirt policy level (`"the command is not allowed"`),
so there was no way to inspect or repair the node without a working SSH path, which is exactly what
was broken. Recovered by destroying and PXE-redeploying the node fresh (`per_distro/14`) rather than
debugging blind.

**Fixed at the actual root**: `firewall` role moved to run immediately after `nic` (before
`hosts_file`/`dns_client`/`time`/`dhcp_server`/etc.) in all three of this harness's own playbooks —
`logins.yml`, `computes.yml`, *and* `managements_full.yml` (which hadn't failed yet, but had the
identical latent ordering fragility, just masked). Not a BlueBanquise role bug — these are our own
harness-authored playbooks, and BlueBanquise's roles don't prescribe any particular relative order
among themselves; this is purely about *our* role list making sure `firewall` always runs early
enough that no later role's `immediate: true` firewalld task can ever race it again.

---

## testuser

- Username: `testuser`, uid: 1500, gid: 1500
- Home: `/home/testuser` (on NFS share from mgmt VM)
- Password: `"!"` (locked — only SSH key access from bluebanquise account via `sudo su - testuser`)
- Defined in `cluster/group_vars/all/users.yml` (identical across all distros)
- Home directory must be created manually on the mgmt VM before cluster nodes mount NFS (step 12 does this)

## Slurm test

From `login1` as `testuser`:
```bash
srun --nodes=2 --ntasks-per-node=1 hostname
```
Expected output: both `c001` and `c002` appear. Step 16 validates this and exits non-zero on failure (allowing cleanup to still run via `set +e` in `launch_v3.sh`).

---

## TODO: `pcs` (HA) role has zero test coverage anywhere — needs a Validation V3 step (added 2026-08)

Found during a `bluebanquise` repo coherency review of the `pcs` role: it is not in the tag list of
*any* `.github/workflows/*.yml` invocation of `high_availability.yml` — every workflow (el9, el10,
u24, deb13, lp16) runs `-t haproxy,keepalived` only, `pcs` is absent even on el9/el10/u24 where the
role claims support. Two real bugs (a `run_once`+`delegate_to`+`register` variable-scoping bug
picking the wrong host's data, and a colocation-constraint task that crashes on an integer `score`)
had evidently never been exercised as a result, and were only caught by hand.

**Why this repo's Docker-based CI can't just add the missing tag**: pacemaker/corosync are a
genuinely multi-host, network-quorum-dependent stack — the kind of thing `bluebanquise`'s own
container-based CI model (single container, `--connection=local --limit mgt1`, no real inter-host
networking or systemd corosync/pacemaker daemons under it) isn't built to exercise honestly. Forcing
it in there would risk the same trap already documented in `bluebanquise/AI/CLAUDE.md`'s CI/Testing
section ("container-only failure is a CI workflow problem, never grounds for touching role
behavior") in reverse — a container-shaped pass/fail on `pcs` wouldn't actually prove the role works
on real HA hardware, and a container-shaped *failure* could easily be a container artifact, not a
real bug, muddying the signal either way.

**Proposed home instead: a new Validation V3 step here**, since this harness already does real
multi-VM KVM deployment (unlike CI's single container) — the natural place to actually exercise
`pcs` end-to-end: real `corosync`/`pacemaker` on real (if virtual) separate hosts, real quorum
behavior, a real `pcs cluster node add` join. Not designed yet — needs its own host topology
decision (how many HA nodes, which existing step's VMs to repurpose or whether it needs dedicated
ones) before it can be scoped as a numbered step like 01-17 above. Flagging here as a known gap
rather than designing it blind; revisit when `pcs`/HA work is next prioritized.
