"""
Shared library: the drift-comparison primitives used to decide whether a dynamic (live) YAML
tree differs from its static (inventory-declared) counterpart. Installed by the cluster_management
role to /usr/local/lib/bluebanquise/cluster/state_diff.py, alongside (not inside) the
auto-discovered plugins/ directory - it is not itself a bluebanquise-cluster action.

Extracted from the state plugin (formerly its private _node_has_drift/_generic_match family) so
the state daemon can reuse the exact same comparison logic to decide whether to latch an Error
via events.py (see AI/CLAUDE.md's "Cluster Management System" section) - a single source of
truth for "what counts as drift", not two copies that could quietly diverge. Not a runnable
script - loaded dynamically (importlib.util.spec_from_file_location) by whichever plugin/daemon
needs it, same reasoning as events.py: these are standalone files, not an importable package.

Pure data comparison only - no printing, no color, no knowledge of files on disk.
"""

# Sentinel distinguishing "key absent" from a real YAML null.
MISSING = object()


def ordered_keys(dyn_dict, sta_dict):
    """dyn's key order first, then any static-only keys appended."""
    keys = list(dyn_dict.keys())
    for k in sta_dict.keys():
        if k not in dyn_dict:
            keys.append(k)
    return keys


def has_drift(dyn, sta):
    return node_has_drift(dyn if isinstance(dyn, dict) else {}, sta if isinstance(sta, dict) else {})


def node_has_drift(dyn_dict, sta_dict):
    for key in ordered_keys(dyn_dict, sta_dict):
        dv = dyn_dict[key] if key in dyn_dict else MISSING
        sv = sta_dict[key] if key in sta_dict else MISSING
        if dv is MISSING or sv is MISSING:
            continue  # missing on one side is NA, not drift
        sample = dv
        if isinstance(sample, dict):
            if node_has_drift(dv if isinstance(dv, dict) else {}, sv if isinstance(sv, dict) else {}):
                return True
        elif is_named_list(sample):
            if named_list_has_drift(dv if isinstance(dv, list) else [], sv if isinstance(sv, list) else []):
                return True
        elif not generic_match(dv, sv):
            return True
    return False


def named_list_has_drift(dv_list, sv_list):
    for name in named_list_names(dv_list, sv_list):
        dv_item = find_by_name(dv_list, name)
        sv_item = find_by_name(sv_list, name)
        if dv_item is None or sv_item is None:
            continue  # missing item on one side is NA, not drift
        if node_has_drift(strip_name(dv_item), strip_name(sv_item)):
            return True
    return False


def is_named_list(value):
    return isinstance(value, list) and bool(value) and isinstance(value[0], dict) and 'name' in value[0]


def named_list_names(dv_list, sv_list):
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


def find_by_name(lst, name):
    if not isinstance(lst, list):
        return None
    for item in lst:
        if isinstance(item, dict) and item.get('name') == name:
            return item
    return None


def strip_name(d):
    return {k: v for k, v in d.items() if k != 'name'} if d else {}


def generic_match(dv, sv):
    if isinstance(dv, list) or isinstance(sv, list):
        # A scalar on one side (e.g. static network_interfaces[].ip4 as a single string) can
        # pair against a list on the other (the daemon reports ip4 as a list) - normalize the
        # scalar side into a one-item list before comparing as sets.
        dv_list = dv if isinstance(dv, list) else [dv]
        sv_list = sv if isinstance(sv, list) else [sv]
        return sorted(norm_item(v) for v in dv_list) == sorted(norm_item(v) for v in sv_list)
    return values_match(dv, sv)


def norm_item(v):
    if isinstance(v, (dict, list)):
        return fmt_any(v)
    return str(v).split('/')[0].strip()


def values_match(a, b):
    if a == b:
        return True
    # Normalize IP addresses: strip CIDR prefix before comparing.
    return str(a).split('/')[0].strip() == str(b).split('/')[0].strip()


def fmt(value):
    """Format a scalar for YAML-like display."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if value is None:
        return 'null'
    if isinstance(value, str) and any(c in value for c in ':#{}[]'):
        return "'{}'".format(value.replace("'", "''"))
    return str(value)


def fmt_any(value):
    """Format any YAML-serialisable value as a compact single-line string."""
    if isinstance(value, dict):
        return '{' + ', '.join('{}: {}'.format(k, fmt_any(v)) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(fmt_any(v) for v in value) + ']'
    return fmt(value)
