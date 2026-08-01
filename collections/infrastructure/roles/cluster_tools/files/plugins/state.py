#!/usr/bin/env python3
"""
State plugin for bluebanquise-cluster.
Displays static inventory state and dynamic live state with drift detection.

Usage:
  bluebanquise-cluster state host <hostname>   display one host
  bluebanquise-cluster state all               display all hosts
  bluebanquise-cluster state error             display only hosts with drift

Static and dynamic files are paired by suffix: static_<suffix>.yml is compared against
dynamic_<suffix>.yml. Each suffix is displayed independently — nothing is merged across
suffixes. `cluster_state` is always shown first since it is the primary pair; every other
suffix (pxe_stack, cluster_playbooks, ...) is a plugin-style addition and may only have one
side (static or dynamic) present.
"""

import glob
import os
import sys
import yaml

GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

# Fields extracted into the cluster_state banner's header line; omitted from the body.
HEADER_FIELDS = {'last_updated', 'ping', 'ssh'}

# Sentinel distinguishing "key absent" from a real YAML null.
_MISSING = object()


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
            suffixes = _load_suffixes(hostname, base_path)
            if _host_has_error(suffixes):
                _display_host(hostname, base_path, suffixes=suffixes)

    else:
        print('Unknown subcommand: {!r}'.format(subcommand))
        print()
        _print_usage()
        sys.exit(1)


def _print_usage():
    print('Usage:')
    print('  bluebanquise-cluster state host <hostname>  display one host')
    print('  bluebanquise-cluster state all               display all hosts')
    print('  bluebanquise-cluster state error             display hosts with drift')


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

def _load_suffixes(hostname, base_path):
    """Bucket every static_<suffix>.yml / dynamic_<suffix>.yml in a host's folder by suffix.

    Returns {suffix: {'static': dict|None, 'dynamic': dict|None}}. No merging across files —
    one suffix maps to at most one static file and one dynamic file.
    """
    host_dir = os.path.join(base_path, hostname)
    suffixes = {}
    if not os.path.isdir(host_dir):
        return suffixes

    for prefix, side in (('static_', 'static'), ('dynamic_', 'dynamic')):
        pattern = os.path.join(host_dir, prefix + '*.yml')
        for filepath in sorted(glob.glob(pattern)):
            suffix = os.path.basename(filepath)[len(prefix):-len('.yml')]
            suffixes.setdefault(suffix, {'static': None, 'dynamic': None})[side] = _load_yaml(filepath)

    return suffixes


def _load_yaml(filepath):
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print('Warning: could not load {}: {}'.format(filepath, e), file=sys.stderr)
        return {}


def _strip_header_fields(suffix, dyn):
    if suffix == 'cluster_state' and isinstance(dyn, dict):
        return {k: v for k, v in dyn.items() if k not in HEADER_FIELDS}
    return dyn


# ─── display ──────────────────────────────────────────────────────────────────

def _display_host(hostname, base_path, suffixes=None):
    if suffixes is None:
        suffixes = _load_suffixes(hostname, base_path)

    width = 62
    title = ' {} '.format(hostname)
    print('\n' + title.center(width, '='))

    if not suffixes:
        print(DIM + '  (no state data)' + RESET)
        return

    ordered = sorted(suffixes.keys(), key=lambda s: (s != 'cluster_state', s))
    for suffix in ordered:
        pair = suffixes[suffix]
        _display_suffix(suffix, pair.get('dynamic'), pair.get('static'))


def _display_suffix(suffix, dyn, sta):
    header_extra = ''
    if suffix == 'cluster_state' and isinstance(dyn, dict):
        last_updated = dyn.get('last_updated', 'unknown')
        ping = _bool_str(dyn.get('ping', '?'))
        ssh = _bool_str(dyn.get('ssh', '?'))
        header_extra = '  (last scan: {}  ping: {}  ssh: {})'.format(last_updated, ping, ssh)
    body_dyn = _strip_header_fields(suffix, dyn)

    if dyn is not None and sta is not None:
        drift = _has_drift(body_dyn, sta)
        title_color = RED if drift else GREEN
        print('\n{}{}{}{}{}'.format(BOLD, title_color, suffix, RESET, header_extra))
        print(DIM + '  dynamic / static  (green=match, red=drift, cyan=dynamic-only, blue NA=missing on one side)' + RESET)
        for line in _render_paired(body_dyn, sta):
            print(line)

    elif sta is not None:
        print('\n{}{}{}'.format(BOLD, suffix, RESET))
        print(DIM + '  static only — inventory snapshot, no dynamic data for this suffix' + RESET)
        for line in _render_single(sta, 0, ''):
            print(line)

    else:
        print('\n{}{}{}{}'.format(BOLD, suffix, RESET, header_extra))
        print(DIM + '  dynamic only — live daemon data, no static counterpart for this suffix' + RESET)
        for line in _render_single(body_dyn, 0, CYAN):
            print(line)


# ─── drift detection ──────────────────────────────────────────────────────────

def _has_drift(dyn, sta):
    return _node_has_drift(dyn if isinstance(dyn, dict) else {}, sta if isinstance(sta, dict) else {})


def _node_has_drift(dyn_dict, sta_dict):
    for key in _ordered_keys(dyn_dict, sta_dict):
        dv = dyn_dict[key] if key in dyn_dict else _MISSING
        sv = sta_dict[key] if key in sta_dict else _MISSING
        if dv is _MISSING or sv is _MISSING:
            continue  # missing on one side is NA, not drift
        sample = dv
        if isinstance(sample, dict):
            if _node_has_drift(dv if isinstance(dv, dict) else {}, sv if isinstance(sv, dict) else {}):
                return True
        elif _is_named_list(sample):
            if _named_list_has_drift(dv if isinstance(dv, list) else [], sv if isinstance(sv, list) else []):
                return True
        elif not _generic_match(dv, sv):
            return True
    return False


def _named_list_has_drift(dv_list, sv_list):
    for name in _named_list_names(dv_list, sv_list):
        dv_item = _find_by_name(dv_list, name)
        sv_item = _find_by_name(sv_list, name)
        if dv_item is None or sv_item is None:
            continue  # missing item on one side is NA, not drift
        if _node_has_drift(_strip_name(dv_item), _strip_name(sv_item)):
            return True
    return False


def _host_has_error(suffixes):
    for suffix, pair in suffixes.items():
        dyn, sta = pair.get('dynamic'), pair.get('static')
        if dyn is None or sta is None:
            continue
        if _has_drift(_strip_header_fields(suffix, dyn), sta):
            return True
    return False


# ─── paired (both static and dynamic present) rendering ───────────────────────

def _render_paired(dyn, sta, indent=0):
    dyn_dict = dyn if isinstance(dyn, dict) else {}
    sta_dict = sta if isinstance(sta, dict) else {}
    lines = []
    for key in _ordered_keys(dyn_dict, sta_dict):
        dv = dyn_dict[key] if key in dyn_dict else _MISSING
        sv = sta_dict[key] if key in sta_dict else _MISSING
        lines.extend(_render_pair_value(key, dv, sv, indent))
    return lines


def _render_pair_value(key, dv, sv, indent):
    pad = '  ' * indent
    sample = dv if dv is not _MISSING else sv

    if isinstance(sample, dict):
        sub_dv = dv if isinstance(dv, dict) else {}
        sub_sv = sv if isinstance(sv, dict) else {}
        return ['{}{}:'.format(pad, key)] + _render_paired(sub_dv, sub_sv, indent + 1)

    if _is_named_list(sample):
        sub_dv = dv if isinstance(dv, list) else []
        sub_sv = sv if isinstance(sv, list) else []
        return ['{}{}:'.format(pad, key)] + _render_paired_named_list(sub_dv, sub_sv, indent + 1)

    return [_pair_line(pad, key, dv, sv)]


def _render_paired_named_list(dv_list, sv_list, indent):
    lines = []
    pad = '  ' * indent

    for name in _named_list_names(dv_list, sv_list):
        dv_item = _find_by_name(dv_list, name)
        sv_item = _find_by_name(sv_list, name)
        if dv_item is not None and sv_item is not None:
            name_color = GREEN
        elif dv_item is not None:
            name_color = CYAN
        else:
            name_color = BLUE
        lines.append('{}- {}name: {}{}'.format(pad, name_color, name, RESET))
        lines.extend(_render_paired(_strip_name(dv_item or {}), _strip_name(sv_item or {}), indent + 1))

    return lines


def _pair_line(pad, key, dv, sv):
    if dv is _MISSING:
        dyn_disp = '{}NA{}'.format(BLUE, RESET)
    elif sv is _MISSING:
        dyn_disp = '{}{}{}'.format(CYAN, _fmt_any(dv), RESET)
    elif _generic_match(dv, sv):
        dyn_disp = '{}{}{}'.format(GREEN, _fmt_any(dv), RESET)
    else:
        dyn_disp = '{}{}{}'.format(RED, _fmt_any(dv), RESET)

    sta_disp = '{}NA{}'.format(BLUE, RESET) if sv is _MISSING else _fmt_any(sv)

    return '{}{}: {} / {}'.format(pad, key, dyn_disp, sta_disp)


# ─── single-sided (static-only or dynamic-only) rendering ─────────────────────

def _render_single(node, indent, color):
    lines = []
    if not isinstance(node, dict):
        return lines
    for key, value in node.items():
        lines.extend(_render_single_value(key, value, indent, color))
    return lines


def _render_single_value(key, value, indent, color):
    pad = '  ' * indent

    if isinstance(value, dict):
        return ['{}{}:'.format(pad, key)] + _render_single(value, indent + 1, color)

    if _is_named_list(value):
        lines = ['{}{}:'.format(pad, key)]
        item_pad = '  ' * (indent + 1)
        for item in value:
            lines.append(_colorize('{}- name: {}'.format(item_pad, item.get('name', '')), color))
            for k2, v2 in item.items():
                if k2 == 'name':
                    continue
                lines.extend(_render_single_value(k2, v2, indent + 2, color))
        return lines

    return [_colorize('{}{}: {}'.format(pad, key, _fmt_any(value)), color)]


def _colorize(text, color):
    return '{}{}{}'.format(color, text, RESET) if color else text


# ─── helpers ──────────────────────────────────────────────────────────────────

def _ordered_keys(dyn_dict, sta_dict):
    """dyn's key order first, then any static-only keys appended."""
    keys = list(dyn_dict.keys())
    for k in sta_dict.keys():
        if k not in dyn_dict:
            keys.append(k)
    return keys


def _is_named_list(value):
    return isinstance(value, list) and bool(value) and isinstance(value[0], dict) and 'name' in value[0]


def _named_list_names(dv_list, sv_list):
    names = []
    for item in dv_list:
        n = item.get('name', '') if isinstance(item, dict) else ''
        if n not in names:
            names.append(n)
    for item in sv_list:
        n = item.get('name', '') if isinstance(item, dict) else ''
        if n not in names:
            names.append(n)
    return names


def _find_by_name(lst, name):
    if not isinstance(lst, list):
        return None
    for item in lst:
        if isinstance(item, dict) and item.get('name') == name:
            return item
    return None


def _strip_name(d):
    return {k: v for k, v in d.items() if k != 'name'} if d else {}


def _generic_match(dv, sv):
    if isinstance(dv, list) or isinstance(sv, list):
        # A scalar on one side (e.g. static network_interfaces[].ip4 as a single string) can
        # pair against a list on the other (the daemon reports ip4 as a list) — normalize the
        # scalar side into a one-item list before comparing as sets.
        dv_list = dv if isinstance(dv, list) else [dv]
        sv_list = sv if isinstance(sv, list) else [sv]
        return sorted(_norm_item(v) for v in dv_list) == sorted(_norm_item(v) for v in sv_list)
    return _values_match(dv, sv)


def _norm_item(v):
    if isinstance(v, (dict, list)):
        return _fmt_any(v)
    return str(v).split('/')[0].strip()


def _values_match(a, b):
    if a == b:
        return True
    # Normalize IP addresses: strip CIDR prefix before comparing.
    return str(a).split('/')[0].strip() == str(b).split('/')[0].strip()


def _bool_str(value):
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    return str(value)


def _fmt(value):
    """Format a scalar for YAML-like display."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if value is None:
        return 'null'
    if isinstance(value, str) and any(c in value for c in ':#{}[]'):
        return "'{}'".format(value.replace("'", "''"))
    return str(value)


def _fmt_any(value):
    """Format any YAML-serialisable value as a compact single-line string."""
    if isinstance(value, dict):
        return '{' + ', '.join('{}: {}'.format(k, _fmt_any(v)) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(_fmt_any(v) for v in value) + ']'
    return _fmt(value)
