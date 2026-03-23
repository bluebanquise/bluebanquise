#!/usr/bin/env python3
import yaml
from flask import Flask, render_template_string, abort

app = Flask(__name__, static_url_path='/static')

RESULTS_FILE = "results.yaml"

# -----------------------------
# Templates
# -----------------------------

MAIN_TEMPLATE2 = """
<!DOCTYPE html>
<html data-theme="light">
<head>
    <title>Healthcheck Dashboard</title>
    <link rel="stylesheet" href="/static/bulma.min.css">
    <link rel="stylesheet" href="/static/bulma_switch.min.css">
    <meta http-equiv="refresh" content="30">
</head>

<body>

<!-- NAVBAR -->
<nav class="navbar is-dark" role="navigation">
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
      <strong>Health Dashboard</strong>
    </a>
  </div>

  <div class="navbar-end">
      <div class="navbar-item">
        <span id="theme-icon" style="cursor:pointer; font-size:20px;" onclick="toggleDarkMode()">🌙</span>
    </div>
  </div>
</nav>

<section class="section">
    <div class="container">

        <h1 class="title">Remote Hosts</h1>
        <p class="subtitle">Auto-refreshing every 30 seconds</p>

        <div class="columns">

            <div class="column is-3">
                <h2 class="subtitle"> {{ error_count }} hosts in error </h2>
            </div>

            <div class="column is-3">
                <div class="field">
                    <label class="switch is-rounded">
                        <input id="error-filter" type="checkbox" onclick="filterHosts()">
                        <span class="check"></span>
                        <span class="control-label">Show only errors</span>
                    </label>
                </div>
            </div>
            <div class="column is-3">
                <div class="field">
                    <input id="host-search" class="input is-small" type="text" placeholder="Search host…" oninput="filterHosts()">
                </div>
            </div>

            <div class="column is-3">
                <button class="button is-small is-info" onclick="toggleView()">Toggle Table View</button>
            </div>
        </div>
  
        <div id="tile-view" class="columns is-multiline">

            <table id="table-view" class="table is-striped is-hoverable is-fullwidth" style="display:none;">
                <thead>
                    <tr>
                        <th>Host</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for host, data in results.items() %}
                    <tr class="host-row"
                        data-host="{{ host }}"
                        data-error="{{ 'true' if data.errors else 'false' }}"
                        onclick="window.location='/host/{{ host }}'">
                        <td>{{ host }}</td>
                        <td>
                            {% if data.errors %}
                                <span class="tag is-danger">ERROR</span>
                            {% else %}
                                <span class="tag is-success">OK</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>


            {% for host, data in results.items() %}
            <div class="column is-2 host-tile"
                        data-host="{{ host }}"
                        data-error="{{ 'true' if data.errors else 'false' }}">
                <a href="/host/{{ host }}">
                    <div class="box has-text-centered {% if data.errors %}has-background-danger{% else %}has-background-success{% endif %}">
                        <h2 class="title is-4">{{ host }}</h2>
                        {% if data.errors %}
                            <span class="tag is-danger is-light is-medium">ERROR</span>
                        {% else %}
                            <span class="tag is-success is-light is-medium">OK</span>
                        {% endif %}
                    </div>
                </a>
            </div>
            {% endfor %}

        </div>

    </div>
</section>

<script>

function toggleView() {
    const tile = document.getElementById("tile-view");
    const table = document.getElementById("table-view");

    if (tile.style.display === "none") {
        tile.style.display = "";
        table.style.display = "none";
    } else {
        tile.style.display = "none";
        table.style.display = "";
    }

    filterHosts();  // keep filters applied
}

function filterHosts() {
    const query = document.getElementById("host-search").value.toLowerCase();
    const onlyErrors = document.getElementById("error-filter").checked;
    const tiles = document.querySelectorAll(".host-tile");
    const rows = document.querySelectorAll(".host-row");

    tiles.forEach(tile => {
        const name = tile.getAttribute("data-host").toLowerCase();
        const isError = tile.getAttribute("data-error") === "true";

        let visible = true;

        // Apply search filter
        if (!name.includes(query)) {
            visible = false;
        }

        // Apply error-only filter
        if (onlyErrors && !isError) {
            visible = false;
        }

        tile.style.display = visible ? "" : "none";
    });

    rows.forEach(row => {
        const name = row.getAttribute("data-host").toLowerCase();
        const isError = row.getAttribute("data-error") === "true";

        let visible = true;

        if (!name.includes(query)) visible = false;
        if (onlyErrors && !isError) visible = false;

        row.style.display = visible ? "" : "none";
    });

    
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");

    const icon = document.getElementById("theme-icon");
    if (document.body.classList.contains("dark-mode")) {
        icon.textContent = "☀️";
        localStorage.setItem("theme", "dark");
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        icon.textContent = "🌙";
        localStorage.setItem("theme", "light");
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

window.onload = function() {
    const icon = document.getElementById("theme-icon");
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        icon.textContent = "☀️";
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        icon.textContent = "🌙";
        document.documentElement.setAttribute('data-theme', 'dark');
    }
};
</script>


</body>
</html>

"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html data-theme="light">
<head>
    <title>Healthcheck Dashboard</title>
    <link rel="stylesheet" href="/static/bulma.min.css">
    <link rel="stylesheet" href="/static/bulma_switch.min.css">
    <meta http-equiv="refresh" content="30">
</head>

<body>

<!-- NAVBAR -->
<nav class="navbar is-dark" role="navigation">
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
      <strong>Health Dashboard</strong>
    </a>
  </div>

  <div class="navbar-end">
      <div class="navbar-item">
        <span id="theme-icon" style="cursor:pointer; font-size:20px;" onclick="toggleDarkMode()">🌙</span>
    </div>
  </div>
</nav>

<section class="section">
    <div class="container">

        <h1 class="title">Remote Hosts</h1>
        <p class="subtitle">Auto-refreshing every 30 seconds</p>

        <div class="columns">

            <div class="column is-3">
                <h2 class="subtitle"> {{ error_count }} hosts in error </h2>
            </div>

            <div class="column is-3">
                <div class="field">
                    <label class="switch is-rounded">
                        <input id="error-filter" type="checkbox" onclick="filterHosts()">
                        <span class="check"></span>
                        <span class="control-label">Show only errors</span>
                    </label>
                </div>
            </div>
            <div class="column is-3">
                <div class="field">
                    <input id="host-search" class="input is-small" type="text" placeholder="Search host…" oninput="filterHosts()">
                </div>
            </div>

            <div class="column is-3">
                <button class="button is-small is-info" onclick="toggleView()">Toggle Table View</button>
            </div>
        </div>
  
        <div id="tile-view" class="columns is-multiline">

           {% for host, data in results.items() %}
            <div class="column is-2 host-tile"
                        data-host="{{ host }}"
                        data-error="{{ 'true' if data.errors else 'false' }}">
                <a href="/host/{{ host }}">
                    <div class="box has-text-centered {% if data.errors %}has-background-danger{% else %}has-background-success{% endif %}">
                        <h2 class="title is-4">{{ host }}</h2>
                        {% if data.errors %}
                            <span class="tag is-danger is-light is-medium">ERROR</span>
                        {% else %}
                            <span class="tag is-success is-light is-medium">OK</span>
                        {% endif %}
                    </div>
                </a>
            </div>
            {% endfor %}

        </div>

        <!-- TABLE VIEW (CONDENSED) -->
        <table id="table-view" class="table is-striped is-hoverable is-fullwidth" style="display:none;">
            <thead>
                <tr>
                    <th>Host</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for host, data in results.items() %}
                <tr class="host-row"
                    data-host="{{ host }}"
                    data-error="{{ 'true' if data.errors else 'false' }}"
                    onclick="window.location='/host/{{ host }}'">
                    <td>{{ host }}</td>
                    <td>
                        {% if data.errors %}
                            <span class="tag is-danger">ERROR</span>
                        {% else %}
                            <span class="tag is-success">OK</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

    </div>
</section>

<script>

function toggleView() {
    const tile = document.getElementById("tile-view");
    const table = document.getElementById("table-view");

    if (tile.style.display === "none") {
        tile.style.display = "";
        table.style.display = "none";
    } else {
        tile.style.display = "none";
        table.style.display = "";
    }

    filterHosts();  // keep filters applied
}

function filterHosts() {
    const query = document.getElementById("host-search").value.toLowerCase();
    const onlyErrors = document.getElementById("error-filter").checked;
    const tiles = document.querySelectorAll(".host-tile");
    const rows = document.querySelectorAll(".host-row");

    tiles.forEach(tile => {
        const name = tile.getAttribute("data-host").toLowerCase();
        const isError = tile.getAttribute("data-error") === "true";

        let visible = true;

        // Apply search filter
        if (!name.includes(query)) {
            visible = false;
        }

        // Apply error-only filter
        if (onlyErrors && !isError) {
            visible = false;
        }

        tile.style.display = visible ? "" : "none";
    });

    rows.forEach(row => {
        const name = row.getAttribute("data-host").toLowerCase();
        const isError = row.getAttribute("data-error") === "true";

        let visible = true;

        if (!name.includes(query)) visible = false;
        if (onlyErrors && !isError) visible = false;

        row.style.display = visible ? "" : "none";
    });

    
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");

    const icon = document.getElementById("theme-icon");
    if (document.body.classList.contains("dark-mode")) {
        icon.textContent = "☀️";
        localStorage.setItem("theme", "dark");
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        icon.textContent = "🌙";
        localStorage.setItem("theme", "light");
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

window.onload = function() {
    const icon = document.getElementById("theme-icon");
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        icon.textContent = "☀️";
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        icon.textContent = "🌙";
        document.documentElement.setAttribute('data-theme', 'dark');
    }
};
</script>


</body>
</html>

"""


MAIN_TEMPLATE_OK = """
<!DOCTYPE html>
<html>
<head>
    <title>Healthcheck Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <style>
        body.dark-mode {
            background-color: #121212;
            color: #e0e0e0;
        }
        body.dark-mode .box {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        body.dark-mode pre {
            background-color: #2a2a2a;
            color: #e0e0e0;
        }
        body.dark-mode .navbar {
            background-color: #1e1e1e !important;
        }
        body.dark-mode .table {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        body.dark-mode .table thead {
            background-color: #2a2a2a;
        }
    </style>
    <meta http-equiv="refresh" content="5">
</head>

<body class="has-background-light">

<!-- NAVBAR -->
<nav class="navbar is-light" role="navigation">
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
      <strong>Health Dashboard</strong>
    </a>
  </div>

  <div class="navbar-end">
    <div class="navbar-item">
        <input id="host-search" class="input is-small" type="text" placeholder="Search host…" oninput="filterHosts()">
    </div>

    <div class="navbar-item">
        <label class="checkbox">
            <input id="error-filter" type="checkbox" onclick="filterHosts()">
            Show only errors
        </label>
    </div>

    <div class="navbar-item">
        <button class="button is-small is-info" onclick="toggleView()">Toggle Table View</button>
    </div>

    <div class="navbar-item">
        <span id="theme-icon" style="cursor:pointer; font-size:20px;" onclick="toggleDarkMode()">🌙</span>
    </div>
  </div>
</nav>

<section class="section">
    <div class="container">
        <h1 class="title">Remote Hosts</h1>
        <p class="subtitle">Auto-refreshing every 5 seconds</p>

        <!-- TILE VIEW -->
        <div id="tile-view" class="columns is-multiline">
            {% for host, data in results.items() %}
            <div class="column is-one-quarter host-tile"
                 data-host="{{ host }}"
                 data-error="{{ 'true' if data.errors else 'false' }}">
                <a href="/host/{{ host }}">
                    <div class="box has-text-centered {% if data.errors %}has-background-danger-light{% else %}has-background-success-light{% endif %}">
                        <h2 class="title is-4">{{ host }}</h2>
                        {% if data.errors %}
                            <span class="tag is-danger is-medium">ERROR</span>
                        {% else %}
                            <span class="tag is-success is-medium">OK</span>
                        {% endif %}
                    </div>
                </a>
            </div>
            {% endfor %}
        </div>

        <!-- TABLE VIEW (CONDENSED) -->
        <table id="table-view" class="table is-striped is-hoverable is-fullwidth" style="display:none;">
            <thead>
                <tr>
                    <th>Host</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for host, data in results.items() %}
                <tr class="host-row"
                    data-host="{{ host }}"
                    data-error="{{ 'true' if data.errors else 'false' }}"
                    onclick="window.location='/host/{{ host }}'">
                    <td>{{ host }}</td>
                    <td>
                        {% if data.errors %}
                            <span class="tag is-danger">ERROR</span>
                        {% else %}
                            <span class="tag is-success">OK</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

    </div>
</section>

<script>
function filterHosts() {
    const searchInput = document.getElementById("host-search");
    const errorFilter = document.getElementById("error-filter");

    const query = searchInput ? searchInput.value.toLowerCase() : "";
    const onlyErrors = errorFilter ? errorFilter.checked : false;

    const tiles = document.querySelectorAll(".host-tile");
    const rows = document.querySelectorAll(".host-row");

    tiles.forEach(tile => {
        const name = tile.getAttribute("data-host").toLowerCase();
        const isError = tile.getAttribute("data-error") === "true";

        let visible = true;

        if (!name.includes(query)) visible = false;
        if (onlyErrors && !isError) visible = false;

        tile.style.display = visible ? "" : "none";
    });

    rows.forEach(row => {
        const name = row.getAttribute("data-host").toLowerCase();
        const isError = row.getAttribute("data-error") === "true";

        let visible = true;

        if (!name.includes(query)) visible = false;
        if (onlyErrors && !isError) visible = false;

        row.style.display = visible ? "" : "none";
    });
}

function toggleView() {
    const tile = document.getElementById("tile-view");
    const table = document.getElementById("table-view");

    if (tile.style.display === "none") {
        tile.style.display = "";
        table.style.display = "none";
    } else {
        tile.style.display = "none";
        table.style.display = "";
    }

    // Re-apply filters to the currently visible view
    filterHosts();
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");

    const icon = document.getElementById("theme-icon");
    if (document.body.classList.contains("dark-mode")) {
        icon.textContent = "☀️";
        localStorage.setItem("theme", "dark");
    } else {
        icon.textContent = "🌙";
        localStorage.setItem("theme", "light");
    }
}

window.onload = function() {
    const icon = document.getElementById("theme-icon");
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        icon.textContent = "☀️";
    } else {
        icon.textContent = "🌙";
    }

    // Apply initial filters (in case fields get prefilled by browser)
    filterHosts();
};
</script>

</body>
</html>

"""

HOST_TEMPLATE = """
<!DOCTYPE html>
<html data-theme="light">
<head>
    <title>{{ host }} — Healthchecks</title>
    <link rel="stylesheet" href="/static/bulma.min.css">
    <link rel="stylesheet" href="/static/bulma_switch.min.css">
    <!-- <meta http-equiv="refresh" content="5"> -->
</head>

<body">

<!-- NAVBAR -->
<nav class="navbar is-dark" role="navigation">
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
      <strong>Health Dashboard</strong>
    </a>
  </div>

  <div class="navbar-end">
    <div class="navbar-item">
        <span id="theme-icon" style="cursor:pointer; font-size:20px;" onclick="toggleDarkMode()">🌙</span>
    </div>
  </div>
</nav>

<section class="section">
    <div class="container">

        <h1 class="title">Host: {{ host }}</h1>

        {% if data.errors %}
            <span class="tag is-danger is-medium">ERROR</span>
        {% else %}
            <span class="tag is-success is-medium">OK</span>
        {% endif %}

        <div style="margin-top: 30px;">
            {% for hc in data.healthchecks %}
            <div class="box {% if hc.error %}has-background-danger{% else %}has-background-success{% endif %}">
                <h2 class="title is-5">{{ hc.name }}</h2>

                <p><strong>Status:</strong>
                    {% if hc.error %}
                        <span class="tag is-danger is-light">ERROR</span>
                    {% else %}
                        <span class="tag is-success is-light">OK</span>
                    {% endif %}
                </p>

                <p><strong>stdout:</strong></p>
                <pre class="has-background-white-ter" style="padding: 10px; color: #303030">{{ hc.stdout }}</pre>

                <p><strong>stderr:</strong></p>
                <pre class="has-background-white-ter" style="padding: 10px; color: #303030">{{ hc.stderr }}</pre>
            </div>
            {% endfor %}
        </div>

    </div>
</section>

<script>
function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");

    const icon = document.getElementById("theme-icon");
    if (document.body.classList.contains("dark-mode")) {
        icon.textContent = "☀️";
        localStorage.setItem("theme", "dark");
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        icon.textContent = "🌙";
        localStorage.setItem("theme", "light");
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

window.onload = function() {
    const icon = document.getElementById("theme-icon");
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        icon.textContent = "☀️";
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        icon.textContent = "🌙";
        document.documentElement.setAttribute('data-theme', 'dark');
    }
};
</script>

</body>
</html>

"""

# -----------------------------
# Helpers
# -----------------------------

def load_results():
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def index():
    results = load_results()
    error_count = sum(1 for host, data in results.items() if data.get("errors"))
    return render_template_string(MAIN_TEMPLATE, results=results, error_count=error_count) 

@app.route("/host/<host>")
def host_page(host):
    results = load_results()
    if host not in results:
        abort(404)
    return render_template_string(HOST_TEMPLATE, host=host, data=results[host])

# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
