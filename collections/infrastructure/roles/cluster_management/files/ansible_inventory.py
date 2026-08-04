#!/usr/bin/env python3
"""
AnsibleInventory - load/edit/save a BlueBanquise-managed Ansible inventory, then git-commit the
result. Shared library for the `inventory` bluebanquise-cluster plugin, and meant to back a
future Flask REST server on the same code - all resource-shaping logic (skeletons, sub-resource
addressing, group-kind rules) lives here so both clients stay thin routers over one implementation.

v1 assumes the inventory tree was created by this same module: hosts are always written as
explicit lists (never ClusterShell/Ansible nodeset ranges - the two use incompatible range
syntaxes anyway), and group_vars/host_vars are always a single main.yml per group/host. Loading a
hand-authored inventory using ranges, extensionless group files, or several arbitrarily-named
group_vars files per group is out of scope.

Layout, per inventory (see AnsibleInventory._ensure_inventory_exists() for how
<inventories_root>/<inventory_name>/ is bootstrapped on first use):

  <inventories_root>/                 one git repo, git-init'd on first use
    <inventory_name>/
      cluster/
        hosts/<fn_group>.yml          {"all": {"hosts": {...}}}, one file per fn group
        groups/<group>.ini            membership, one file per non-"all" group
      group_vars/<group>/main.yml     always exactly this one file, no per-key file splitting
      host_vars/<host>/main.yml       always exactly this one file

No locking: v1 is a single-shot CLI process. A future concurrent REST server built on this class
will need per-inventory locking around load/mutate/save - not addressed here.
"""

import configparser
import copy
import glob
import os
import shutil
import subprocess
import tempfile

import yaml


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class InventoryError(Exception):
    """Base class for every error AnsibleInventory raises - callers (CLI, REST) can catch this
    alone, or one of the subclasses below to react differently (404 vs 409 vs 400, ...)."""


class ResourceExistsError(InventoryError):
    """Raised when creating a resource (host, group, network, ...) that already exists."""


class ResourceNotFoundError(InventoryError):
    """Raised when referencing a resource that does not exist."""


class ValidationError(InventoryError):
    """Raised when supplied data fails skeleton/required-field validation, or breaks a data
    model invariant (e.g. deleting a group that still has member hosts)."""


# ─────────────────────────────────────────────────────────────────────────────
# YAML / INI helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_yaml_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def load_ini_file(path):
    parser = configparser.ConfigParser(allow_no_value=True, delimiters=("=",))
    parser.optionxform = str  # keep hostname case
    with open(path, "r", encoding="utf-8") as f:
        parser.read_file(f)
    return parser


def deep_merge(base, override):
    """Return a new dict: `override` merged onto a copy of `base`, recursing into nested dicts.
    Lists and scalars in `override` replace the corresponding value in `base` outright - only
    dict-vs-dict recurses, so e.g. supplying one key of a nested dict (os_operating_system:
    {distribution_version: ...}) keeps the skeleton's sibling keys instead of dropping them."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def get_by_path(data, dotted_path):
    """Walk a dotted path ("os_operating_system.distribution") into a dict, return the value
    found or None if any segment is missing - used for required-field checks after a skeleton
    merge."""
    current = data
    for segment in dotted_path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


# ─────────────────────────────────────────────────────────────────────────────
# Skeletons
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_SKELETONS_PATH = "/usr/local/lib/bluebanquise/cluster/inventory_skeletons"

# fn_group/hw_group/os_group prefixes, per resources/data_model.md section 3. Anything else is a
# custom "group" - no prefix rule, no skeleton.
GROUP_KIND_PREFIXES = {
    "fn_group": "fn_",
    "hw_group": "hw_",
    "os_group": "os_",
}

# Host bucket used for write_inventory() when a host is in no fn_ group yet - kept distinct from
# a real group name (no fn_ prefix, leading underscore) so it can never collide with an operator-
# named fn_ group.
UNASSIGNED_FN_BUCKET = "_unassigned"


def load_skeletons(skeletons_path):
    """Scan `skeletons_path` for *.yml files, return {resource_type: {"skeleton": {...},
    "required": [...]}}. resource_type is the filename without extension. A missing/empty
    directory yields an empty index - every add_* method below then simply applies no skeleton,
    it never fails because skeletons are absent."""
    index = {}
    if not os.path.isdir(skeletons_path):
        return index
    for path in sorted(glob.glob(os.path.join(skeletons_path, "*.yml"))):
        resource_type = os.path.splitext(os.path.basename(path))[0]
        content = load_yaml_file(path)
        index[resource_type] = {
            "skeleton": content.get("skeleton", {}),
            "required": content.get("required", []),
        }
    return index


def group_kind_from_name(name):
    for kind, prefix in GROUP_KIND_PREFIXES.items():
        if name.startswith(prefix):
            return kind
    return "group"


# ─────────────────────────────────────────────────────────────────────────────
# AnsibleInventory
# ─────────────────────────────────────────────────────────────────────────────

class AnsibleInventory:
    """
    Represents one BlueBanquise-managed Ansible inventory, rooted at
    <inventories_root>/<inventory_name>/. See module docstring for the on-disk layout.
    """

    def __init__(
        self,
        inventories_root,
        inventory_name,
        working_folder,
        skeletons_path=DEFAULT_SKELETONS_PATH,
        check=False,
        logger=None,
    ):
        self.inventories_root = os.path.abspath(inventories_root)
        self.inventory_name = inventory_name
        self.inventory_root = os.path.join(self.inventories_root, inventory_name)
        self.working_folder = os.path.abspath(working_folder)
        self.check = check
        self.logger = logger

        self.skeletons = load_skeletons(skeletons_path)

        created = self._ensure_inventory_exists()

        self.hosts = {}
        self.groups = {}
        self.load_inventory()

        if created:
            all_skeleton = self.skeletons.get("all_group", {}).get("skeleton", {})
            self.groups["all"]["vars"] = deep_merge(self.groups["all"]["vars"], all_skeleton)
            if not self.check:
                self.save()

    def _log(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

    def _run_git(self, args, check_exit_code=True):
        try:
            return subprocess.run(args, capture_output=True, text=True, check=check_exit_code)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise InventoryError(f"git command failed ({' '.join(args)}): {exc}") from exc

    # ####################################################################################
    # ##### Bootstrap
    # ##

    def _ensure_inventory_exists(self):
        """Create inventories_root (+ git init it) if missing, then create this inventory's
        folder skeleton if missing. Returns True if the inventory folder was just created - the
        caller then still needs to apply the all_group skeleton and save()."""
        os.makedirs(self.inventories_root, exist_ok=True)
        os.makedirs(self.working_folder, exist_ok=True)

        if not os.path.isdir(os.path.join(self.inventories_root, ".git")):
            self._log(f"Initializing git repository at {self.inventories_root}")
            self._run_git(["git", "init", self.inventories_root])

        if os.path.isdir(self.inventory_root):
            return False

        self._log(f"Creating new inventory {self.inventory_name!r} at {self.inventory_root}")
        os.makedirs(os.path.join(self.inventory_root, "cluster", "hosts"), exist_ok=True)
        os.makedirs(os.path.join(self.inventory_root, "cluster", "groups"), exist_ok=True)
        os.makedirs(os.path.join(self.inventory_root, "group_vars"), exist_ok=True)
        os.makedirs(os.path.join(self.inventory_root, "host_vars"), exist_ok=True)
        return True

    # ####################################################################################
    # ##### Load
    # ##

    def load_inventory(self):
        self.load_hosts()
        self.load_groups()

    def load_hosts(self):
        self.hosts = {}

        hosts_dir = os.path.join(self.inventory_root, "cluster", "hosts")
        if not os.path.isdir(hosts_dir):
            return

        for fname in sorted(os.listdir(hosts_dir)):
            if not fname.endswith(".yml") and not fname.endswith(".yaml"):
                continue
            buffer_data = load_yaml_file(os.path.join(hosts_dir, fname))
            hosts_section = buffer_data.get("all", {}).get("hosts", {}) or {}
            self.hosts.update(hosts_section)

        for hostname in self.hosts:
            if self.hosts[hostname] is None:
                self.hosts[hostname] = {}
            hv_path = os.path.join(self.inventory_root, "host_vars", hostname, "main.yml")
            if os.path.isfile(hv_path):
                self.hosts[hostname].update(load_yaml_file(hv_path) or {})

    def load_groups(self):
        self.groups = {"all": {"hosts": [], "vars": {}}}

        groups_dir = os.path.join(self.inventory_root, "cluster", "groups")
        if os.path.isdir(groups_dir):
            for fname in sorted(os.listdir(groups_dir)):
                if not fname.endswith(".ini"):
                    continue
                group_name = os.path.splitext(fname)[0]
                if group_name == "all":
                    continue
                parser = load_ini_file(os.path.join(groups_dir, fname))
                hosts_list = list(parser.options(group_name)) if parser.has_section(group_name) else []
                self.groups[group_name] = {"hosts": hosts_list, "vars": {}}

        # group_vars: flat-merge every *.yml file found directly into vars, matching real
        # Ansible semantics (see resources/examples/simple_cluster/group_vars/all/*.yml) - even
        # though write_inventory() only ever produces a single main.yml, loading stays tolerant
        # of any filename so nothing silently nests on the next save().
        for group_name in self.groups:
            gv_dir = os.path.join(self.inventory_root, "group_vars", group_name)
            if not os.path.isdir(gv_dir):
                continue
            merged = {}
            for fname in sorted(os.listdir(gv_dir)):
                if not fname.endswith(".yml") and not fname.endswith(".yaml"):
                    continue
                merged.update(load_yaml_file(os.path.join(gv_dir, fname)) or {})
            self.groups[group_name]["vars"] = merged

    # ####################################################################################
    # ##### Skeletons
    # ##

    def _apply_skeleton(self, resource_type, data):
        """Deep-merge `data` over the resource_type's skeleton (if any), validate required
        fields, return the merged dict. Resource types with no skeleton file (fn_group, custom
        group) just pass `data` through unchanged."""
        data = data or {}
        spec = self.skeletons.get(resource_type)
        if spec is None:
            return copy.deepcopy(data)
        merged = deep_merge(spec["skeleton"], data)
        missing = [field for field in spec["required"] if not get_by_path(merged, field)]
        if missing:
            raise ValidationError(
                f"{resource_type} is missing required field(s): {', '.join(missing)}"
            )
        return merged

    # ####################################################################################
    # ##### Groups
    # ##

    def _validate_group_kind(self, name, kind):
        if kind not in ("fn_group", "hw_group", "os_group", "group"):
            raise ValidationError(f"Unknown group kind {kind!r}")
        prefix = GROUP_KIND_PREFIXES.get(kind)
        if prefix and not name.startswith(prefix):
            raise ValidationError(f"{kind} name {name!r} must start with {prefix!r}")

    def add_group(self, name, kind, data=None):
        if name in self.groups:
            raise ResourceExistsError(f"Group {name!r} already exists")
        self._validate_group_kind(name, kind)
        vars_data = self._apply_skeleton(kind, data)
        self.groups[name] = {"hosts": [], "vars": vars_data}

    def get_group(self, name):
        if name not in self.groups:
            raise ResourceNotFoundError(f"Group {name!r} does not exist")
        return self.groups[name]

    def get_groups(self, kind=None):
        if kind is None:
            return self.groups
        if kind == "group":
            known_prefixes = tuple(GROUP_KIND_PREFIXES.values())
            return {
                n: g for n, g in self.groups.items()
                if n != "all" and not n.startswith(known_prefixes)
            }
        prefix = GROUP_KIND_PREFIXES.get(kind)
        if prefix is None:
            raise ValidationError(f"Unknown group kind {kind!r}")
        return {n: g for n, g in self.groups.items() if n.startswith(prefix)}

    def update_group_vars(self, name, data):
        if name not in self.groups:
            raise ResourceNotFoundError(f"Group {name!r} does not exist")
        self.groups[name]["vars"] = deep_merge(self.groups[name]["vars"], data)

    def set_group_hosts(self, name, hosts):
        if name not in self.groups:
            raise ResourceNotFoundError(f"Group {name!r} does not exist")
        self.groups[name]["hosts"] = list(hosts)

    def delete_group(self, name):
        if name == "all":
            raise ValidationError("The 'all' group cannot be deleted")
        if name not in self.groups:
            raise ResourceNotFoundError(f"Group {name!r} does not exist")
        kind = group_kind_from_name(name)
        member_hosts = self.groups[name]["hosts"]
        if kind in ("fn_group", "hw_group", "os_group") and member_hosts:
            raise ValidationError(
                f"Group {name!r} still has member hosts ({', '.join(sorted(member_hosts))}); "
                "reassign them before deleting"
            )
        del self.groups[name]

    # ####################################################################################
    # ##### Hosts
    # ##

    def get_hosts(self):
        return self.hosts

    def get_host(self, name):
        if name not in self.hosts:
            raise ResourceNotFoundError(f"Host {name!r} does not exist")
        return self.hosts[name]

    def add_host(self, name, fn_group, hw_group, os_group, data=None):
        if name in self.hosts:
            raise ResourceExistsError(f"Host {name!r} already exists")
        for group_name in (fn_group, hw_group, os_group):
            if group_name not in self.groups:
                raise ResourceNotFoundError(
                    f"Group {group_name!r} does not exist - create it before assigning a host to it"
                )
        data = data or {}
        self.hosts[name] = {
            "alias": data.get("alias"),
            "network_interfaces": data.get("network_interfaces", []),
            "bmc": data.get("bmc", {}),
        }
        extra_vars = {k: v for k, v in data.items() if k not in ("alias", "network_interfaces", "bmc")}
        self.hosts[name].update(extra_vars)
        for group_name in (fn_group, hw_group, os_group):
            self.groups[group_name]["hosts"].append(name)

    def update_host_vars(self, name, data):
        if name not in self.hosts:
            raise ResourceNotFoundError(f"Host {name!r} does not exist")
        self.hosts[name] = deep_merge(self.hosts[name], data)

    def delete_host(self, name):
        if name not in self.hosts:
            raise ResourceNotFoundError(f"Host {name!r} does not exist")
        del self.hosts[name]
        for group_data in self.groups.values():
            if name in group_data["hosts"]:
                group_data["hosts"].remove(name)

    def add_host_to_group(self, hostname, group_name):
        if hostname not in self.hosts:
            raise ResourceNotFoundError(f"Host {hostname!r} does not exist")
        if group_name not in self.groups:
            raise ResourceNotFoundError(f"Group {group_name!r} does not exist")
        kind = group_kind_from_name(group_name)
        if kind in ("fn_group", "hw_group", "os_group"):
            # Exactly one membership of this kind per the data model - drop any existing one.
            for other_name, other_data in self.groups.items():
                if other_name != group_name and group_kind_from_name(other_name) == kind:
                    if hostname in other_data["hosts"]:
                        other_data["hosts"].remove(hostname)
        if hostname not in self.groups[group_name]["hosts"]:
            self.groups[group_name]["hosts"].append(hostname)

    def remove_host_from_group(self, hostname, group_name):
        if group_name not in self.groups:
            raise ResourceNotFoundError(f"Group {group_name!r} does not exist")
        if hostname in self.groups[group_name]["hosts"]:
            self.groups[group_name]["hosts"].remove(hostname)

    # ####################################################################################
    # ##### Host network interfaces
    # ##

    def add_host_network_interface(self, hostname, data):
        if hostname not in self.hosts:
            raise ResourceNotFoundError(f"Host {hostname!r} does not exist")
        entry = self._apply_skeleton("network_interface", data)
        interfaces = self.hosts[hostname].setdefault("network_interfaces", [])
        if any(i.get("interface") == entry["interface"] for i in interfaces):
            raise ResourceExistsError(
                f"Interface {entry['interface']!r} already exists on host {hostname!r}"
            )
        interfaces.append(entry)

    def update_host_network_interface(self, hostname, interface_name, data):
        if hostname not in self.hosts:
            raise ResourceNotFoundError(f"Host {hostname!r} does not exist")
        interfaces = self.hosts[hostname].get("network_interfaces", [])
        for index, entry in enumerate(interfaces):
            if entry.get("interface") == interface_name:
                interfaces[index] = deep_merge(entry, data)
                return
        raise ResourceNotFoundError(f"Interface {interface_name!r} does not exist on host {hostname!r}")

    def remove_host_network_interface(self, hostname, interface_name):
        if hostname not in self.hosts:
            raise ResourceNotFoundError(f"Host {hostname!r} does not exist")
        interfaces = self.hosts[hostname].get("network_interfaces", [])
        for index, entry in enumerate(interfaces):
            if entry.get("interface") == interface_name:
                del interfaces[index]
                return
        raise ResourceNotFoundError(f"Interface {interface_name!r} does not exist on host {hostname!r}")

    # ####################################################################################
    # ##### Host BMC
    # ##

    def add_host_bmc(self, hostname, data):
        if hostname not in self.hosts:
            raise ResourceNotFoundError(f"Host {hostname!r} does not exist")
        if self.hosts[hostname].get("bmc"):
            raise ResourceExistsError(f"Host {hostname!r} already has a bmc defined")
        self.hosts[hostname]["bmc"] = self._apply_skeleton("bmc", data)

    def update_host_bmc(self, hostname, data):
        if hostname not in self.hosts:
            raise ResourceNotFoundError(f"Host {hostname!r} does not exist")
        if not self.hosts[hostname].get("bmc"):
            raise ResourceNotFoundError(f"Host {hostname!r} has no bmc defined")
        self.hosts[hostname]["bmc"] = deep_merge(self.hosts[hostname]["bmc"], data)

    def remove_host_bmc(self, hostname):
        if hostname not in self.hosts:
            raise ResourceNotFoundError(f"Host {hostname!r} does not exist")
        self.hosts[hostname]["bmc"] = {}

    # ####################################################################################
    # ##### Networks (group_vars/all/main.yml's "networks" key)
    # ##

    def _networks(self):
        return self.groups["all"]["vars"].setdefault("networks", {})

    def add_network(self, name, data):
        networks = self._networks()
        if name in networks:
            raise ResourceExistsError(f"Network {name!r} already exists")
        networks[name] = self._apply_skeleton("network", data)

    def get_network(self, name):
        networks = self._networks()
        if name not in networks:
            raise ResourceNotFoundError(f"Network {name!r} does not exist")
        return networks[name]

    def get_networks(self):
        return self._networks()

    def update_network(self, name, data):
        networks = self._networks()
        if name not in networks:
            raise ResourceNotFoundError(f"Network {name!r} does not exist")
        networks[name] = deep_merge(networks[name], data)

    def delete_network(self, name):
        networks = self._networks()
        if name not in networks:
            raise ResourceNotFoundError(f"Network {name!r} does not exist")
        del networks[name]

    # ####################################################################################
    # ##### Save
    # ##

    def save(self):
        """
        Write the in-memory inventory to disk and git-commit the result.

        - Always writes to a fresh temporary tree under working_folder first.
        - In check mode: print a diff against the real inventory_root and stop - nothing on disk
          is touched, no commit happens.
        - Otherwise: replace inventory_root's contents with the temporary tree, then commit.
        """
        tmp_dir = tempfile.mkdtemp(prefix="bluebanquise-inventory-", dir=self.working_folder)
        try:
            self.write_inventory(tmp_dir)

            if self.check:
                self._print_diff(self.inventory_root, tmp_dir)
                return

            if os.path.isdir(self.inventory_root):
                shutil.rmtree(self.inventory_root)
            shutil.copytree(tmp_dir, self.inventory_root)
        finally:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)

        self._commit_change()

    def write_inventory(self, root):
        self._write_hosts(root)
        self._write_host_vars(root)
        self._write_groups(root)

    def _host_fn_group(self, hostname):
        for group_name, group_data in self.groups.items():
            if group_name.startswith("fn_") and hostname in group_data["hosts"]:
                return group_name
        return None

    def _write_hosts(self, root):
        hosts_by_fn = {}
        for hostname in self.hosts:
            fn_group = self._host_fn_group(hostname) or UNASSIGNED_FN_BUCKET
            hosts_by_fn.setdefault(fn_group, []).append(hostname)

        hosts_dir = os.path.join(root, "cluster", "hosts")
        for fn_group, hostnames in hosts_by_fn.items():
            payload = {"all": {"hosts": {}}}
            for hostname in sorted(hostnames):
                host_data = self.hosts[hostname]
                entry = {}
                if host_data.get("alias"):
                    entry["alias"] = host_data["alias"]
                if host_data.get("network_interfaces"):
                    entry["network_interfaces"] = host_data["network_interfaces"]
                if host_data.get("bmc"):
                    entry["bmc"] = host_data["bmc"]
                payload["all"]["hosts"][hostname] = entry
            dump_yaml_file(os.path.join(hosts_dir, fn_group + ".yml"), payload)

    def _write_host_vars(self, root):
        for hostname, host_data in self.hosts.items():
            host_vars = {k: v for k, v in host_data.items() if k not in ("alias", "network_interfaces", "bmc")}
            if host_vars:
                dump_yaml_file(os.path.join(root, "host_vars", hostname, "main.yml"), host_vars)

    def _write_groups(self, root):
        groups_dir = os.path.join(root, "cluster", "groups")
        os.makedirs(groups_dir, exist_ok=True)

        for group_name, group_data in self.groups.items():
            if group_name != "all":
                # "all" membership is implicit in Ansible - it never gets a membership file.
                ini_path = os.path.join(groups_dir, group_name + ".ini")
                lines = [f"[{group_name}]"] + list(group_data["hosts"])
                with open(ini_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")

            if group_data["vars"]:
                dump_yaml_file(
                    os.path.join(root, "group_vars", group_name, "main.yml"),
                    group_data["vars"],
                )

    def _print_diff(self, old_root, new_root):
        try:
            result = subprocess.run(["diff", "-ruN", old_root, new_root], capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr and self.logger:
                self.logger.warning(f"diff stderr: {result.stderr.strip()}")
        except FileNotFoundError:
            self._log("diff binary not found; cannot show diff")

    def _commit_change(self):
        git_dir = os.path.join(self.inventories_root, ".git")
        work_tree = self.inventories_root

        self._run_git(
            ["git", "--git-dir", git_dir, "--work-tree", work_tree, "add", "-A", self.inventory_name]
        )
        result = self._run_git(
            [
                "git", "--git-dir", git_dir, "--work-tree", work_tree,
                "commit", "-m", f"Updating inventory {self.inventory_name}",
            ],
            check_exit_code=False,
        )
        if result.returncode == 0:
            self._log(f"Committed inventory changes: {self.inventory_name}")
        elif "nothing to commit" in result.stdout:
            self._log(f"No changes to commit for inventory {self.inventory_name}")
        else:
            self._log(f"git commit failed: {result.stderr.strip()}")
