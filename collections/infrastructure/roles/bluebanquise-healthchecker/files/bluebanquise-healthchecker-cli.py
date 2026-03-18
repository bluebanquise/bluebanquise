#!/usr/bin/env python3
import sys
import yaml
import os

RESULTS_FILE = "/var/lib/bluebanquise/bluebanquise-healtchecker/results.yaml"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_results():
    if not os.path.exists(RESULTS_FILE):
        print(f"Results file not found: {RESULTS_FILE}")
        sys.exit(1)

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def print_all_hosts(results, only_errors=False):
    for host, data in results.items():
        is_error = data.get("errors", False)

        if only_errors and not is_error:
            continue

        status = f"{GREEN}OK{RESET}" if not is_error else f"{RED}ERROR{RESET}"
        print(f"{host}: {status}")


def print_host_details(host, data):
    header_status = f"{GREEN}OK{RESET}" if not data.get("errors") else f"{RED}ERROR{RESET}"
    print(f"{BOLD}{host}{RESET} — {header_status}")
    print("-" * 60)

    for hc in data.get("healthchecks", []):
        name = hc.get("name", "Unnamed check")
        error = hc.get("error", True)

        status = f"{GREEN}OK{RESET}" if not error else f"{RED}ERROR{RESET}"

        print(f"{BOLD}{name}{RESET} — {status}")

        stdout = hc.get("stdout", "").strip()
        stderr = hc.get("stderr", "").strip()

        if stdout:
            print(f"  {BOLD}stdout:{RESET}")
            for line in stdout.splitlines():
                print(f"    {line}")

        if stderr:
            print(f"  {BOLD}stderr:{RESET}")
            for line in stderr.splitlines():
                print(f"    {line}")

        print("-" * 60)


def main():
    results = load_results()

    # Parse arguments
    args = sys.argv[1:]
    only_errors = False

    # Detect --in-error flag
    if "--in-error" in args or "-e" in args:
        only_errors = True
        args = [a for a in args if a not in ("--in-error", "-e")]

    # No argument → list hosts
    if len(args) == 0:
        print_all_hosts(results, only_errors=only_errors)
        return

    # One argument → show host details
    host = args[0]
    if host not in results:
        print(f"Host '{host}' not found in results.")
        sys.exit(1)

    print_host_details(host, results[host])


if __name__ == "__main__":
    main()
