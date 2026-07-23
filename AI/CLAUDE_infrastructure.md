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
| rhel9 | AlmaLinux-9-latest-x86_64-dvd.iso | repo.almalinux.org/almalinux/9/isos/x86_64/ |
| rhel10 | AlmaLinux-10-latest-x86_64-dvd.iso | repo.almalinux.org/almalinux/10/isos/x86_64/ |
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

The Ubuntu 24.04 autoinstall fails with 8 GB RAM. Use `--ram=12000` for the install; step 03 reduces it to 4 GB at runtime after installation completes.

---

## Playbooks reference

### `managements_full.yml` (run on the mgmt VM as `--limit mgt`)
Roles in order: `repositories`, `set_hostname`, `http_server`, `nic`, `hosts_file`, `dhcp_server`, `dns_server`, `clustershell`, `pxe_stack`, `time` (profile: server), `firewall`, `nfs` (profile: server), `slurm` (profile: controller), `users`

### `logins.yml` (run on `login1`)
Roles: `repositories`, `set_hostname`, `nic`, `hosts_file`, `dns_client`, `time` (profile: client), `firewall`, `nfs` (profile: client), `slurm` (profile: submitter), `users`

### `computes.yml` (run on `c001`, `c002`)
Roles: `repositories`, `set_hostname`, `nic`, `hosts_file`, `dns_client`, `time` (profile: client), `firewall`, `nfs` (profile: client), `slurm` (profile: compute), `users`

---

## Current test status (as of 2026-07-10)

### What passed

- Step 01: networks (virbr1 + virbr2 created and active)
- Step 02: HTTP server
- Step 03: mgt1 cloud-init install (Ubuntu 24.04.4, 12 GB RAM during install)
- Step 04 (partial): BB bootstrap on mgt1 succeeded up to and including the Ansible run:

```
ansible-playbook playbooks/managements_full.yml -i mgt1_bootstrap --limit mgt1 -b
```

### What failed

One of the roles in `managements_full.yml` failed on mgt1. The specific role and error are not yet identified — this is the next thing to investigate.

**To resume:** Start a new session, read this file, ask Oxedions for the Ansible error output from the failed run, identify the failing role, fix it in `collections/infrastructure/roles/<name>/`, then re-run from `STEP=3` (or `STEP=4` if mgt1 is still up and reachable).

### Next steps

1. Get the full Ansible error output from the `managements_full.yml` run on mgt1.
2. Identify and fix the failing role.
3. Re-run `ansible-playbook playbooks/managements_full.yml -i mgt1_bootstrap --limit mgt1 -b` on mgt1 (no need to rebuild the VM if it is still up).
4. Continue with step 10 (per-distro loop) once mgt1 stack is clean.

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
