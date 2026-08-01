#!/usr/bin/env python3
"""
Supervision plugin for bluebanquise-cluster.
Displays health check results produced by the cluster_supervision daemon.

Usage:
  bluebanquise-cluster supervision host <hostname>   display one host
  bluebanquise-cluster supervision all               display every host with supervision data
  bluebanquise-cluster supervision error              display only hosts currently in error

Reads supervision.yml (full per-check detail) and dynamic_supervision.yml (host_status/
bmc_status summary) from /var/lib/bluebanquise/cluster/hosts/<hostname>/. A host with no
cluster_supervision_checks configured for it - or one the daemon hasn't scanned yet - has
neither file; that is reported clearly rather than treated as an error.
"""

import os
import sys
import yaml

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

OK_STATUSES = ('Ok',)


def run(args, config):
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
            print('No supervision data for {!r}: either it has no cluster_supervision_checks '
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


# ─── display ──────────────────────────────────────────────────────────────────

def _status_color(status):
    return GREEN if status in OK_STATUSES else RED


def _display_host(hostname, base_path):
    supervision = _load_yaml(_supervision_path(hostname, base_path))
    dynamic = _load_yaml(_dynamic_path(hostname, base_path))

    width = 62
    title = ' {} '.format(hostname)
    print('\n' + title.center(width, '='))

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
