"""
Shared library: per-host persistent status (maintenance flag + a latched Ok/Error per
subsystem) and an append-only event history. Installed once by the cluster_management role,
under /usr/local/lib/bluebanquise/cluster/ by default.

Every consumer (the state and supervision daemons, and the state/supervision/events/maintenance
CLI plugins - all part of this same role) loads this file dynamically via
importlib.util.spec_from_file_location rather than a plain `import` (it's a standalone file, not
an importable package - there is no shared Python package/sys.path between the daemon scripts,
the plugins, and this library even though they're all installed by one role) and treats a
missing file as a fatal startup error, not something to gracefully work around: if it's missing,
this role's install is incomplete. This file is not itself a runnable script.

Files, per host, under the shared cluster/hosts/<hostname>/ directory:
  status.yml   maintenance: {active, reason, since, by}
               latched: {<subsystem>: "Ok"|"Error", ...}
  events.yml   append-only list of {number, kind, timestamp, subsystem, message, [by], [reason]}

Latch policy (the whole point of this module): a daemon can only ever move a subsystem's latch
Ok -> Error, never Error -> Ok on its own - only acknowledge_event() (driven by a sysadmin via
the `bluebanquise-cluster events ... ack` plugin) clears it. Once latched Error, a daemon calling
record_transition() again with is_error=True writes nothing further (no repeat events) until
acknowledged - the current *live* status is already visible in dynamic_cluster_state.yml /
dynamic_supervision.yml, so the latch only needs to answer "did this go bad since the last ack",
not "is it bad right now". A host under maintenance is skipped entirely: no latch changes, no
events, while active.
"""

import fcntl
import os
import yaml
from datetime import datetime, timezone

STATUS_FILENAME = 'status.yml'
EVENTS_FILENAME = 'events.yml'

OK = 'Ok'
ERROR = 'Error'


# ─── paths ──────────────────────────────────────────────────────────────────────

def _host_dir(hostname, base_path):
    return os.path.join(base_path, hostname)


def _status_path(hostname, base_path):
    return os.path.join(_host_dir(hostname, base_path), STATUS_FILENAME)


def _events_path(hostname, base_path):
    return os.path.join(_host_dir(hostname, base_path), EVENTS_FILENAME)


# ─── low-level atomic read/write (tmp file + per-host lock + os.replace, same pattern used by
# every daemon in this codebase) ──────────────────────────────────────────────────

def _default_status():
    return {
        'maintenance': {'active': False, 'reason': None, 'since': None, 'by': None},
        'latched': {},
    }


def _load_yaml(path, default):
    if not os.path.isfile(path):
        return default
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return default if data is None else data


def _atomic_write_yaml(data, dest_path, tmp_path, lock_suffix):
    host_dir = os.path.dirname(dest_path)
    os.makedirs(host_dir, exist_ok=True)
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    lock_path = os.path.join(host_dir, lock_suffix)

    with open(tmp_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    lock_fd = open(lock_path, 'w')
    try:
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        os.replace(tmp_path, dest_path)
    finally:
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
        lock_fd.close()


# ─── status.yml ─────────────────────────────────────────────────────────────────

def read_status(hostname, base_path):
    status = _load_yaml(_status_path(hostname, base_path), _default_status())
    status.setdefault('maintenance', _default_status()['maintenance'])
    status.setdefault('latched', {})
    return status


def write_status(hostname, status, base_path, tmp_path):
    dest = _status_path(hostname, base_path)
    tmp_file = os.path.join(tmp_path, 'status_{}.yml.tmp'.format(hostname))
    _atomic_write_yaml(status, dest, tmp_file, 'status.lock')


def is_in_maintenance(status):
    return bool(status.get('maintenance', {}).get('active'))


# ─── events.yml ─────────────────────────────────────────────────────────────────

def read_events(hostname, base_path):
    return _load_yaml(_events_path(hostname, base_path), [])


def _write_events(hostname, events, base_path, tmp_path):
    dest = _events_path(hostname, base_path)
    tmp_file = os.path.join(tmp_path, 'events_{}.yml.tmp'.format(hostname))
    _atomic_write_yaml(events, dest, tmp_file, 'events.lock')


def _next_event_number(events):
    return max((e.get('number', 0) for e in events), default=0) + 1


def append_event(hostname, kind, subsystem, message, base_path, tmp_path, by=None, reason=None):
    events = read_events(hostname, base_path)
    event = {
        'number': _next_event_number(events),
        'kind': kind,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'subsystem': subsystem,
        'message': message,
    }
    if by is not None:
        event['by'] = by
    if reason is not None:
        event['reason'] = reason
    events.append(event)
    _write_events(hostname, events, base_path, tmp_path)
    return event['number']


def format_event_line(event):
    return '[{}] {} - {}: {}'.format(
        event.get('number'), event.get('kind'), event.get('timestamp'), event.get('message'))


# ─── daemon-facing entry point ────────────────────────────────────────────────────

def record_transition(hostname, subsystem, is_error, message, base_path, tmp_path, logger=None):
    """Call once per host per cycle from a daemon, after it has computed this cycle's transient
    is_error boolean for `subsystem`. Returns True if an Error event was written, False
    otherwise - purely so the caller can log accordingly."""
    status = read_status(hostname, base_path)

    if is_in_maintenance(status):
        if logger:
            logger.debug('[%s] In maintenance - skipping %s event/latch check', hostname, subsystem)
        return False

    if not is_error:
        return False

    current = status['latched'].get(subsystem, OK)
    if current == ERROR:
        if logger:
            logger.debug('[%s] %s already latched Error - suppressing duplicate event',
                         hostname, subsystem)
        return False

    status['latched'][subsystem] = ERROR
    write_status(hostname, status, base_path, tmp_path)
    number = append_event(hostname, 'Error', subsystem, message, base_path, tmp_path)
    if logger:
        logger.warning('[%s] %s transitioned to Error - event #%d written, latch set',
                       hostname, subsystem, number)
    return True


# ─── sysadmin-facing entry points (called by the events/maintenance CLI plugins) ──────

def acknowledge_event(hostname, event_number, by, reason, base_path, tmp_path):
    """Returns (success: bool, message: str)."""
    events = read_events(hostname, base_path)
    target = next((e for e in events if e.get('number') == event_number), None)
    if target is None:
        return False, 'Event #{} not found for {}'.format(event_number, hostname)
    if target['kind'] != 'Error':
        return False, 'Event #{} is a {} event, not an Error - nothing to acknowledge'.format(
            event_number, target['kind'])

    subsystem = target['subsystem']
    status = read_status(hostname, base_path)
    if status['latched'].get(subsystem, OK) != ERROR:
        return False, '{} is not currently latched Error for {} (already acknowledged?)'.format(
            subsystem, hostname)

    status['latched'][subsystem] = OK
    write_status(hostname, status, base_path, tmp_path)
    append_event(
        hostname, 'Acknowledge', subsystem,
        '{}: acknowledged event #{} by {} ({})'.format(subsystem, event_number, by, reason),
        base_path, tmp_path, by=by, reason=reason)
    return True, 'Acknowledged event #{} for {} ({}) - latch cleared'.format(
        event_number, hostname, subsystem)


def set_maintenance(hostname, reason, by, base_path, tmp_path):
    status = read_status(hostname, base_path)
    if is_in_maintenance(status):
        return False, '{} is already in maintenance (since {}, by {})'.format(
            hostname, status['maintenance'].get('since'), status['maintenance'].get('by'))

    now = datetime.now(timezone.utc).isoformat()
    status['maintenance'] = {'active': True, 'reason': reason, 'since': now, 'by': by}
    write_status(hostname, status, base_path, tmp_path)
    append_event(hostname, 'MaintenanceStart', 'maintenance',
                 'maintenance started by {} ({})'.format(by, reason), base_path, tmp_path,
                 by=by, reason=reason)
    return True, 'Maintenance started for {} by {} ({})'.format(hostname, by, reason)


def clear_maintenance(hostname, reason, by, base_path, tmp_path):
    status = read_status(hostname, base_path)
    if not is_in_maintenance(status):
        return False, '{} is not currently in maintenance'.format(hostname)

    status['maintenance'] = _default_status()['maintenance']
    write_status(hostname, status, base_path, tmp_path)
    append_event(hostname, 'MaintenanceEnd', 'maintenance',
                 'maintenance ended by {} ({})'.format(by, reason), base_path, tmp_path,
                 by=by, reason=reason)
    return True, 'Maintenance ended for {} by {} ({})'.format(hostname, by, reason)
