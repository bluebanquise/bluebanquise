#!/usr/bin/env python3
"""
Maintenance plugin for bluebanquise-cluster.
Sets/clears a host's maintenance flag via events.py (a sibling file installed by this same role,
cluster_management). While active, the state/supervision daemons stop latching new errors for
that host (see events.py's docstring), and the state/supervision plugins show a MAINTENANCE
banner instead of the normal error coloring.

Usage:
  bluebanquise-cluster maintenance set <hostname> --by <name> --reason "<text>"
  bluebanquise-cluster maintenance unset <hostname> --by <name> --reason "<text>"

--by and --reason are required on both actions - maintenance windows are meant to be a readable
history (`bluebanquise-cluster events host <hostname>`), especially useful when several
sysadmins work the same cluster.
"""

import argparse
import importlib.util
import os
import sys

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


def _load_events_module(path):
    if not os.path.isfile(path):
        print('events.py not found at {} - this cluster_management installation is '
              'incomplete.'.format(path), file=sys.stderr)
        sys.exit(1)
    spec = importlib.util.spec_from_file_location('cluster_events_lib', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(args, config):
    events_lib = _load_events_module(config['events_module_path'])
    base_path = config['base_path']
    tmp_path = config['tmp_path']

    if not args:
        _print_usage()
        sys.exit(1)

    subcommand = args[0]
    sub_args = args[1:]

    if subcommand not in ('set', 'unset'):
        print('Unknown subcommand: {!r}'.format(subcommand))
        print()
        _print_usage()
        sys.exit(1)

    if not sub_args:
        print('Usage: bluebanquise-cluster maintenance {} <hostname> --by <name> --reason "<text>"'.format(subcommand))
        sys.exit(1)

    hostname = sub_args[0]
    parser = argparse.ArgumentParser(prog='maintenance {}'.format(subcommand), add_help=False)
    parser.add_argument('--by', required=True, help='Who is setting/clearing maintenance (required)')
    parser.add_argument('--reason', required=True, help='Why (required)')
    parsed = parser.parse_args(sub_args[1:])

    if subcommand == 'set':
        success, message = events_lib.set_maintenance(hostname, parsed.reason, parsed.by, base_path, tmp_path)
    else:
        success, message = events_lib.clear_maintenance(hostname, parsed.reason, parsed.by, base_path, tmp_path)

    print((GREEN if success else RED) + message + RESET)
    sys.exit(0 if success else 1)


def _print_usage():
    print('Usage:')
    print('  bluebanquise-cluster maintenance set <hostname> --by <name> --reason "<text>"')
    print('  bluebanquise-cluster maintenance unset <hostname> --by <name> --reason "<text>"')
