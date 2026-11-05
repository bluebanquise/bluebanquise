// bluebanquise-supervision WebUI: plain JavaScript, no framework, data from the REST API.
// Data coming from hosts (probe output, messages) is always inserted with textContent, never as
// HTML, so it can never be interpreted by the browser.

const REFRESH_SECONDS = 30;

const STATE_TAGS = {
  ok: 'is-success',
  error: 'is-danger',
  maintenance: 'is-link',
  unknown: 'is-light',
};


// Create an element, with optional CSS classes and text
function element(tag, classes, text) {
  const node = document.createElement(tag);
  if (classes) {
    node.className = classes;
  }
  if (text !== undefined && text !== null) {
    node.textContent = text;
  }
  return node;
}


// Call the REST API. Returns the decoded JSON answer, throws an Error with the API message.
async function api(method, path, body) {
  const options = {method: method, headers: {}};
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }
  // window.location.origin never holds credentials: a page opened as http://user:pass@host/
  // can not fetch a relative URL, the browser refuses URLs with credentials.
  const response = await fetch(window.location.origin + path, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || ('HTTP ' + response.status));
  }
  return data;
}


// ─── dark mode ──────────────────────────────────────────────────────────────────
// Bulma follows the system theme by default. The moon/sun button forces the other one, saved in
// the browser (localStorage), and applied early by a small script in the <head> of each page.

function savedSetting(name) {
  try {
    return localStorage.getItem(name);
  } catch (error) {
    return null;
  }
}

function saveSetting(name, value) {
  try {
    localStorage.setItem(name, value);
  } catch (error) {
    // Storage not available (private window...): the setting is just not remembered
  }
}

function currentTheme() {
  const forced = document.documentElement.getAttribute('data-theme');
  if (forced) {
    return forced;
  }
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function showThemeIcon() {
  // In dark mode show the sun (switch to light), in light mode the moon (switch to dark)
  const dark = currentTheme() === 'dark';
  document.getElementById('icon-sun').classList.toggle('is-hidden', !dark);
  document.getElementById('icon-moon').classList.toggle('is-hidden', dark);
}

function setupThemeButton() {
  showThemeIcon();
  document.getElementById('theme-toggle').addEventListener('click', function () {
    const theme = currentTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    saveSetting('theme', theme);
    showThemeIcon();
  });
}


// ─── index page: global report, cluster map or hosts list ──────────────────────

// Message of a host, displayed on map tiles hover and in the list
function hostMessage(host) {
  let message = host.host + ': ' + host.state;
  if (host.failed.length > 0) {
    message = message + ' (' + host.failed.join(', ') + ')';
  }
  return message;
}

function renderMap(container, groups, groupNames) {
  for (const groupName of groupNames) {
    const box = element('div', 'box');
    box.appendChild(element('p', 'has-text-weight-bold mb-2', groupName + ' (' + groups[groupName].length + ')'));
    for (const host of groups[groupName]) {
      const tile = element('a', 'tile-host state-' + host.state);
      tile.href = '/' + encodeURIComponent(host.host);
      tile.title = hostMessage(host);
      box.appendChild(tile);
    }
    container.appendChild(box);
  }
}

function renderList(container, groups, groupNames) {
  const table = element('table', 'table is-fullwidth is-narrow');
  const head = element('thead');
  const headRow = element('tr');
  headRow.appendChild(element('th', null, 'Host'));
  headRow.appendChild(element('th', null, 'Group'));
  headRow.appendChild(element('th', null, 'Status'));
  head.appendChild(headRow);
  table.appendChild(head);
  const body = element('tbody');
  for (const groupName of groupNames) {
    for (const host of groups[groupName]) {
      const row = element('tr', 'row-host state-' + host.state);
      const hostCell = element('td');
      const link = element('a', 'has-text-weight-bold', host.host);
      link.href = '/' + encodeURIComponent(host.host);
      hostCell.appendChild(link);
      row.appendChild(hostCell);
      row.appendChild(element('td', null, groupName));
      row.appendChild(element('td', null, hostMessage(host)));
      body.appendChild(row);
    }
  }
  table.appendChild(body);
  container.appendChild(table);
}


async function refreshIndex() {
  const data = await api('GET', '/api/hosts');

  for (const state of ['ok', 'error', 'maintenance', 'unknown']) {
    document.getElementById('count-' + state).textContent = data.counts[state];
  }

  const onlyError = document.getElementById('filter-error').checked;
  const onlyMaintenance = document.getElementById('filter-maintenance').checked;

  // Group hosts by function group, keeping only the ones passing the filters
  const groups = {};
  for (const host of data.hosts) {
    if (onlyError || onlyMaintenance) {
      const keep = (onlyError && host.state === 'error') || (onlyMaintenance && host.state === 'maintenance');
      if (!keep) {
        continue;
      }
    }
    if (!(host.group in groups)) {
      groups[host.group] = [];
    }
    groups[host.group].push(host);
  }

  const container = document.getElementById('hosts');
  container.replaceChildren();
  const groupNames = Object.keys(groups).sort();
  if (groupNames.length === 0) {
    container.appendChild(element('p', 'has-text-grey', 'No host to display.'));
  } else if (savedSetting('view') === 'list') {
    renderList(container, groups, groupNames);
  } else {
    renderMap(container, groups, groupNames);
  }

  document.getElementById('updated').textContent = 'Updated ' + new Date().toLocaleTimeString();
}

function showViewButtons() {
  const list = savedSetting('view') === 'list';
  document.getElementById('view-list').classList.toggle('is-selected', list);
  document.getElementById('view-list').classList.toggle('is-link', list);
  document.getElementById('view-map').classList.toggle('is-selected', !list);
  document.getElementById('view-map').classList.toggle('is-link', !list);
}

function indexPage() {
  setupThemeButton();
  showViewButtons();
  document.getElementById('view-map').addEventListener('click', function () {
    saveSetting('view', 'map');
    showViewButtons();
    refreshIndex();
  });
  document.getElementById('view-list').addEventListener('click', function () {
    saveSetting('view', 'list');
    showViewButtons();
    refreshIndex();
  });
  document.getElementById('filter-error').addEventListener('change', refreshIndex);
  document.getElementById('filter-maintenance').addEventListener('change', refreshIndex);
  refreshIndex();
  setInterval(refreshIndex, REFRESH_SECONDS * 1000);
}


// ─── host page ─────────────────────────────────────────────────────────────────

const hostname = decodeURIComponent(window.location.pathname.substring(1));

function showMessage(text, isError) {
  const message = document.getElementById('message');
  message.textContent = text;
  message.className = 'notification ' + (isError ? 'is-danger' : 'is-success');
}

function probeBlock(name, result) {
  // One <details> per probe: name and status visible, output folded
  const details = element('details', 'box p-3 mb-2');
  if (result.error) {
    details.open = true;
  }
  const summary = element('summary');
  summary.appendChild(element('span', 'tag mr-2 ' + (result.error ? 'is-danger' : 'is-success'), result.error ? 'ERROR' : 'OK'));
  let text = name;
  if (result.exit_code !== undefined) {
    text = text + ' - exit code ' + result.exit_code;
  }
  summary.appendChild(element('span', null, text + ', ' + result.duration + 's'));
  details.appendChild(summary);

  if (result.args !== undefined && result.args !== null) {
    details.appendChild(element('p', 'is-size-7 mt-2', 'args: ' + result.args));
  }
  if (result.findings !== undefined && result.findings.length > 0) {
    const list = element('ul', 'mt-2');
    for (const finding of result.findings) {
      list.appendChild(element('li', null, finding));
    }
    details.appendChild(list);
  }
  const output = ((result.stdout || '') + (result.stderr || '')).trim();
  if (output !== '') {
    details.appendChild(element('pre', 'probe-output mt-2', output));
  }
  return details;
}

async function refreshHost() {
  const data = await api('GET', '/api/hosts/' + encodeURIComponent(hostname));
  const summary = data.summary;

  document.getElementById('hostname').textContent = hostname;
  const state = document.getElementById('state');
  state.textContent = summary.state;
  state.className = 'tag is-medium ' + STATE_TAGS[summary.state];
  document.getElementById('host-info').textContent = 'Group ' + summary.group;
  document.title = 'Inquisitor - ' + hostname;

  const maintenanceInfo = document.getElementById('maintenance-info');
  if (data.maintenance.active) {
    maintenanceInfo.textContent = 'In maintenance since ' + data.maintenance.since + ' by ' +
      data.maintenance.by + ': ' + data.maintenance.reason;
    maintenanceInfo.classList.remove('is-hidden');
  } else {
    maintenanceInfo.classList.add('is-hidden');
  }
  const latchedInfo = document.getElementById('latched-info');
  if (summary.latched) {
    latchedInfo.textContent = 'Error not acknowledged yet: see the events below, then acknowledge it.';
    latchedInfo.classList.remove('is-hidden');
  } else {
    latchedInfo.classList.add('is-hidden');
  }

  const probes = document.getElementById('probes');
  probes.replaceChildren();
  const probeInfo = document.getElementById('probe-info');
  if (data.probes === null) {
    probeInfo.textContent = 'Never probed.';
  } else {
    let text = data.probes.started + ' -> ' + data.probes.finished;
    if (data.probes.request_id) {
      text = text + ' (on demand)';
    }
    if (data.probes.ssh === false) {
      text = text + ' - SSH connection failed';
    }
    probeInfo.textContent = text;
    for (const name of Object.keys(data.probes.probes)) {
      probes.appendChild(probeBlock(name, data.probes.probes[name]));
    }
    if (data.probes.drift !== undefined) {
      probes.appendChild(probeBlock('drift check', data.probes.drift));
    }
  }

  const eventsData = await api('GET', '/api/hosts/' + encodeURIComponent(hostname) + '/events');
  const events = document.getElementById('events');
  events.replaceChildren();
  // Newest first
  for (const event of eventsData.events.slice().reverse()) {
    const row = element('tr');
    row.appendChild(element('td', null, event.number));
    row.appendChild(element('td', null, event.time));
    const kind = element('td');
    let kindClass = 'tag';
    if (event.kind === 'Error') {
      kindClass = 'tag is-danger';
    } else if (event.kind.startsWith('Maintenance')) {
      kindClass = 'tag is-link';
    } else if (event.kind === 'Acknowledge') {
      kindClass = 'tag is-success';
    }
    kind.appendChild(element('span', kindClass, event.kind));
    row.appendChild(kind);
    row.appendChild(element('td', null, event.by || ''));
    row.appendChild(element('td', null, event.message));
    events.appendChild(row);
  }
}

// Run an action needing the text field (reason or note), then refresh the page
async function textAction(method, path, field) {
  const text = document.getElementById('text').value.trim();
  if (text === '') {
    showMessage('Please write a reason (or the note text) first.', true);
    return;
  }
  const body = {};
  body[field] = text;
  try {
    const data = await api(method, '/api/hosts/' + encodeURIComponent(hostname) + path, body);
    showMessage(data.message, false);
    document.getElementById('text').value = '';
  } catch (error) {
    showMessage(error.message, true);
  }
  await refreshHost();
}

// Request a probe, then wait for its result (the probe daemon writes the request id in it)
async function probeNow() {
  const button = document.getElementById('button-probe');
  button.classList.add('is-loading');
  try {
    const request = await api('POST', '/api/hosts/' + encodeURIComponent(hostname) + '/probe', {});
    showMessage(request.message + ', waiting for the result...', false);
    for (let i = 0; i < 300; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const data = await api('GET', '/api/hosts/' + encodeURIComponent(hostname));
      if (data.probes !== null && data.probes.request_id === request.request_id) {
        showMessage('Probe done.', false);
        break;
      }
    }
  } catch (error) {
    showMessage(error.message, true);
  }
  button.classList.remove('is-loading');
  await refreshHost();
}

function hostPage() {
  setupThemeButton();
  document.getElementById('button-probe').addEventListener('click', probeNow);
  document.getElementById('button-acknowledge').addEventListener('click', function () {
    textAction('POST', '/acknowledge', 'reason');
  });
  document.getElementById('button-maintenance-start').addEventListener('click', function () {
    textAction('POST', '/maintenance', 'reason');
  });
  document.getElementById('button-maintenance-stop').addEventListener('click', function () {
    textAction('DELETE', '/maintenance', 'reason');
  });
  document.getElementById('button-note').addEventListener('click', function () {
    textAction('POST', '/notes', 'text');
  });
  refreshHost();
  setInterval(refreshHost, REFRESH_SECONDS * 1000);
}
