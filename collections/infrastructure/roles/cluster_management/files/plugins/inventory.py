#!/usr/bin/env python3
"""
Inventory plugin for bluebanquise-cluster.
Manage an ansible-inventory (hosts, fn_group/hw_group/os_group/custom groups, networks, host
network_interfaces and bmc) through a REST-shaped verb/path grammar. All the actual logic
(skeleton defaults, sub-resource addressing, data model invariants) lives in ansible_inventory.py,
a sibling library file installed by this same role (cluster_management) - this plugin is a thin
router: parse the command line, call the matching AnsibleInventory method, save(), report.

Usage:
  bluebanquise-cluster inventory <verb> <resource-path> [data] [--inventory <name>]

  verb ∈ add | get | update | remove          (POST / GET / PATCH / DELETE)
  data: key=value,key=value (one level)  OR  a JSON string, e.g. '{"a": {"b": 1}}'
  --inventory <name>: overrides the configured default_inventory for this call

Resource paths:
  fn_group/<name>                                  hw_group/<name>          os_group/<name>
  group/<name>                                      (custom group, no prefix rule, no skeleton)
  network/<name>
  host/<name>
  host/<name>/network_interface/<iface>
  host/<name>/bmc
  host/<name>/fn_group | hw_group | os_group        (single membership; update = move)
  host/<name>/group/<groupname>                     (multi membership; add/remove only)

Examples:
  bluebanquise-cluster inventory add fn_group/fn_workers
  bluebanquise-cluster inventory add hw_group/hw_supermicro_A hw_equipment_type=server
  bluebanquise-cluster inventory add os_group/os_ubuntu_24_04
  bluebanquise-cluster inventory add network/net-admin subnet=10.10.0.0,prefix=16,services_ip=10.10.0.1
  bluebanquise-cluster inventory add host/c001 fn_group=fn_workers,hw_group=hw_supermicro_A,os_group=os_ubuntu_24_04
  bluebanquise-cluster inventory add host/c001/network_interface/eno1 '{"ip4": "10.10.4.2", "network": "net-admin"}'
  bluebanquise-cluster inventory update host/c001/network_interface/eno1 ip4=10.10.4.1
  bluebanquise-cluster inventory update host/c001/fn_group fn_training_workers
  bluebanquise-cluster inventory get host/c001
  bluebanquise-cluster inventory remove host/c001/network_interface/eno1

Configuration: reads inventories_root/working_folder/default_inventory from
config['inventory_conf_path'] (see cluster_management's README / defaults/main.yml -
cluster_management_tools_inventory_conf_path, default /etc/bluebanquise/cluster_inventory.conf).
"""

import argparse
import importlib.util
import json
import os
import sys

import yaml

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

VERBS = ('add', 'get', 'update', 'remove')
GROUP_KINDS = ('fn_group', 'hw_group', 'os_group', 'group')


def _load_ansible_inventory_lib(plugins_path):
    """ansible_inventory.py is installed next to (not inside) plugins/, same layout as
    state_diff.py/events.py - see state.py's _load_state_diff() for the same derivation."""
    lib_dir = os.path.dirname(plugins_path.rstrip('/'))
    lib_path = os.path.join(lib_dir, 'ansible_inventory.py')
    if not os.path.isfile(lib_path):
        print(f'ansible_inventory.py not found at {lib_path} (cluster_management installation '
              'incomplete?)', file=sys.stderr)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location('ansible_inventory_lib', lib_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, os.path.join(lib_dir, 'inventory_skeletons')


def _load_inventory_config(conf_path):
    if not conf_path or not os.path.isfile(conf_path):
        print(f'Inventory configuration file not found at {conf_path} - run the '
              'cluster_management role first.', file=sys.stderr)
        sys.exit(1)
    with open(conf_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _parse_data(raw):
    """key=value,key=value (one level) or a JSON string. Bare kv values get light type
    coercion (int/float/bool) since everything from the shell is otherwise a string; JSON
    values already carry their own types."""
    if raw is None:
        return {}
    stripped = raw.strip()
    if stripped.startswith('{'):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError as exc:
            print(f'Invalid JSON data: {exc}', file=sys.stderr)
            sys.exit(1)
    data = {}
    for pair in stripped.split(','):
        if not pair:
            continue
        if '=' not in pair:
            print(f'Invalid data segment {pair!r}, expected key=value', file=sys.stderr)
            sys.exit(1)
        key, _, value = pair.partition('=')
        data[key.strip()] = _coerce_scalar(value.strip())
    return data


def _coerce_scalar(value):
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _print_usage():
    print(__doc__)


def _fail(message):
    print(RED + message + RESET, file=sys.stderr)
    sys.exit(1)


def _succeed(message):
    print(GREEN + message + RESET)


def _print_yaml(data):
    print(yaml.safe_dump(data, default_flow_style=False, sort_keys=False))


def run(args, config):
    if len(args) < 2:
        _print_usage()
        sys.exit(1)

    verb = args[0]
    path = args[1]
    rest = args[2:]

    if verb not in VERBS:
        _fail(f'Unknown verb {verb!r}, expected one of {", ".join(VERBS)}')

    parser = argparse.ArgumentParser(prog=f'inventory {verb}', add_help=False)
    parser.add_argument('data', nargs='?', default=None)
    parser.add_argument('--inventory', default=None)
    parsed = parser.parse_args(rest)

    segments = [s for s in path.strip('/').split('/') if s]
    if not segments:
        _fail(f'Invalid resource path {path!r}')

    ansible_inventory_lib, skeletons_path = _load_ansible_inventory_lib(config['plugins_path'])
    inv_config = _load_inventory_config(config.get('inventory_conf_path'))
    inventory_name = parsed.inventory or inv_config.get('default_inventory')
    if not inventory_name:
        _fail('No inventory specified: pass --inventory <name> or set default_inventory in '
              'the inventory configuration file')

    try:
        inventory = ansible_inventory_lib.AnsibleInventory(
            inventories_root=inv_config['inventories_root'],
            inventory_name=inventory_name,
            working_folder=inv_config['working_folder'],
            skeletons_path=skeletons_path,
        )
        _dispatch(inventory, verb, segments, parsed.data)
    except ansible_inventory_lib.InventoryError as exc:
        _fail(str(exc))


def _dispatch(inventory, verb, segments, raw_data):
    # ── top-level groups: fn_group/<name>, hw_group/<name>, os_group/<name>, group/<name> ──
    if len(segments) == 2 and segments[0] in GROUP_KINDS:
        kind, name = segments
        if verb == 'add':
            inventory.add_group(name, kind, _parse_data(raw_data))
            inventory.save()
            _succeed(f'{kind} {name!r} created.')
        elif verb == 'get':
            _print_yaml(inventory.get_group(name))
        elif verb == 'update':
            inventory.update_group_vars(name, _parse_data(raw_data))
            inventory.save()
            _succeed(f'{kind} {name!r} updated.')
        elif verb == 'remove':
            inventory.delete_group(name)
            inventory.save()
            _succeed(f'{kind} {name!r} deleted.')
        return

    # ── network/<name> ──
    if len(segments) == 2 and segments[0] == 'network':
        name = segments[1]
        if verb == 'add':
            inventory.add_network(name, _parse_data(raw_data))
            inventory.save()
            _succeed(f'Network {name!r} created.')
        elif verb == 'get':
            _print_yaml(inventory.get_network(name))
        elif verb == 'update':
            inventory.update_network(name, _parse_data(raw_data))
            inventory.save()
            _succeed(f'Network {name!r} updated.')
        elif verb == 'remove':
            inventory.delete_network(name)
            inventory.save()
            _succeed(f'Network {name!r} deleted.')
        return

    # ── host/<name> ──
    if len(segments) == 2 and segments[0] == 'host':
        name = segments[1]
        if verb == 'add':
            data = _parse_data(raw_data)
            missing = [k for k in ('fn_group', 'hw_group', 'os_group') if k not in data]
            if missing:
                _fail(f'add host requires {", ".join(missing)} in the data')
            fn_group = data.pop('fn_group')
            hw_group = data.pop('hw_group')
            os_group = data.pop('os_group')
            inventory.add_host(name, fn_group, hw_group, os_group, data)
            inventory.save()
            _succeed(f'Host {name!r} created.')
        elif verb == 'get':
            _print_yaml(inventory.get_host(name))
        elif verb == 'update':
            inventory.update_host_vars(name, _parse_data(raw_data))
            inventory.save()
            _succeed(f'Host {name!r} updated.')
        elif verb == 'remove':
            inventory.delete_host(name)
            inventory.save()
            _succeed(f'Host {name!r} deleted.')
        return

    # ── host/<name>/network_interface/<iface> ──
    if len(segments) == 4 and segments[0] == 'host' and segments[2] == 'network_interface':
        _, hostname, _, iface = segments
        if verb == 'add':
            data = _parse_data(raw_data)
            data['interface'] = iface
            inventory.add_host_network_interface(hostname, data)
            inventory.save()
            _succeed(f'Interface {iface!r} added to host {hostname!r}.')
        elif verb == 'get':
            host = inventory.get_host(hostname)
            match = next((i for i in host.get('network_interfaces', []) if i.get('interface') == iface), None)
            if match is None:
                _fail(f'Interface {iface!r} does not exist on host {hostname!r}')
            _print_yaml(match)
        elif verb == 'update':
            inventory.update_host_network_interface(hostname, iface, _parse_data(raw_data))
            inventory.save()
            _succeed(f'Interface {iface!r} updated on host {hostname!r}.')
        elif verb == 'remove':
            inventory.remove_host_network_interface(hostname, iface)
            inventory.save()
            _succeed(f'Interface {iface!r} removed from host {hostname!r}.')
        return

    # ── host/<name>/bmc ──
    if len(segments) == 3 and segments[0] == 'host' and segments[2] == 'bmc':
        _, hostname, _ = segments
        if verb == 'add':
            inventory.add_host_bmc(hostname, _parse_data(raw_data))
            inventory.save()
            _succeed(f'bmc added to host {hostname!r}.')
        elif verb == 'get':
            _print_yaml(inventory.get_host(hostname).get('bmc', {}))
        elif verb == 'update':
            inventory.update_host_bmc(hostname, _parse_data(raw_data))
            inventory.save()
            _succeed(f'bmc updated on host {hostname!r}.')
        elif verb == 'remove':
            inventory.remove_host_bmc(hostname)
            inventory.save()
            _succeed(f'bmc removed from host {hostname!r}.')
        return

    # ── host/<name>/fn_group|hw_group|os_group (single membership) ──
    if len(segments) == 3 and segments[0] == 'host' and segments[2] in ('fn_group', 'hw_group', 'os_group'):
        _, hostname, kind = segments
        if verb == 'get':
            current = [n for n, g in inventory.get_groups(kind).items() if hostname in g['hosts']]
            _print_yaml({kind: current[0] if current else None})
        elif verb == 'update':
            if not raw_data:
                _fail(f'update host/{hostname}/{kind} requires the target group name as data')
            inventory.add_host_to_group(hostname, raw_data.strip())
            inventory.save()
            _succeed(f'Host {hostname!r} moved to {kind} {raw_data.strip()!r}.')
        else:
            _fail(f'{verb} is not supported on host/{hostname}/{kind} - it is a mandatory '
                  'membership, use update to move it')
        return

    # ── host/<name>/group/<groupname> (multi membership) ──
    if len(segments) == 4 and segments[0] == 'host' and segments[2] == 'group':
        _, hostname, _, group_name = segments
        if verb == 'add':
            inventory.add_host_to_group(hostname, group_name)
            inventory.save()
            _succeed(f'Host {hostname!r} added to group {group_name!r}.')
        elif verb == 'remove':
            inventory.remove_host_from_group(hostname, group_name)
            inventory.save()
            _succeed(f'Host {hostname!r} removed from group {group_name!r}.')
        else:
            _fail(f'{verb} is not supported on host/{hostname}/group/{group_name} - use add/remove')
        return

    _fail(f'Unrecognized resource path: {"/".join(segments)}')
