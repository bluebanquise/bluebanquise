"""
Shared code of bluebanquise-slurm: used by its two daemons, each run by its own user:
  bluebanquise-slurm-api     (user bluebanquise-slurm-api): WebUI and REST API. It never runs a
                             Slurm command: it reads the files of the worker, and writes requests.
  bluebanquise-slurm-worker  (user bluebanquise-slurm): runs the node wrapper
                             (bluebanquise-slurm-node) as the SlurmUser, through its sudo rule.
Installed in /usr/lib/bluebanquise/bluebanquise-slurm/lib/, and imported with a plain
`import common` after adding this folder to sys.path.

Files, under data_path (/var/lib/bluebanquise-slurm), one writer each:
  state.yml               state of every node, CPUs and jobs counts (written by the worker)
  requests/<job id>.yml   a drain or resume asked by a user (written by the API, removed by the
                          worker when it starts the job)
  jobs/<job id>.yml       the job: state, result per node (written by the worker)

Every file is written atomically (temporary file in the same folder, then os.replace()), so a
reader never sees a half-written file.
"""

import grp
import logging
import os
import pwd
import re
import sys
import threading
import time
import unicodedata
import uuid

import yaml
from ClusterShell.NodeSet import NodeSet

SETTINGS_FILE = '/etc/bluebanquise/bluebanquise-slurm/bluebanquise-slurm.yml'

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

ACTIONS = ['drain', 'resume']

# A drain reason, prefix "[user] " included: same limit as the node wrapper
MAX_REASON = 200


# ─── settings, logging, privileges ─────────────────────────────────────────────

# Control characters, written as \xNN in logs (new line and carriage return as \n and \r)
CONTROL_CHARACTERS = re.compile(r'[\x00-\x1f\x7f-\x9f]')

# A log line longer than this is cut: journald splits longer lines (48K bytes by default)
MAX_LOG_LINE = 8000


def escape_control_character(match):
    return '\\x{:02x}'.format(ord(match.group()))


class OneLineFormatter(logging.Formatter):
    """One journal line per log call: text coming from a user or from Slurm (a reason) can never
    start a line of its own, so it can never forge a line (an AUDIT line for example). Same as
    common.OneLineFormatter of bluebanquise-supervision."""

    def format(self, record):
        line = super().format(record)
        line = line.replace('\n', '\\n').replace('\r', '\\r')
        line = CONTROL_CHARACTERS.sub(escape_control_character, line)
        if len(line) > MAX_LOG_LINE:
            line = line[:MAX_LOG_LINE] + '... (cut)'
        return line


def setup_logging(log_level):
    level = getattr(logging, str(log_level).upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(OneLineFormatter(LOG_FORMAT))
        root.addHandler(handler)


def load_settings(path=SETTINGS_FILE):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def load_hosts(settings):
    """Hosts of the inventory and their function group, to group nodes on the map."""
    with open(settings['hosts_file'], 'r') as f:
        data = yaml.safe_load(f) or {}
    return data.get('hosts') or {}


def drop_privileges(user):
    """If started as root, switch to the daemon user before touching any file, so every file
    keeps the right owner. Files are readable by the group of the pack (umask 027)."""
    os.umask(0o027)
    if os.getuid() != 0:
        return
    pw = pwd.getpwnam(user)
    os.initgroups(user, pw.pw_gid)
    os.setgid(pw.pw_gid)
    os.setuid(pw.pw_uid)
    os.environ['HOME'] = pw.pw_dir
    logging.debug('Dropped privileges to %s (uid=%d gid=%d, group %s)',
                  user, pw.pw_uid, pw.pw_gid, grp.getgrgid(pw.pw_gid).gr_name)


# ─── files ──────────────────────────────────────────────────────────────────────

def read_yaml(path, default):
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return default
    if data is None:
        return default
    return data


def write_yaml(path, data):
    """Atomic write: temporary file in the same folder (starting with a dot), then os.replace()."""
    folder = os.path.dirname(path)
    tmp_path = os.path.join(folder, '.{}.{}.{}.tmp'.format(
        os.path.basename(path), os.getpid(), threading.get_ident()))
    with open(tmp_path, 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    os.replace(tmp_path, path)


def valid_text(value, max_length):
    """True for one line of text: a string of 1 to max_length characters, not starting with "-",
    without control characters or line separators (the narrow no-break space of French typing is
    fine)."""
    if not isinstance(value, str) or value.strip() == '' or len(value) > max_length:
        return False
    if value.startswith('-'):
        return False
    for character in value:
        if unicodedata.category(character) in ('Cc', 'Zl', 'Zp'):
            return False
    return True


# ─── jobs ───────────────────────────────────────────────────────────────────────
#   1. write_request() (API) writes requests/<job id>.yml: action, hosts, reason, user.
#   2. The worker reads it, writes jobs/<job id>.yml (state running), removes the request, runs
#      the node wrapper for each host, and ends the job: success (every host done) or failed,
#      with the result of every host.
# A job asked but not started yet is read from its request file (state running, "Waiting for
# the worker"). Times are seconds since 1970. Job files older than JOBS_KEPT_DAYS are removed.

JOBS_KEPT_DAYS = 7


def valid_job_id(job_id):
    """True for a job id made by write_request() (a uuid): checked before building a path."""
    try:
        return str(uuid.UUID(job_id)) == job_id
    except ValueError:
        return False


def job_file(settings, job_id):
    return os.path.join(settings['jobs_path'], job_id + '.yml')


def request_file(settings, job_id):
    return os.path.join(settings['requests_path'], job_id + '.yml')


def write_request(settings, action, hosts, reason, by):
    """Ask the worker to drain or resume hosts (a nodeset of known nodes, checked by the caller).
    reason is None for resume. Returns the job, as the API shows it until the worker starts it."""
    request = {
        'job': str(uuid.uuid4()),
        'action': action,
        'hosts': hosts,
        'reason': reason,
        'by': by,
        'started': int(time.time()),
    }
    write_yaml(request_file(settings, request['job']), request)
    return pending_job(request)


def pending_job(request):
    """A request not started by the worker yet, as a job."""
    job = dict(request)
    job['state'] = 'running'
    job['message'] = 'Waiting for the worker'
    job['ended'] = None
    job['results'] = {}
    return job


def read_job(settings, job_id):
    """The job, or its request when the worker did not start it yet, or None."""
    job = read_yaml(job_file(settings, job_id), None)
    if job is not None:
        return job
    request = read_yaml(request_file(settings, job_id), None)
    if request is not None:
        return pending_job(request)
    return None


def write_job(settings, job):
    write_yaml(job_file(settings, job['job']), job)


def list_jobs(settings):
    """Every job and every request not started yet, the newest first."""
    # A job starting now is in both folders for a moment: each id once
    job_ids = set()
    for folder in [settings['jobs_path'], settings['requests_path']]:
        for filename in os.listdir(folder):
            job_id = filename[:-len('.yml')]
            if filename.endswith('.yml') and valid_job_id(job_id):
                job_ids.add(job_id)
    jobs = []
    for job_id in job_ids:
        job = read_job(settings, job_id)
        if job is not None:
            jobs.append(job)
    jobs.sort(key=lambda job: job['started'], reverse=True)
    return jobs


def job_hosts(job):
    return list(NodeSet(job['hosts']))


# ─── state of the nodes ─────────────────────────────────────────────────────────

def read_state(settings):
    """Last state read by the worker: {as_of, error, nodes, cpus, jobs}. error is None, or why the
    last read failed (nodes then keep their previous state, which gets old)."""
    return read_yaml(settings['state_file'], {'as_of': None, 'error': None, 'nodes': {},
                                              'cpus': {}, 'jobs': {}})


# Slurm states (sinfo %T) giving each state of the federator contract. A node not answering
# slurmctld has a "*" after its state: it is an error whatever its state.
ERROR_STATES = ['down', 'fail', 'failing', 'inval', 'invalid', 'error']
MAINTENANCE_STATES = ['drain', 'drained', 'draining']


def node_state(node):
    """State of a node for the pages and the federator contract: (state, text, drained).
         maintenance  drained or draining: out of production, on purpose
         error        down, failed, or not answering slurmctld
         unknown      state unknown to slurmctld
         ok           idle, allocated, mixed, completing, reserved...
    drained is True once a drained node has no job left (Automation waits for it). The reason
    is shown only when the node is out of production: Slurm keeps the last reason after a
    resume."""
    slurm_state = node['state']
    not_responding = slurm_state.endswith('*')
    # Flags after the state: * not responding, ~ powered off, # powering up, % powering down,
    # $ maintenance reservation, @ reboot pending, ^ rebooting, ! pending power down, - planned
    base = slurm_state.rstrip('*~#%$@^!-').split('+')[0]
    drained = base == 'drained'
    if not_responding:
        state = 'error'
    elif base in ERROR_STATES:
        state = 'error'
    elif base in MAINTENANCE_STATES:
        state = 'maintenance'
    elif base == 'unknown':
        state = 'unknown'
    else:
        state = 'ok'
    text = slurm_state
    if not_responding:
        text = slurm_state + ' (not responding)'
    if state != 'ok' and node['reason'] != '':
        text = text + ': ' + node['reason']
    return state, text, drained
