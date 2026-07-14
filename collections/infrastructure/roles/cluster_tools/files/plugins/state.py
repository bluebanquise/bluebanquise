#!/usr/bin/env python3
"""
State plugin for bluebanquise-cluster.
Displays static inventory state and dynamic live state with drift detection.

Usage:
  bluebanquise-cluster state host <hostname>   display one host
  bluebanquise-cluster state all               display all hosts
  bluebanquise-cluster state error             display only hosts with drift
"""

import glob
import os
import sys
import yaml

GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

# Fields extracted into the DYNAMIC header line; omitted from the body.
HEADER_FIELDS = {'last_updated', 'ping', 'ssh'}


def run(args, config):
    base_path = config['base_path']

    if not args:
        _print_usage()
        sys.exit(1)

    subcommand = args[0]
    sub_args = args[1:]

    if subcommand == 'host':
        if not sub_args:
            print('Usage: bluebanquise-cluster state host <hostname>')
            sys.exit(1)
        _display_host(sub_args[0], base_path)

    elif subcommand == 'all':
        for hostname in _all_hosts(base_path):
            _display_host(hostname, base_path)

    elif subcommand == 'error':
        for hostname in _all_hosts(base_path):
            static, dynamic = _load_host(hostname, base_path)
            if dynamic and _has_drift(dynamic, static):
                _display_host(hostname, base_path, static=static, dynamic=dynamic)

    else:
        print('Unknown subcommand: {!r}'.format(subcommand))
        print()
        _print_usage()
        sys.exit(1)


def _print_usage():
    print('Usage:')
    print('  bluebanquise-cluster state host <hostname>  display one host')
    print('  bluebanquise-cluster state all              display all hosts')
    print('  bluebanquise-cluster state error            display hosts with drift')


# ─── host discovery ───────────────────────────────────────────────────────────

def _all_hosts(base_path):
    if not os.path.isdir(base_path):
        print('Base path not found: {}'.format(base_path))
        sys.exit(1)
    return sorted(
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d))
    )


# ─── data loading ─────────────────────────────────────────────────────────────

def _load_host(hostname, base_path):
    host_dir = os.path.join(base_path, hostname)
    static = _load_glob(os.path.join(host_dir, 'static_*.yml'))
    dynamic = _load_glob(os.path.join(host_dir, 'dynamic_*.yml'))
    return static, dynamic


def _load_glob(pattern):
    """Load and deep-merge all YAML files matching pattern. Later files win on conflict."""
    result = {}
    for filepath in sorted(glob.glob(pattern)):
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                _deep_merge(result, data)
        except Exception as e:
            print('Warning: could not load {}: {}'.format(filepath, e), file=sys.stderr)
    return result


def _deep_merge(base, override):
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


# ─── display ──────────────────────────────────────────────────────────────────

def _display_host(hostname, base_path, static=None, dynamic=None):
    if static is None or dynamic is None:
        static, dynamic = _load_host(hostname, base_path)

    width = 62
    title = ' {} '.format(hostname)
    print('\n' + title.center(width, '='))

    # Static section
    print('\n{}STATIC  (inventory snapshot){}'.format(BOLD, RESET))
    if not static:
        print(DIM + '  (no static data)' + RESET)
    else:
        print(yaml.dump(static, default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip())

    # Dynamic section
    print()
    if dynamic:
        last_updated = dynamic.get('last_updated', 'unknown')
        ping = dynamic.get('ping', '?')
        ssh = dynamic.get('ssh', '?')
        ping_str = 'true' if ping is True else ('false' if ping is False else str(ping))
        ssh_str = 'true' if ssh is True else ('false' if ssh is False else str(ssh))
        print('{}DYNAMIC{}  (last scan: {}  ping: {}  ssh: {})'.format(
            BOLD, RESET, last_updated, ping_str, ssh_str))
    else:
        print('{}DYNAMIC{}'.format(BOLD, RESET))

    if not dynamic:
        print(DIM + '  (no dynamic data yet)' + RESET)
    else:
        dynamic_body = {k: v for k, v in dynamic.items() if k not in HEADER_FIELDS}
        for line in _render(dynamic_body, static):
            print(line)


# ─── drift detection ──────────────────────────────────────────────────────────

def _has_drift(dynamic, static):
    """Return True if any dynamic scalar value differs from its static counterpart."""
    return _node_has_drift(dynamic, static)


def _node_has_drift(dyn, sta):
    if isinstance(dyn, dict):
        for key, value in dyn.items():
            if key in HEADER_FIELDS:
                continue
            sta_child = sta.get(key) if isinstance(sta, dict) else None
            if _node_has_drift(value, sta_child):
                return True
    elif isinstance(dyn, list):
        for item in dyn:
            if isinstance(item, dict) and 'name' in item:
                sta_item = _find_by_name(sta, item['name']) if isinstance(sta, list) else None
                if _node_has_drift(item, sta_item or {}):
                    return True
            else:
                if sta is not None and not any(_values_match(item, s) for s in (sta if isinstance(sta, list) else [sta])):
                    return True
    else:
        if sta is not None and not _values_match(dyn, sta):
            return True
    return False


# ─── colored rendering ────────────────────────────────────────────────────────

def _render(dyn, sta, indent=0):
    """Return a list of colored YAML-like lines for dyn, compared against sta."""
    lines = []
    pad = '  ' * indent

    if not isinstance(dyn, dict):
        return lines

    for key, value in dyn.items():
        sta_child = sta.get(key) if isinstance(sta, dict) else None

        if isinstance(value, dict):
            lines.append('{}{}:'.format(pad, key))
            lines.extend(_render(value, sta_child, indent + 1))

        elif isinstance(value, list):
            if not value:
                color = _color(value, sta_child)
                lines.append('{}{}{}: []{}'.format(color, pad, key, RESET))
            elif isinstance(value[0], dict) and 'name' in value[0]:
                lines.append('{}{}:'.format(pad, key))
                lines.extend(_render_named_list(value, sta_child, indent + 1))
            else:
                lines.append('{}{}:'.format(pad, key))
                lines.extend(_render_scalar_list(value, sta_child, indent + 1))

        else:
            color = _color(value, sta_child)
            lines.append('{}{}{}: {}{}'.format(color, pad, key, _fmt(value), RESET))

    return lines


def _render_named_list(dyn_list, sta_list, indent):
    """Render a list of dicts matched by their 'name' key."""
    lines = []
    pad = '  ' * indent
    inner = pad + '  '

    for item in dyn_list:
        name = item.get('name', '')
        sta_item = _find_by_name(sta_list, name) if isinstance(sta_list, list) else None
        name_color = GREEN if sta_item is not None else CYAN
        lines.append('{}- {}name: {}{}'.format(pad, name_color, name, RESET))

        for key, value in item.items():
            if key == 'name':
                continue
            sta_val = sta_item.get(key) if sta_item else None

            if isinstance(value, dict):
                lines.append('{}{}:'.format(inner, key))
                lines.extend(_render(value, sta_val, indent + 2))
            elif isinstance(value, list):
                if not value:
                    color = _color(value, sta_val)
                    lines.append('{}{}{}: []{}'.format(color, inner, key, RESET))
                else:
                    lines.append('{}{}:'.format(inner, key))
                    lines.extend(_render_scalar_list(value, sta_val, indent + 2))
            else:
                color = _color(value, sta_val)
                lines.append('{}{}{}: {}{}'.format(color, inner, key, _fmt(value), RESET))

    return lines


def _render_scalar_list(dyn_list, sta_ref, indent):
    """Render a list of scalars. sta_ref may be a list or a scalar."""
    lines = []
    pad = '  ' * indent

    if sta_ref is None:
        sta_values = None
    elif isinstance(sta_ref, list):
        sta_values = sta_ref
    else:
        sta_values = [sta_ref]

    for item in dyn_list:
        if sta_values is not None:
            matched = any(_values_match(item, s) for s in sta_values)
            color = GREEN if matched else RED
        else:
            color = CYAN
        lines.append('{}{}- {}{}'.format(color, pad, _fmt(item), RESET))

    return lines


# ─── helpers ──────────────────────────────────────────────────────────────────

def _find_by_name(lst, name):
    if not isinstance(lst, list):
        return None
    for item in lst:
        if isinstance(item, dict) and item.get('name') == name:
            return item
    return None


def _values_match(a, b):
    if a == b:
        return True
    # Normalize IP addresses: strip CIDR prefix before comparing.
    return str(a).split('/')[0].strip() == str(b).split('/')[0].strip()


def _color(dyn_val, sta_val):
    if sta_val is None:
        return CYAN
    if _values_match(dyn_val, sta_val):
        return GREEN
    return RED


def _fmt(value):
    """Format a scalar for YAML-like display."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if value is None:
        return 'null'
    if isinstance(value, str) and any(c in value for c in ':#{}[]'):
        return "'{}'".format(value.replace("'", "''"))
    return str(value)
