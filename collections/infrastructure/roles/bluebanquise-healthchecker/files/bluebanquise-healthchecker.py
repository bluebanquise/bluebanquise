#!/usr/bin/env python3
import os
import sys
import time
import signal
import smtplib
from email.mime_text import MIMEText

import yaml
import paramiko
from dask.distributed import Client, as_completed

import subprocess

CONFIG_PATH = "/etc/bluebanquise/bluebanquise-healtchecker/configuration.yaml"


# -----------------------------
# YAML helpers
# -----------------------------

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml(data: dict, path: str) -> None:
    tmp_path = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    os.replace(tmp_path, path)


# -----------------------------
# GROUPS helpers
# -----------------------------

def merge_groups_into_hosts(hosts_config: dict, groups_config: dict) -> dict:
    """
    Merge group-based healthchecks into the hosts configuration.

    Rules:
    - If a host already exists, append group healthchecks.
    - If a host does not exist, create it with only the group healthchecks.
    - Hosts may belong to multiple groups.
    """
    merged = {host: cfg.copy() for host, cfg in hosts_config.items()}

    for group_name, group in groups_config.items():
        group_hosts = group.get("hosts", [])
        group_checks = group.get("healthchecks", [])
        group_triggers = group.get("on_error_triggers", [])

        for host in group_hosts:
            if host not in merged:
                merged[host] = {"healthchecks": [], "on_error_triggers": []}

            # Ensure lists exist
            merged[host].setdefault("healthchecks", [])
            merged[host].setdefault("on_error_triggers", [])

            # Append group healthchecks
            merged[host]["healthchecks"].extend(group_checks)

            # Append group triggers
            merged[host]["on_error_triggers"].extend(group_triggers)

    return merged


# -----------------------------
# SSH helpers
# -----------------------------

def create_ssh_client(
    hostname: str,
    username: str,
    port: int = 22,
    password: str = None,
    key_filename: str = None,
    timeout: int = 10,
) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        key_filename=os.path.expanduser(key_filename) if key_filename else None,
        timeout=timeout,
    )
    return client


def run_healthchecks_on_host(
    hostname: str,
    host_config: dict,
    username: str,
    port: int,
    password: str,
    key_filename: str,
    ssh_timeout: int,
) -> dict:
    """
    Executed on a Dask worker.
    Opens a single SSH connection, runs all healthchecks with per-command timeouts,
    and closes it.
    """
    result: dict[str, object] = {
        "errors": False,
        "healthchecks": [],
    }

    healthchecks: list[dict] = host_config.get("healthchecks", [])

    if not healthchecks:
        return result

    client = None
    try:
        client = create_ssh_client(
            hostname=hostname,
            username=username,
            port=port,
            password=password,
            key_filename=key_filename,
            timeout=ssh_timeout,
        )

        for hc in healthchecks:
            name = hc.get("name", "")
            command = hc.get("command", "")
            ok_exitcode = hc.get("ok_exitcode", 0)
            cmd_timeout = hc.get("timeout", 10)  # seconds

            hc_result: dict[str, object] = {
                "name": name,
                "stdout": "",
                "stderr": "",
                "error": True,  # assume error until proven otherwise
            }

            if not command:
                hc_result["stderr"] = "No command provided"
                result["healthchecks"].append(hc_result)
                result["errors"] = True
                continue

            try:
                stdin, stdout, stderr = client.exec_command(command)
                channel = stdout.channel
                start_time = time.time()

                # Wait for command to finish or timeout
                while not channel.exit_status_ready():
                    if time.time() - start_time > cmd_timeout:
                        channel.close()  # kills remote command
                        hc_result["stderr"] = (
                            f"Command timed out after {cmd_timeout} seconds"
                        )
                        hc_result["error"] = True
                        result["errors"] = True
                        result["healthchecks"].append(hc_result)
                        break
                    time.sleep(0.1)

                else:
                    # Command finished normally
                    out_str = stdout.read().decode("utf-8", errors="replace")
                    err_str = stderr.read().decode("utf-8", errors="replace")
                    exit_status = channel.recv_exit_status()

                    hc_result["stdout"] = out_str.strip()
                    hc_result["stderr"] = err_str.strip()
                    hc_result["error"] = exit_status != ok_exitcode

                    if hc_result["error"]:
                        result["errors"] = True

                    result["healthchecks"].append(hc_result)

            except Exception as e:
                hc_result["stderr"] = f"Exception while running command: {e}"
                hc_result["error"] = True
                result["errors"] = True
                result["healthchecks"].append(hc_result)

    except Exception as e:
        # SSH connection failed: mark all healthchecks as failed
        result["errors"] = True
        result["healthchecks"] = []
        for hc in host_config.get("healthchecks", []):
            result["healthchecks"].append(
                {
                    "name": hc.get("name", ""),
                    "stdout": "",
                    "stderr": f"SSH connection failed: {e}",
                    "error": True,
                }
            )
    finally:
        if client is not None:
            client.close()

    return result


# -----------------------------
# Email alerting
# -----------------------------

def send_alert_email(subject: str, body: str, config: dict) -> None:
    email_cfg = config.get("email", {})
    if not email_cfg.get("enabled", False):
        return

    required_keys = ["smtp_server", "smtp_port", "username", "password", "from", "to"]
    for key in required_keys:
        if key not in email_cfg:
            # Missing required email config; silently skip
            return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_cfg["from"]
    msg["To"] = ", ".join(email_cfg["to"])

    server = smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"])

    if email_cfg.get("use_tls", False):
        server.starttls()

    server.login(email_cfg["username"], email_cfg["password"])
    server.sendmail(email_cfg["from"], email_cfg["to"], msg.as_string())
    server.quit()


# -----------------------------
# Errors trigger
# -----------------------------


def run_error_triggers(host: str, triggers: list):
    for trig in triggers:
        name = trig.get("name", "Unnamed trigger")
        cmd = trig.get("command", "").replace("%%host%%", host)

        if not cmd:
            print(f"[TRIGGER] Skipping empty trigger for {host}")
            continue

        print(f"[TRIGGER] Executing '{name}' for {host}: {cmd}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"[TRIGGER] stdout: {result.stdout.strip()}")
            print(f"[TRIGGER] stderr: {result.stderr.strip()}")
        except Exception as e:
            print(f"[TRIGGER] ERROR running trigger '{name}' for {host}: {e}")


# -----------------------------
# Config
# -----------------------------

def load_global_config() -> dict:
    try:
        return load_yaml(CONFIG_PATH)
    except Exception as e:
        print(f"Failed to read configuration file {CONFIG_PATH}: {e}", file=sys.stderr)
        sys.exit(1)


# -----------------------------
# Main loop
# -----------------------------

def main():
    config = load_global_config()

    interval = config.get("interval", 60)

    ssh_cfg = config.get("ssh", {})
    ssh_user = ssh_cfg.get("user")
    ssh_port = ssh_cfg.get("port", 22)
    ssh_key = ssh_cfg.get("key")
    ssh_password = ssh_cfg.get("password")  # optional, if not using key
    ssh_timeout = ssh_cfg.get("timeout", 10)

    if not ssh_user:
        print("SSH user must be defined in configuration under 'ssh.user'", file=sys.stderr)
        sys.exit(1)

    hosts_file = config.get("hosts_file")
    results_file = config.get("results_file")

    if not hosts_file:
        print("hosts_file must be defined in configuration", file=sys.stderr)
        sys.exit(1)
    if not results_file:
        print("results_file must be defined in configuration", file=sys.stderr)
        sys.exit(1)

    # Load hosts configuration
    try:
        hosts_config = load_yaml(hosts_file)
    except Exception as e:
        print(f"Failed to read hosts file {hosts_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Load groups configuration (optional)
    groups_file = config.get("groups_file")
    if groups_file:
        try:
            groups_config = load_yaml(groups_file)
        except Exception as e:
            print(f"Failed to read groups file {groups_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        groups_config = {}

    # Merge groups into hosts
    hosts_config = merge_groups_into_hosts(hosts_config, groups_config)

    if not isinstance(hosts_config, dict) or not hosts_config:
        print("Hosts file does not define any hosts", file=sys.stderr)
        sys.exit(1)

    # Setup Dask client
    dask_cfg = config.get("dask", {})
    dask_address = dask_cfg.get("address")
    if dask_address:
        client = Client(address=dask_address)
    else:
        client = Client(processes=True)

    print("Dask client:", client)

    # Handle clean shutdown with Ctrl+C
    stop = {"flag": False}

    def handle_sigint(signum, frame):
        print("Received interrupt, stopping after current iteration...")
        stop["flag"] = True

    signal.signal(signal.SIGINT, handle_sigint)

    previous_results: dict[str, dict] = {}

    print("Starting healthcheck loop. Press Ctrl+C to stop.")
    while not stop["flag"]:
        loop_start = time.time()
        futures = {}

        # Submit a task per host
        for hostname, host_cfg in hosts_config.items():
            futures[hostname] = client.submit(
                run_healthchecks_on_host,
                hostname,
                host_cfg,
                ssh_user,
                ssh_port,
                ssh_password,
                ssh_key,
                ssh_timeout,
            )

        results: dict[str, dict] = {}
        for future in as_completed(list(futures.values())):
            host_for_future = None
            for host, fut in futures.items():
                if fut == future:
                    host_for_future = host
                    break

            try:
                res = future.result()
            except Exception as e:
                res = {
                    "errors": True,
                    "healthchecks": [
                        {
                            "name": "Dask execution",
                            "stdout": "",
                            "stderr": f"Dask task failed: {e}",
                            "error": True,
                        }
                    ],
                }

            if host_for_future is not None:
                results[host_for_future] = res

        # Write results
        try:
            dump_yaml(results, results_file)
            print(f"Wrote results to {results_file}")
        except Exception as e:
            print(f"Failed to write results: {e}", file=sys.stderr)

        # Check for state transitions and send alerts
        email_cfg = config.get("email", {})
        send_recovery = email_cfg.get("send_recovery", False)

        for host, data in results.items():
            prev_errors = previous_results.get(host, {}).get("errors", False)
            now_errors = data.get("errors", False)

            # OK -> ERROR
            if now_errors and not prev_errors:
                subject = f"[ALERT] Host {host} is in ERROR"
                body_lines = [f"The host {host} has entered an error state.", "", "Details:"]
                for hc in data.get("healthchecks", []):
                    status = "ERROR" if hc.get("error") else "OK"
                    body_lines.append(f"- {hc.get('name')} : {status}")
                    if hc.get("error"):
                        body_lines.append(f"  stderr: {hc.get('stderr')}")
                body = "\n".join(body_lines)
                send_alert_email(subject, body, config)

            # ERROR -> OK (optional recovery email)
            if send_recovery and prev_errors and not now_errors:
                subject = f"[RECOVERY] Host {host} is back to OK"
                body = f"The host {host} has recovered and is now OK."
                send_alert_email(subject, body, config)

            # ERROR transition: run triggers
            if now_errors and not prev_errors:
                triggers = hosts_config.get(host, {}).get("on_error_triggers", [])
                if triggers:
                    run_error_triggers(host, triggers)

                

        previous_results = results

        # Sleep until next iteration
        elapsed = time.time() - loop_start
        remaining = max(0, interval - elapsed)
        if remaining > 0 and not stop["flag"]:
            time.sleep(remaining)

    print("Healthcheck loop stopped.")


if __name__ == "__main__":
    main()
