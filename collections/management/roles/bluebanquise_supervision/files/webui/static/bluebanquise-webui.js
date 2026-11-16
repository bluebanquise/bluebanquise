// DUPLICATED FILE: any change made to this file must be made identically in every copy below.
// Copies:
//   collections/management/roles/bluebanquise_federator/files/webui/static/bluebanquise-webui.js
//   collections/management/roles/bluebanquise_operation/files/webui/static/bluebanquise-webui.js
//   collections/management/roles/bluebanquise_slurm/files/webui/static/bluebanquise-webui.js
//   collections/management/roles/bluebanquise_supervision/files/webui/static/bluebanquise-webui.js
//
// bluebanquise-webui.js: helpers shared by every WebUI pack. Plain JavaScript, no framework.
//
// A page uses it like this:
//   - its fields are written in the page HTML, each with an id;
//   - a load function calls apiRequest() and fills the fields one by one, with textContent;
//   - a save function reads the fields one by one and sends them with apiRequest().
//
// Data coming from the API is always inserted with textContent, never as HTML (innerHTML), so it
// can never be interpreted by the browser.
//
// This file is loaded at the end of <body>, so the page is already there when it runs.

// URL prefix of the pack (for example /webui/supervision), host of a host page (empty on other
// pages), and level of the logged in user (viewer, operator, admin). All are written by the
// server in the <body> tag of webui_base.html. LEVEL only hides what the user can not use: every
// request is still checked by the server.
const SCRIPT_ROOT = document.body.dataset.scriptRoot;
const HOST = document.body.dataset.host;
const LEVEL = document.body.dataset.level;


// Call the REST API of this pack, for example apiRequest('GET', 'api/hosts').
// path has no leading /. body is optional, sent as JSON.
// Returns the JSON answer. On error, shows a notification and throws an Error.
// A success answer to a write request (POST, PUT, PATCH, DELETE) with a "message" field also
// shows a notification. GET answers are data: a "message" field in them (a job) is not shown.
async function apiRequest(method, path, body) {
  const options = {method: method, headers: {}};
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }

  // window.location.origin never holds credentials: a page opened as http://user:pass@host/
  // can not fetch a relative URL, the browser refuses URLs with credentials.
  const url = window.location.origin + SCRIPT_ROOT + '/' + path;

  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    showNotification('is-danger', 'Server not reachable: ' + error.message);
    throw error;
  }

  // Errors from Apache (pack daemon stopped...) are HTML pages, not JSON
  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    let message = method + ' ' + path + ': HTTP error ' + response.status;
    if (data !== null && data.error) {
      message = data.error;
    }
    showNotification('is-danger', message);
    throw new Error(message);
  }

  if (method !== 'GET' && data !== null && data.message) {
    showNotification('is-success', data.message);
  }
  return data;
}


// Call the REST API of a pack, this one or another one, for example
// packRequest('supervision', 'api/summary'). Shows no notification and never throws: the page
// shows what went wrong where the data would be (a pack that is stopped must not fill the screen
// with notifications at every refresh). Returns:
//   {ok: true, status: 200, data: <JSON answer>}
//   {ok: false, status: <HTTP code, 0 when not reachable>, error: '<what went wrong>',
//    answeredByPack: true when the pack itself answered the error (JSON {"error"}), false when
//    Apache did (pack stopped or not installed: an HTML page)}
async function packRequest(pack, path) {
  // Packs are side by side: /webui/cluster -> /webui/supervision/api/summary
  const packsRoot = SCRIPT_ROOT.substring(0, SCRIPT_ROOT.lastIndexOf('/'));
  const url = window.location.origin + packsRoot + '/' + pack + '/' + path;

  let response;
  try {
    // A pack that hangs is given up after 10 seconds
    response = await fetch(url, {signal: AbortSignal.timeout(10000)});
  } catch (error) {
    return {ok: false, status: 0, error: 'not reachable (' + error.message + ')', answeredByPack: false};
  }

  // Errors from Apache (pack daemon stopped, pack not installed...) are HTML pages, not JSON
  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    let message = 'HTTP error ' + response.status;
    if (data !== null && data.error) {
      message = data.error;
    }
    return {ok: false, status: response.status, error: message, answeredByPack: data !== null};
  }
  if (data === null) {
    return {ok: false, status: response.status, error: 'answer is not JSON', answeredByPack: false};
  }
  return {ok: true, status: response.status, data: data};
}


// ─── summaries of packs (federator contract) ────────────────────────────────────
// as_of is the time of the data, in seconds since 1970, refresh the seconds between two
// refreshes of the data of its pack. Ages are computed with the clock of the browser.

// Data older than 3 times the refresh period of its pack is stale: shown grey, never green
// (a stale green is worse than a grey). A pack giving no refresh period is never stale.
function isStale(asOf, refresh) {
  if (refresh === undefined || refresh === null) {
    return false;
  }
  return Date.now() / 1000 - asOf > 3 * refresh;
}

// Age of data, for example "5 min ago"
function ageText(asOf) {
  const seconds = Math.max(0, Math.round(Date.now() / 1000 - asOf));
  if (seconds < 120) {
    return seconds + ' s ago';
  }
  if (seconds < 7200) {
    return Math.round(seconds / 60) + ' min ago';
  }
  if (seconds < 172800) {
    return Math.round(seconds / 3600) + ' h ago';
  }
  return Math.round(seconds / 86400) + ' days ago';
}


// Show a message in the top right corner. type: is-success, is-danger, is-warning, is-info.
// Success messages close after 5 seconds, others after 15 seconds.
function showNotification(type, message) {
  const box = element('div', 'notification ' + type);
  const close = element('button', 'delete');
  close.addEventListener('click', function () {
    box.remove();
  });
  box.appendChild(close);
  box.appendChild(element('span', null, message));
  document.getElementById('notifications').appendChild(box);

  let seconds = 15;
  if (type === 'is-success') {
    seconds = 5;
  }
  setTimeout(function () {
    box.remove();
  }, seconds * 1000);
}


// Create an element, with optional CSS classes and text (always inserted as text, never as HTML)
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


// ─── settings remembered by the browser ─────────────────────────────────────────

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


// ─── dark mode ──────────────────────────────────────────────────────────────────
// Bulma follows the system theme by default. The moon/sun button forces the other one, saved in
// the browser, and applied early by a small script in the <head> of webui_base.html.

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

function switchTheme() {
  let theme = 'dark';
  if (currentTheme() === 'dark') {
    theme = 'light';
  }
  document.documentElement.setAttribute('data-theme', theme);
  saveSetting('theme', theme);
  showThemeIcon();
}

showThemeIcon();
document.getElementById('theme-toggle').addEventListener('click', switchTheme);
