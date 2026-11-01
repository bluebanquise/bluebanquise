import os
import shlex
import socket
import subprocess

# Each action function (power, boot) returns a (return_code, detail) tuple:
# return_code is 0 on success and 1 on failure, detail is a short text shown in the final
# status table (for example the power state).


def build_ipmi_command(node_configuration, command, parameters, verbose=False):
    """
    Build the ipmitool argument list and its environment. The password is passed through the
    IPMI_PASSWORD environment variable (ipmitool -E), never as a command line argument: command
    lines are readable by any user (ps, /proc), and no shell is involved, so special characters
    in credentials cannot break or inject into the command.
    Also returns the exact command as a copy-pastable string, password included (shown only in
    debug mode), and the same string with the password masked.
    """
    cmd = ['timeout', str(parameters.get('timeout', 10)), 'ipmitool', '-I', 'lanplus']
    if verbose:
        cmd.append('-v')
    cmd += ['-H', node_configuration['bmc']['address'], '-U', str(node_configuration['user']), '-E']
    cmd += command.split()
    env = dict(os.environ)
    env['IPMI_PASSWORD'] = str(node_configuration['password'])
    plain = 'IPMI_PASSWORD=' + shlex.quote(env['IPMI_PASSWORD']) + ' ' + shlex.join(cmd)
    masked = 'IPMI_PASSWORD=**** ' + shlex.join(cmd)
    return cmd, env, plain, masked


def execute_ipmi_command(node, node_configuration, command, logger, parameters):
    cmd, env, plain, masked = build_ipmi_command(node_configuration, command, parameters)
    logger.debug(f'[{node}] Command: {plain}')

    if parameters.get('dryrun', False):
        logger.info(f'[{node}] Dryrun. Cmd: {masked}')
        return 0, ""

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        # exit code 124 is set by the timeout command, when the BMC did not answer in time
        logger.error(f'[{node}] ipmitool failed, exit code {result.returncode}. '
                     f'stdout: {result.stdout.strip()} stderr: {result.stderr.strip()}')
        return 1, ""
    return 0, result.stdout.strip()


def debug_bmc(node, node_configuration, parameters):
    """
    Best-effort diagnostic report, run automatically whenever a power/boot
    action fails. Returns the report as a list of lines, so that it can be
    printed in one block, not mixed with other nodes output.
    IPMI-over-LAN gives far less structured feedback than Redfish (no HTTP
    status codes, just ipmitool exit codes and free-text stderr), so this
    leans more heavily on pattern-matching ipmitool's verbose output to point
    at the likely cause:

      1. BMC address (bmc.ip4, or bmc.name DNS resolution)
      2. ICMP reachability (informational only, often blocked/inconclusive)
      3. Best-effort UDP/623 reachability probe (RMCP presence ping)
      4. A verbose, read-only ipmitool handshake ("chassis status"),
         with stderr pattern-matched for common failure classes

    Each step is independent and wrapped so one failing step doesn't stop
    later steps from running, except when a step makes the rest of the
    report meaningless (DNS failure).
    """
    report = []
    if parameters.get('dryrun', False):
        return report

    bmc_config = node_configuration.get('bmc', {})
    bmc_name = bmc_config.get('name')
    bmc_address = bmc_config.get('address')
    user = node_configuration.get('user')

    report.append(f'----- BMC debug report for {node} ({bmc_name}) -----')

    if not bmc_address:
        report.append('No bmc.ip4 nor bmc.name configured, cannot debug further.')
        report.append('----- End of BMC debug report -----')
        return report

    # 1. Address: bmc.ip4 is used when set, else bmc.name, which then needs DNS resolution
    ip = None
    try:
        ip = socket.gethostbyname(bmc_address)
        if bmc_address == bmc_name:
            report.append(f'DNS: "{bmc_name}" resolves to {ip}.')
        else:
            report.append(f'Address: using bmc.ip4 {ip}, no DNS resolution needed.')
    except socket.gaierror as e:
        report.append(f'DNS: could not resolve "{bmc_address}": {e}. '
                      f'Setting bmc.ip4 in the inventory avoids depending on name resolution.')
        report.append('----- End of BMC debug report -----')
        return report

    # 2. ICMP reachability (informational: absence of ping reply is common
    # and does not necessarily mean the BMC/IPMI service is down)
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            report.append(f'Ping: {ip} responds to ICMP.')
        else:
            report.append(f'Ping: {ip} did not reply to ICMP '
                          f'(inconclusive on its own, ICMP is often blocked while IPMI/UDP still works).')
    except Exception as e:
        report.append(f'Ping: could not run ping command: {e}.')

    # 3. Best-effort UDP/623 reachability probe using a minimal RMCP/ASF
    # presence ping packet. UDP is connectionless, so a timeout here is
    # inconclusive on its own (some BMCs simply ignore malformed/unexpected
    # packets), but a "connection refused" (ICMP port unreachable) is a
    # strong signal the IPMI LAN service is not listening at all, and a
    # clean response is a strong signal that it is.
    try:
        asf_presence_ping = bytes([
            0x06, 0x00, 0xff, 0x06,  # RMCP header (version, reserved, seq, class=ASF)
            0x00, 0x00, 0x11, 0xbe,  # ASF IANA enterprise number (ASF_RMCP_IANA)
            0x80,                    # ASF message type: Presence Ping
            0x00, 0x00, 0x00,        # message tag, reserved, data length
        ])
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        try:
            sock.sendto(asf_presence_ping, (ip, 623))
            try:
                sock.recvfrom(1024)
                report.append(f'UDP/623: {ip}:623 replied to an RMCP presence ping, '
                              f'IPMI LAN service looks reachable.')
            except socket.timeout:
                report.append(f'UDP/623: no reply within 2s from {ip}:623. Inconclusive on its own, '
                              f'but combined with an ipmitool timeout below, points to a network/firewall '
                              f'issue on UDP 623 rather than bad credentials.')
        except OSError as e:
            report.append(f'UDP/623: {ip}:623 unreachable ({e}). IPMI LAN service may not be '
                          f'listening, or a firewall is rejecting the traffic.')
        finally:
            sock.close()
    except Exception as e:
        report.append(f'UDP/623: could not run reachability probe: {e}.')

    # 4. Verbose, read-only ipmitool handshake to surface the actual failure
    # reason. "chassis status" is safe (no side effects) and exercises the
    # full session setup (channel auth capabilities, session challenge,
    # RAKP/activation), the same path power/boot actions rely on.
    cmd, env, plain, masked = build_ipmi_command(node_configuration, 'chassis status', parameters, verbose=True)
    if parameters.get('debug', False):
        report.append(f'Command: {plain}')
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, errors='replace', env=env)
        exit_code = result.returncode
        stdout_text = result.stdout
        stderr_text = result.stderr
        combined = (stdout_text + stderr_text).lower()

        if exit_code == 0:
            report.append(f'IPMI handshake: succeeded, credentials for user "{user}" are valid '
                          f'and the BMC answered "chassis status".')
            first_lines = "\n".join(stdout_text.splitlines()[:6])
            if first_lines:
                report.append(f'chassis status output (truncated):\n{first_lines}')
        else:
            report.append(f'IPMI handshake: "chassis status" failed, exit code {exit_code}.')

            if 'unable to get channel authentication capabilities' in combined:
                report.append('Likely cause: the BMC did not answer the very first IPMI packet. '
                              'Check the hostname/IP and that IPMI-over-LAN is enabled on the BMC - this '
                              'is a connectivity issue, not a credentials problem.')
            if 'unable to establish' in combined and 'session' in combined:
                report.append('Likely cause: could not establish an IPMI v2/RMCP+ session. '
                              'Common causes: UDP 623 blocked by a firewall, a cipher suite mismatch '
                              '(try forcing one with "-C 3" or "-C 17"), or IPMI-over-LAN disabled on the BMC.')
            if 'invalid user name' in combined or 'get session challenge' in combined:
                report.append(f'Likely cause: username rejected. Check that user "{user}" exists '
                              f'on the BMC and has IPMI-over-LAN access enabled.')
            if 'rakp' in combined or 'activate session' in combined or 'password' in combined:
                report.append('Likely cause: authentication failed - wrong password, insufficient '
                              'privilege level configured for this account, or an unsupported cipher suite.')
            if 'insufficient resources' in combined:
                report.append('Likely cause: BMC has no free IPMI sessions left. Some BMCs cap '
                              'concurrent sessions and need a moment (or a BMC reset) to free one up.')

            report.append(f'Raw ipmitool stderr:\n{stderr_text.strip()}')
    except Exception as e:
        report.append(f'IPMI handshake: could not run ipmitool: {e}.')

    report.append('----- End of BMC debug report -----')
    return report


def fail(node, node_configuration, parameters, logger, message):
    """
    Log an error, run the BMC debug report and print it in one block, then return the standard
    failure result. Centralised here so every failure path in power() and boot() automatically
    triggers debug_bmc().
    """
    logger.error(f'[{node}] Error, {message}.')
    report = debug_bmc(node, node_configuration, parameters)
    if report:
        # A single log call is printed in one piece, even when several nodes run in parallel
        logger.error(f'[{node}] BMC debug report:\n' + '\n'.join(report))
    return 1, message


def power(node, node_configuration, parameter, parameters, logger):
    if parameter == "on":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power on", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Powered on.')
            return 0, 'powered on'
        else:
            return fail(node, node_configuration, parameters, logger, 'could not power on node')

    elif parameter == "off":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power off", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Powered off.')
            return 0, 'powered off'
        else:
            return fail(node, node_configuration, parameters, logger, 'could not power off node')

    elif parameter == "reset":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power reset", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Reset.')
            return 0, 'reset'
        else:
            return fail(node, node_configuration, parameters, logger, 'could not reset node')

    elif parameter == "status":
        exit_code, stdout = execute_ipmi_command(node, node_configuration, "chassis power status", logger, parameters)
        if exit_code == 0:
            # ipmitool prints "Chassis Power is on" / "Chassis Power is off"
            power_state = stdout.replace('Chassis Power is', '').strip() or 'unknown (dryrun)'
            logger.info(f'[{node}] Power status: {power_state}')
            return 0, power_state
        else:
            return fail(node, node_configuration, parameters, logger, 'could not get node power status')

    else:
        logger.error(f'[{node}] Error, unknown power action {parameter}')
        return 1, f'unknown power action {parameter}'


def boot(node, node_configuration, parameter, parameters, logger):
    if parameter == "disk":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev disk", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Next boot set to disk.')
            return 0, 'next boot: disk'
        else:
            return fail(node, node_configuration, parameters, logger, 'could not set next boot to disk')

    elif parameter == "bios":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev bios", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Next boot set to BIOS.')
            return 0, 'next boot: bios'
        else:
            return fail(node, node_configuration, parameters, logger, 'could not set next boot to BIOS')

    elif parameter == "pxe":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev pxe", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Next boot set to PXE.')
            return 0, 'next boot: pxe'
        else:
            return fail(node, node_configuration, parameters, logger, 'could not set next boot to PXE')

    else:
        logger.error(f'[{node}] Error, unknown boot action {parameter}')
        return 1, f'unknown boot action {parameter}'
