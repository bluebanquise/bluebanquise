// DUPLICATED FILE: any change made to this file must be made identically in every copy below.
// Copies:
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

// URL prefix of the pack (for example /webui/supervision), and host of a host page (empty on
// other pages). Both are written by the server in the <body> tag of webui_base.html.
const SCRIPT_ROOT = document.body.dataset.scriptRoot;
const HOST = document.body.dataset.host;


// Call the REST API of this pack, for example apiRequest('GET', 'api/hosts').
// path has no leading /. body is optional, sent as JSON.
// Returns the JSON answer. On error, shows a notification and throws an Error.
// A success answer with a "message" field also shows a notification.
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

  if (data !== null && data.message) {
    showNotification('is-success', data.message);
  }
  return data;
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
