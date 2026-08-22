#!/usr/bin/env python3
"""
Events plugin for bluebanquise-cluster.
Displays the per-host event history (latch transitions, acknowledgements, maintenance
start/end) written by the state/supervision daemons and by this same plugin's `ack` action, via
events.py (a sibling file installed by this same role, cluster_management).

Usage:
  bluebanquise-cluster events all                                     display every host's events
  bluebanquise-cluster events error                                    display only hosts with an unacknowledged Error latch
  bluebanquise-cluster events host <hostname>                          display one host's events
  bluebanquise-cluster events host <hostname> ack <event_number> --by <name> --reason "<text>"
                                                                        acknowledge an Error event, clearing its latch

`events.yml`/`status.yml` are produced by events.py - this plugin needs that module present to
do anything at all, so a missing module is a fatal, immediate error, not a gracefully-skipped
overlay like state.py/supervision.py have elsewhere - there'd be nothing left to show.
"""

import argparse
import importlib.util
import os
import sys

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'


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

    if subcommand == 'all':
        found_any = False
        for hostname in _all_hosts(base_path):
            events = events_lib.read_events(hostname, base_path)
            if events:
                found_any = True
                _display_host_events(events_lib, hostname, events)
        if not found_any:
            print('No events recorded for any host yet.')

    elif subcommand == 'error':
        found_any = False
        for hostname in _all_hosts(base_path):
            status = events_lib.read_status(hostname, base_path)
            if any(v == events_lib.ERROR for v in status.get('latched', {}).values()):
                found_any = True
                events = events_lib.read_events(hostname, base_path)
                _display_host_events(events_lib, hostname, events)
        if not found_any:
            print(GREEN + 'No host currently has an unacknowledged error.' + RESET)

    elif subcommand == 'host':
        if not sub_args:
            print('Usage: bluebanquise-cluster events host <hostname> [ack <event_number> --by <name> --reason "<text>"]')
            sys.exit(1)
        hostname = sub_args[0]
        rest = sub_args[1:]

        if rest and rest[0] == 'ack':
            _ack(events_lib, hostname, rest[1:], base_path, tmp_path)
        else:
            events = events_lib.read_events(hostname, base_path)
            if not events:
                print('No events recorded for {!r} yet.'.format(hostname))
                return
            _display_host_events(events_lib, hostname, events)

    else:
        print('Unknown subcommand: {!r}'.format(subcommand))
        print()
        _print_usage()
        sys.exit(1)


def _print_usage():
    print('Usage:')
    print('  bluebanquise-cluster events all                            display every host\'s events')
    print('  bluebanquise-cluster events error                          display hosts with an unacknowledged error')
    print('  bluebanquise-cluster events host <hostname>                display one host\'s events')
    print('  bluebanquise-cluster events host <hostname> ack <number> --by <name> --reason "<text>"')
    print('                                                             acknowledge an Error event')


def _ack(events_lib, hostname, ack_args, base_path, tmp_path):
    if not ack_args:
        print('Usage: bluebanquise-cluster events host <hostname> ack <event_number> --by <name> --reason "<text>"')
        sys.exit(1)

    parser = argparse.ArgumentParser(prog='events host <hostname> ack', add_help=False)
    parser.add_argument('event_number', type=int)
    parser.add_argument('--by', required=True, help='Who is acknowledging this event (required)')
    parser.add_argument('--reason', required=True, help='Why this is being acknowledged (required)')
    parsed = parser.parse_args(ack_args)

    success, message = events_lib.acknowledge_event(
        hostname, parsed.event_number, parsed.by, parsed.reason, base_path, tmp_path)
    print((GREEN if success else RED) + message + RESET)
    sys.exit(0 if success else 1)


# ─── host discovery ───────────────────────────────────────────────────────────

def _all_hosts(base_path):
    if not os.path.isdir(base_path):
        print('Base path not found: {}'.format(base_path))
        sys.exit(1)
    return sorted(
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d))
    )


# ─── display ──────────────────────────────────────────────────────────────────

_KIND_COLOR = {
    'Error': RED,
    'Acknowledge': GREEN,
    'MaintenanceStart': YELLOW,
    'MaintenanceEnd': YELLOW,
}


def _display_host_events(events_lib, hostname, events):
    width = 62
    title = ' {} '.format(hostname)
    print('\n' + title.center(width, '='))
    for event in events:
        color = _KIND_COLOR.get(event.get('kind'), '')
        line = events_lib.format_event_line(event)
        print('{}{}{}'.format(color, line, RESET) if color else line)
