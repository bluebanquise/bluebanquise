#!/usr/bin/env python3
"""
Supervision plugin for bluebanquise-cluster.
Displays health check results produced by the supervision daemon (bluebanquise-cluster-supervision-daemon).

Usage:
  bluebanquise-cluster supervision host <hostname>   display one host
  bluebanquise-cluster supervision all               display every host with supervision data
  bluebanquise-cluster supervision error              display only hosts currently in error

Reads supervision.yml (full per-check detail) and dynamic_supervision.yml (host_status/
bmc_status summary) from /var/lib/bluebanquise/cluster/hosts/<hostname>/. A host with no
cluster_management_supervision_checks configured for it - or one the daemon hasn't scanned yet -
has neither file; that is reported clearly rather than treated as an error.

A host's maintenance flag and its latched "cluster_supervision" status (see events.py's
docstring) are shown as a banner right under the host title, and a host in maintenance or with
an unacknowledged latch is excluded from `error`.
"""

import importlib.util
import os
import sys
import yaml

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

OK_STATUSES = ('Ok',)

# The subsystem name the supervision daemon latches under (see events.py's docstring).
SUBSYSTEM = 'cluster_supervision'

_events_lib = None  # loaded lazily in run()


def _load_events_module(path):
    """events.py is installed by this same role (cluster_management) - always present in a
    correct install."""
    if not path or not os.path.isfile(path):
        print('events.py not found at {} (cluster_management installation incomplete?)'.format(path),
              file=sys.stderr)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location('cluster_events_lib', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(args, config):
    global _events_lib
    _events_lib = _load_events_module(config.get('events_module_path'))
    base_path = config['base_path']

    if not args:
        _print_usage()
        sys.exit(1)

    subcommand = args[0]
    sub_args = args[1:]

    if subcommand == 'host':
        if not sub_args:
            print('Usage: bluebanquise-cluster supervision host <hostname>')
            sys.exit(1)
        hostname = sub_args[0]
        if not _has_supervision_data(hostname, base_path):
            print('No supervision data for {!r}: either it has no cluster_management_supervision_checks '
                  'configured, or the daemon has not completed a scan cycle yet.'.format(hostname))
            sys.exit(1)
        _display_host(hostname, base_path)

    elif subcommand == 'all':
        hosts = [h for h in _all_hosts(base_path) if _has_supervision_data(h, base_path)]
        if not hosts:
            print('No host has supervision data yet.')
            return
        for hostname in hosts:
            _display_host(hostname, base_path)

    elif subcommand == 'error':
        found_any = False
        for hostname in _all_hosts(base_path):
            if not _has_supervision_data(hostname, base_path):
                continue
            if _is_in_maintenance(hostname, base_path):
                continue
            dynamic = _load_yaml(_dynamic_path(hostname, base_path))
            if _is_error(dynamic):
                found_any = True
                _display_host(hostname, base_path)
        if not found_any:
            print(GREEN + 'No host currently in error.' + RESET)

    else:
        print('Unknown subcommand: {!r}'.format(subcommand))
        print()
        _print_usage()
        sys.exit(1)


def _print_usage():
    print('Usage:')
    print('  bluebanquise-cluster supervision host <hostname>  display one host')
    print('  bluebanquise-cluster supervision all               display every host with supervision data')
    print('  bluebanquise-cluster supervision error              display only hosts currently in error')


# ─── data loading ─────────────────────────────────────────────────────────────

def _all_hosts(base_path):
    if not os.path.isdir(base_path):
        print('Base path not found: {}'.format(base_path))
        sys.exit(1)
    return sorted(
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d))
    )


def _supervision_path(hostname, base_path):
    return os.path.join(base_path, hostname, 'supervision.yml')


def _dynamic_path(hostname, base_path):
    return os.path.join(base_path, hostname, 'dynamic_supervision.yml')


def _has_supervision_data(hostname, base_path):
    return os.path.isfile(_supervision_path(hostname, base_path))


def _load_yaml(filepath):
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except OSError:
        return {}
    except yaml.YAMLError as e:
        print('Warning: could not parse {}: {}'.format(filepath, e), file=sys.stderr)
        return {}


def _is_error(dynamic):
    for key in ('host_status', 'bmc_status'):
        value = dynamic.get(key)
        if value is not None and value not in OK_STATUSES:
            return True
    return False


# ─── maintenance / latch overlay ────────────────────────────────────────────────

def _is_in_maintenance(hostname, base_path):
    return _events_lib.is_in_maintenance(_events_lib.read_status(hostname, base_path))


def _display_status_banner(hostname, base_path):
    status = _events_lib.read_status(hostname, base_path)
    maintenance = status.get('maintenance', {})

    if maintenance.get('active'):
        print('{}[MAINTENANCE]{} since {} by {}: {}'.format(
            YELLOW, RESET, maintenance.get('since'), maintenance.get('by'), maintenance.get('reason')))
        return

    if status.get('latched', {}).get(SUBSYSTEM) == _events_lib.ERROR:
        print('{}[LATCHED ERROR]{} {} - unacknowledged, see: '
              'bluebanquise-cluster events host {} ack <number> --by <name> --reason "<text>"'.format(
                  RED, RESET, SUBSYSTEM, hostname))


# ─── display ──────────────────────────────────────────────────────────────────

def _status_color(status):
    return GREEN if status in OK_STATUSES else RED


def _display_host(hostname, base_path):
    supervision = _load_yaml(_supervision_path(hostname, base_path))
    dynamic = _load_yaml(_dynamic_path(hostname, base_path))

    width = 62
    title = ' {} '.format(hostname)
    print('\n' + title.center(width, '='))
    _display_status_banner(hostname, base_path)

    host_status = dynamic.get('host_status', 'Unknown')
    print('{}host_status:{} {}{}{}'.format(BOLD, RESET, _status_color(host_status), host_status, RESET))
    if 'bmc_status' in dynamic:
        bmc_status = dynamic.get('bmc_status', 'Unknown')
        print('{}bmc_status:{}  {}{}{}'.format(BOLD, RESET, _status_color(bmc_status), bmc_status, RESET))

    last_scan = supervision.get('last_scan', dynamic.get('last_scan', 'unknown'))
    ssh_gate = supervision.get('ssh_gate')
    ssh_gate_str = 'unknown' if ssh_gate is None else ('ok' if ssh_gate else 'FAILED')
    print(DIM + '  last scan: {}  ssh gate: {}'.format(last_scan, ssh_gate_str) + RESET)

    checks = supervision.get('checks', {}) or {}
    if not checks:
        print(DIM + '  (no per-check detail available)' + RESET)
        return

    for check_name in sorted(checks.keys()):
        _display_check(check_name, checks[check_name])


def _display_check(check_name, result):
    error = result.get('error', True)
    status = RED + 'ERROR' + RESET if error else GREEN + 'OK' + RESET
    args = result.get('args')
    args_str = ' {}'.format(args) if args else ''
    exit_code = result.get('exit_code')

    print('\n{}{}{}{} (exit={}) - {}'.format(BOLD, check_name, RESET, args_str, exit_code, status))

    stdout = (result.get('stdout') or '').strip()
    stderr = (result.get('stderr') or '').strip()

    if stdout:
        print('  {}stdout:{}'.format(BOLD, RESET))
        for line in stdout.splitlines():
            print('    {}'.format(line))

    if stderr:
        print('  {}stderr:{}'.format(BOLD, RESET))
        for line in stderr.splitlines():
            print('    {}'.format(line))
