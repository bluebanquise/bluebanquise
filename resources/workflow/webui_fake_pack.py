#!/usr/bin/env python3
"""
webui_fake_pack.py: a fake WebUI pack, for tests of the federator only. Never install it on a
real cluster: it accepts any user and password.

It answers the federator contract (version 1) with what a JSON file says, read again at every
request, so a test changes the answers by writing the file:

  GET <prefix>/api/summary               the "summary" value of the file
  GET <prefix>/api/hosts/<host>/summary  the "hosts" value of the host, 404 if not in the file
  anything else                          404

A request without an Authorization header gets 401, as a real pack. Example of file:

  {"summary": {"contract": 1, "pack": "fake", "version": "0.0.1", "as_of": 1794746670,
               "refresh": 60, "cluster": {"state": "ok", "text": "1 ok"},
               "hosts": {"c001": {"state": "ok", "text": "ok", "url": "hosts/c001"}}},
   "hosts": {"c001": {"contract": 1, "as_of": 1794746670, "refresh": 60, "state": "ok",
                      "text": "ok", "url": "hosts/c001"}}}

Run it, then add the Apache lines below (as a pack role would):
  python3 webui_fake_pack.py 8099 /webui/fake answers.json

  ProxyPass "/webui/fake/" "http://127.0.0.1:8099/webui/fake/"
  ProxyPassReverse "/webui/fake/" "http://127.0.0.1:8099/webui/fake/"

An "as_of" value of "now" is replaced by the current time, so a test file stays fresh.
"""

import http.server
import json
import sys
import time

port = int(sys.argv[1])
prefix = sys.argv[2]
answers_file = sys.argv[3]


def fresh(value):
    """Replace every "as_of": "now" by the current time."""
    if isinstance(value, dict):
        result = {}
        for key in value:
            if key == 'as_of' and value[key] == 'now':
                result[key] = int(time.time())
            else:
                result[key] = fresh(value[key])
        return result
    return value


class Handler(http.server.BaseHTTPRequestHandler):

    def answer(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get('Authorization') is None:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="BlueBanquise"')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        with open(answers_file, 'r') as f:
            answers = fresh(json.load(f))
        path = self.path
        if path == prefix + '/api/summary':
            self.answer(200, answers['summary'])
            return
        if path.startswith(prefix + '/api/hosts/') and path.endswith('/summary'):
            host = path[len(prefix + '/api/hosts/'):-len('/summary')]
            if host in answers['hosts']:
                self.answer(200, answers['hosts'][host])
                return
        self.answer(404, {'error': 'not in the fake pack: ' + path})


http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
