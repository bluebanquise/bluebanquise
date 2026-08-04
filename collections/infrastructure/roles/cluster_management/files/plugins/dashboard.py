#!/usr/bin/env python3
"""
Dashboard plugin for bluebanquise-cluster.
A single-glance terminal summary of the cluster: connectivity, state drift, and supervision -
three bordered frames, each with a proportional green/red gauge bar. A static snapshot, printed
once and exits - same as every other plugin here, no live refresh.

Usage:
  bluebanquise-cluster dashboard

Prefers events.py's status.yml (latched cluster_state/cluster_supervision) for the drift and
supervision frames when a host has a latched value there - it was designed with this in mind, so
the dashboard doesn't need to recompute drift/health itself. Falls back to computing live
(state_diff.py for drift, dynamic_supervision.yml directly for supervision) per host when that
host hasn't been through a latch-checked cycle yet, exactly like state.py/supervision.py already
do for their own overlays. Hosts currently in maintenance are excluded from every frame's counts
(denominator included) - see events.py's docstring - with a single "N in maintenance" line up
top instead.
"""

import importlib.util
import os
import re
import sys
import yaml

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

BAR_WIDTH = 24
_ANSI_RE = re.compile(r'\033\[[0-9;]*m')

_diff = None  # loaded in run() - state_diff.py and events.py are both installed by this same
_events_lib = None  # role (cluster_management), always present in a correct install


def _load_required_module(path, module_name):
    if not path or not os.path.isfile(path):
        print('{} not found at {} (cluster_management installation incomplete?)'.format(
            module_name, path), file=sys.stderr)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_state_diff(plugins_path):
    diff_path = os.path.join(os.path.dirname(plugins_path.rstrip('/')), 'state_diff.py')
    return _load_required_module(diff_path, 'state_diff')


def run(args, config):
    global _diff, _events_lib
    _diff = _load_state_diff(config['plugins_path'])
    _events_lib = _load_required_module(config.get('events_module_path'), 'cluster_events_lib')
    base_path = config['base_path']

    hosts = _all_hosts(base_path)
    maintenance_hosts = _maintenance_hosts(hosts, base_path)
    active_hosts = [h for h in hosts if h not in maintenance_hosts]

    print()
    print('{}BlueBanquise Cluster Dashboard{} - {} host(s){}'.format(
        BOLD, RESET, len(hosts),
        ', {} in maintenance'.format(len(maintenance_hosts)) if maintenance_hosts else ''))

    connectivity_lines = _connectivity_frame(active_hosts, base_path)
    drift_lines = _state_drift_frame(active_hosts, base_path)
    supervision_lines = _supervision_frame(active_hosts, base_path)

    width = max(
        _frame_width('Connectivity', connectivity_lines),
        _frame_width('State Drift', drift_lines),
        _frame_width('Supervision', supervision_lines),
    )

    for title, lines in (('Connectivity', connectivity_lines),
                         ('State Drift', drift_lines),
                         ('Supervision', supervision_lines)):
        print()
        for line in _render_frame(title, lines, width):
            print(line)
    print()


# ─── host / maintenance discovery ──────────────────────────────────────────────

def _all_hosts(base_path):
    if not os.path.isdir(base_path):
        print('Base path not found: {}'.format(base_path))
        sys.exit(1)
    return sorted(
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d))
    )


def _maintenance_hosts(hosts, base_path):
    return {
        h for h in hosts
        if _events_lib.is_in_maintenance(_events_lib.read_status(h, base_path))
    }


def _load_yaml(filepath):
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except OSError:
        return {}
    except yaml.YAMLError:
        return {}


# ─── frame 1: connectivity ──────────────────────────────────────────────────────

def _connectivity_frame(hosts, base_path):
    ping_up = ping_total = 0
    ssh_up = ssh_total = 0
    bmc_up = bmc_total = 0

    for hostname in hosts:
        dynamic = _load_yaml(os.path.join(base_path, hostname, 'dynamic_cluster_state.yml'))
        if not dynamic:
            continue
        ping_total += 1
        if dynamic.get('ping'):
            ping_up += 1
        ssh_total += 1
        if dynamic.get('ssh'):
            ssh_up += 1
        bmc = dynamic.get('bmc')
        if isinstance(bmc, dict) and 'ping' in bmc:
            bmc_total += 1
            if bmc.get('ping'):
                bmc_up += 1

    return [
        _bar_line('Hosts up', ping_up, ping_total),
        _bar_line('Hosts SSH-able', ssh_up, ssh_total),
        _bar_line('BMC up', bmc_up, bmc_total),
    ]


# ─── frame 2: state drift ───────────────────────────────────────────────────────

def _state_drift_frame(hosts, base_path):
    drifted = total = 0

    for hostname in hosts:
        static_path = os.path.join(base_path, hostname, 'static_cluster_state.yml')
        dynamic_path = os.path.join(base_path, hostname, 'dynamic_cluster_state.yml')
        if not (os.path.isfile(static_path) and os.path.isfile(dynamic_path)):
            continue
        total += 1

        latched = _latched_value(hostname, base_path, 'cluster_state')
        if latched is not None:
            if latched == _events_lib.ERROR:
                drifted += 1
            continue

        static_state = _load_yaml(static_path)
        dynamic_state = _load_yaml(dynamic_path)
        body = {k: v for k, v in dynamic_state.items() if k not in ('last_updated', 'ping', 'ssh')}
        if _diff.has_drift(body, static_state):
            drifted += 1

    # _bar_line's convention (matching frame 1) is "up/green = healthy" - drifted is the
    # unhealthy count here, so what's passed as "up" is total - drifted, and the label is
    # worded to match what's actually shown (was briefly "Hosts drifted" showing the
    # not-drifted count under that label, which is backwards - caught in testing).
    return [_bar_line('Hosts in sync', total - drifted, total)]


# ─── frame 3: supervision ───────────────────────────────────────────────────────

def _supervision_frame(hosts, base_path):
    errored = total = 0

    for hostname in hosts:
        supervision_path = os.path.join(base_path, hostname, 'supervision.yml')
        if not os.path.isfile(supervision_path):
            continue
        total += 1

        latched = _latched_value(hostname, base_path, 'cluster_supervision')
        if latched is not None:
            if latched == _events_lib.ERROR:
                errored += 1
            continue

        dynamic = _load_yaml(os.path.join(base_path, hostname, 'dynamic_supervision.yml'))
        is_error = any(
            dynamic.get(key) is not None and dynamic.get(key) != 'Ok'
            for key in ('host_status', 'bmc_status')
        )
        if is_error:
            errored += 1

    # Same fix as the drift frame above: label matches what's shown (the healthy/green count).
    return [_bar_line('Hosts healthy', total - errored, total)]


def _latched_value(hostname, base_path, subsystem):
    """None means "no opinion, compute live" - this particular host/subsystem was never latched
    (e.g. a newly added host the daemon hasn't scanned yet). Legitimate and expected on a
    freshly-provisioned host - not the same thing as events.py being missing, which is a fatal
    startup error handled in run(), not here."""
    status = _events_lib.read_status(hostname, base_path)
    return status.get('latched', {}).get(subsystem)


# ─── rendering ──────────────────────────────────────────────────────────────────

def _visible_len(s):
    return len(_ANSI_RE.sub('', s))


def _pad(s, width):
    return s + ' ' * max(0, width - _visible_len(s))


def _render_bar(up, total, width=BAR_WIDTH):
    if total == 0:
        return DIM + ('·' * width) + RESET

    up_chars = round((up / total) * width)
    # Never let the bar claim a cleaner result than reality: if the true percentage isn't
    # exactly 0% or 100%, force at least one character of the minority color even if rounding
    # at this width would otherwise collapse it to a single solid color.
    if up_chars == width and up < total:
        up_chars = width - 1
    elif up_chars == 0 and up > 0:
        up_chars = 1
    down_chars = width - up_chars

    return '{}{}{}{}{}{}'.format(GREEN, '█' * up_chars, RESET, RED, '█' * down_chars, RESET)


def _bar_line(label, up, total):
    if total == 0:
        return '{}  {}  [{}]'.format(_pad(label, 16), _pad('no data', 12), _render_bar(0, 0))
    pct = round((up / total) * 100)
    counts = '{}/{} ({}%)'.format(up, total, pct)
    return '{}  {}  [{}]'.format(_pad(label, 16), _pad(counts, 12), _render_bar(up, total))


def _frame_width(title, lines):
    content_width = max([_visible_len(line) for line in lines] + [len(title) + 2])
    return content_width + 4  # 1 space padding each side + 2 border characters


def _render_frame(title, lines, width):
    inner = width - 2
    top = '┌─ {} '.format(title)
    top += '─' * max(0, inner - _visible_len(top) + 1) + '┐'
    rendered = [top]
    for line in lines:
        rendered.append('│ {} │'.format(_pad(line, inner - 2)))
    rendered.append('└' + '─' * inner + '┘')
    return rendered
