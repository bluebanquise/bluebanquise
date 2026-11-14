#!/usr/lib/bluebanquise/venv/bin/python3
# DUPLICATED FILE: any change made to this file must be made identically in every copy below.
# Copies:
#   collections/management/roles/bluebanquise_supervision/files/lib/webui_auth.py
"""
webui_auth.py: users, levels and audit lines, shared by every BlueBanquise WebUI pack.

Users
  Read from /etc/bluebanquise/webui/users.yml (inventory variable bluebanquise_webui_users,
  templated by every pack role), then from /etc/bluebanquise/webui/users.d/*.yml (service
  accounts, each file dropped by the role owning the account). Same format in both files:

    users:
      "jdoe": {"password_hash": "scrypt:32768:8:1$...", "role": "operator"}

  The files are checked at every request, and read again as soon as one of them changes:
  users.yml is shared by every pack, and the role of one pack can change it without restarting
  the daemons of the other packs.

Levels, each one can do everything the previous one can:
  viewer    cluster overview, and the summary of every pack
  operator  everything about hosts: pack pages, actions
  admin     inventory editing, and anything marked admin later

In a pack:

  import webui_auth

  # Who can do what: minimum level of each route, by the name of its function.
  # A route missing here is refused to everyone.
  ROUTE_LEVELS = {
      'get_hosts': 'operator',
      ...
  }

  @app.before_request
  def check_user():
      return webui_auth.check_request(ROUTE_LEVELS)

  # In a write route, once the action is done ('ok') or refused by the pack ('failed'):
  webui_auth.audit('maintenance.start', hostname, 'ok', message)

  # In main(), before serving:
  webui_auth.start('supervision')

  # The logged in user, in any route: g.user['name'], g.user['role']

Print the hash of a password, for bluebanquise_webui_users:
  /usr/lib/bluebanquise/venv/bin/python3 webui_auth.py
"""

import getpass
import glob
import json
import logging
import os
import sys

import yaml
from flask import Response, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

USERS_FILE = '/etc/bluebanquise/webui/users.yml'
USERS_FOLDER = '/etc/bluebanquise/webui/users.d'

# Name shown by the browser in its login window. The same in every pack: after one login, the
# browser sends the same user and password to every pack (same address, same realm).
REALM = 'BlueBanquise'

# From the lowest to the highest
LEVELS = ['viewer', 'operator', 'admin']

WRITE_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')

# An audit line longer than this is cut: journald splits longer lines (48K bytes by default), and
# the second part would be a line of its own. Values are ASCII (JSON escapes the others).
MAX_AUDIT_LINE = 8000

# Checked when the user name is unknown, so that the answer takes as long as for a known user
# (about 80 ms): the response time does not tell which user names exist.
UNKNOWN_USER_HASH = generate_password_hash('unknown user')

# Name of the pack using this module, for audit lines. Set by start().
pack = None

# Last users read, and the state of the files they were read from: (files state, users)
users_cache = (None, {})


def start(pack_name):
    """Called once by the pack, in main(), before serving."""
    global pack
    pack = pack_name
    users = load_users()
    logging.info('%d WebUI user(s) in %s and %s', len(users), USERS_FILE, USERS_FOLDER)
    if len(users) == 0:
        logging.warning('No WebUI user: nobody can log in (see bluebanquise_webui_users)')


# ─── users ──────────────────────────────────────────────────────────────────────

def read_users_file(path):
    """Users of one file, {name: {'password_hash': ..., 'role': ...}}, or {} when unreadable."""
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as error:
        logging.error('Can not read WebUI users file %s: %s', path, error)
        return {}
    if not isinstance(data, dict) or data.get('users') is None:
        return {}
    if not isinstance(data['users'], dict):
        logging.error('WebUI users file %s: "users" must be a mapping of user names', path)
        return {}
    return data['users']


def users_files_state(paths):
    """Modification time and size of each file: they change when a file is written."""
    state = []
    for path in paths:
        try:
            stat = os.stat(path)
            state.append((path, stat.st_mtime_ns, stat.st_size))
        except OSError:
            state.append((path, None, None))
    return state


def load_users():
    """All users: users.yml first, then users.d/*.yml in alphabetical order. A user already
    defined in a previous file is ignored: a file of users.d can not replace a user of users.yml.
    Files are read again only when one of them changed, so a mistake in a file is logged once,
    not at every request."""
    global users_cache
    paths = [USERS_FILE] + sorted(glob.glob(os.path.join(USERS_FOLDER, '*.yml')))
    state = users_files_state(paths)
    if state == users_cache[0]:
        return users_cache[1]

    users = {}
    for path in paths:
        for name, user in read_users_file(path).items():
            if name in users:
                logging.error('WebUI users file %s: user %s already defined, ignored', path, name)
                continue
            if not isinstance(user, dict) or not user.get('password_hash') or user.get('role') not in LEVELS:
                logging.error('WebUI users file %s: user %s needs a password_hash and a role (%s), ignored',
                              path, name, ', '.join(LEVELS))
                continue
            users[name] = user

    # One assignment: other threads see the old or the new users, never a mix
    users_cache = (state, users)
    return users


def password_ok(user, password):
    try:
        return check_password_hash(str(user['password_hash']), password)
    except ValueError:
        # Not a hash made by generate_password_hash
        logging.error('WebUI user has an invalid password_hash, see bluebanquise_webui_users')
        return False


def allowed(user, level, host=None):
    """True when the user has at least this level. host is not used yet: it is the place where
    tenants will be checked later (a user limited to some hosts), without changing any caller."""
    return LEVELS.index(user['role']) >= LEVELS.index(level)


# ─── checks of every request ────────────────────────────────────────────────────

def login_required():
    """Answer asking for a user and password: the browser shows its login window."""
    return Response('Authentication required\n', 401, {'WWW-Authenticate': 'Basic realm="' + REALM + '"'})


def refuse(code, message):
    """Answer refusing the request of a logged in user. A refused write gets its AUDIT line."""
    if request.method in WRITE_METHODS:
        audit(request.method + ' ' + request.path, '', 'refused', message)
    return jsonify({'error': message}), code


def check_request(route_levels):
    """Run before every request of the pack. Returns None when the request can go on, or the
    answer refusing it:
      401  no user, unknown user or wrong password (the browser then shows its login window)
      415  a write request (POST, PUT, PATCH, DELETE) not sent as JSON
      403  the user has not the level needed by the route, or the route has no valid level in
           route_levels
    Every request is checked, even from 127.0.0.1: otherwise any account of the management host
    could use the API without a password."""
    auth = request.authorization
    if auth is None:
        return login_required()
    users = load_users()
    name = auth.username
    password = auth.password or ''
    if name in users:
        password_good = password_ok(users[name], password)
    else:
        check_password_hash(UNKNOWN_USER_HASH, password)
        password_good = False
    if not password_good:
        logging.warning('Authentication failed for user %r', name)
        return login_required()
    g.user = {'name': name, 'role': users[name]['role']}

    # A browser can not send a JSON request to another web site without its agreement (which
    # packs never give), while a simple form can be sent from anywhere: writes must be JSON, so
    # another web site can not use the credentials a browser keeps to act here.
    if request.method in WRITE_METHODS and not request.is_json:
        return refuse(415, 'POST, PUT, PATCH and DELETE requests must be sent as JSON (Content-Type: application/json)')

    # No route matched (Flask answers 404 or 405 itself)
    if request.endpoint is None:
        return None

    level = route_levels.get(request.endpoint)
    if level not in LEVELS:
        logging.error('Route %s has no valid level in ROUTE_LEVELS (%r): refused to everyone', request.endpoint, level)
        return refuse(403, 'This route has no valid access level, refused')
    if not allowed(g.user, level):
        logging.warning('%s %s refused to %s: %s level needed, user is %s',
                        request.method, request.path, name, level, g.user['role'])
        return refuse(403, '{} level needed, {} is {}'.format(level, name, g.user['role']))
    return None


# ─── audit ──────────────────────────────────────────────────────────────────────

def audit(action, hosts, result, message):
    """One line per write request, in the journal of the pack, with the same format in every pack:

    AUDIT user="jdoe" pack="supervision" action="maintenance.start" hosts="c001" result="ok" job="" message="..."

    result: ok (done), failed (refused by the pack: not in maintenance...), refused (refused by
    check_request: level, not JSON; action is then the method and path of the request).
    job is the Automation job id, sent by Automation in the X-BlueBanquise-Job header (any user
    can send this header: it says where a request comes from, it proves nothing).
    Every value is quoted as JSON: quotes, new lines and other control characters are escaped,
    so no text can write a fake second line. Printed, not logged: the log level of the pack must
    never hide an audit line."""
    line = 'AUDIT user={} pack={} action={} hosts={} result={} job={} message={}'.format(
        json.dumps(g.user['name']),
        json.dumps(pack),
        json.dumps(action),
        json.dumps(hosts),
        json.dumps(result),
        json.dumps(request.headers.get('X-BlueBanquise-Job', '')),
        json.dumps(message),
    )
    if len(line) > MAX_AUDIT_LINE:
        line = line[:MAX_AUDIT_LINE] + '... (cut)'
    sys.stdout.write(line + '\n')
    sys.stdout.flush()


# ─── password hash, for the inventory ──────────────────────────────────────────

def hash_password():
    """Ask a password twice, print its hash for bluebanquise_webui_users."""
    password = getpass.getpass('Password: ')
    if password != getpass.getpass('Password again: '):
        print('Error: passwords do not match')
        sys.exit(1)
    print(generate_password_hash(password))


if __name__ == '__main__':
    hash_password()
