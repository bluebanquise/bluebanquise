import socket
import subprocess


def execute_ipmi_command(node, node_configuration, command, logger, parameters):
    timeout = parameters.get('timeout', 10)
    cmd = (
        "timeout " + str(timeout) + " ipmitool -I lanplus "
        + "-H " + node_configuration['bmc']['name']
        + " -U " + node_configuration['user']
        + " -P " + node_configuration['password']
        + " " + command
    )

    if not parameters.get('dryrun', False):
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode

        if exit_code != 0:
            logger.error(f'[{node}] Error executing IPMI command.')
            logger.error(f'[{node}] exit code: {exit_code}')
            logger.error(f'[{node}] stdout: {stdout.decode()}')
            logger.error(f'[{node}] stderr: {stderr.decode()}')
            return 1, ""
        else:
            return 0, stdout.decode()
    else:
        logger.info(f'[{node}] Dryrun. Cmd: {cmd}')
        return 0, ""


def debug_bmc(node, node_configuration, parameters, logger):
    """
    Best-effort diagnostic report, run automatically whenever a power/boot
    action fails. IPMI-over-LAN gives far less structured feedback than
    Redfish (no HTTP status codes, just ipmitool exit codes and free-text
    stderr), so this leans more heavily on pattern-matching ipmitool's
    verbose output to point at the likely cause:

      1. DNS resolution of the BMC hostname
      2. ICMP reachability (informational only, often blocked/inconclusive)
      3. Best-effort UDP/623 reachability probe (RMCP presence ping)
      4. A verbose, read-only ipmitool handshake ("chassis status"),
         with stderr pattern-matched for common failure classes

    Each step is independent and wrapped so one failing step doesn't stop
    later steps from running, except when a step makes the rest of the
    report meaningless (DNS failure).
    """
    if parameters.get('dryrun', False):
        return

    bmc_config = node_configuration.get('bmc', {})
    bmc_name = bmc_config.get('name')
    user = node_configuration.get('user')
    password = node_configuration.get('password')
    timeout = parameters.get('timeout', 10)

    logger.error(f'[{node}] ----- BMC debug report ({bmc_name}) -----')

    if not bmc_name:
        logger.error(f'[{node}] No bmc.name configured, cannot debug further.')
        logger.error(f'[{node}] ----- End of BMC debug report -----')
        return

    # 1. DNS resolution
    ip = None
    try:
        ip = socket.gethostbyname(bmc_name)
        logger.error(f'[{node}] DNS: "{bmc_name}" resolves to {ip}.')
    except socket.gaierror as e:
        logger.error(f'[{node}] DNS: could not resolve "{bmc_name}": {e}.')
        logger.error(f'[{node}] ----- End of BMC debug report -----')
        return

    # 2. ICMP reachability (informational: absence of ping reply is common
    # and does not necessarily mean the BMC/IPMI service is down)
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            logger.error(f'[{node}] Ping: {ip} responds to ICMP.')
        else:
            logger.error(f'[{node}] Ping: {ip} did not reply to ICMP '
                         f'(inconclusive on its own, ICMP is often blocked while IPMI/UDP still works).')
    except Exception as e:
        logger.error(f'[{node}] Ping: could not run ping command: {e}.')

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
                logger.error(f'[{node}] UDP/623: {ip}:623 replied to an RMCP presence ping, '
                             f'IPMI LAN service looks reachable.')
            except socket.timeout:
                logger.error(f'[{node}] UDP/623: no reply within 2s from {ip}:623. Inconclusive on its own, '
                             f'but combined with an ipmitool timeout below, points to a network/firewall '
                             f'issue on UDP 623 rather than bad credentials.')
        except (ConnectionRefusedError, OSError) as e:
            logger.error(f'[{node}] UDP/623: {ip}:623 unreachable ({e}). IPMI LAN service may not be '
                         f'listening, or a firewall is rejecting the traffic.')
        finally:
            sock.close()
    except Exception as e:
        logger.error(f'[{node}] UDP/623: could not run reachability probe: {e}.')

    # 4. Verbose, read-only ipmitool handshake to surface the actual failure
    # reason. "chassis status" is safe (no side effects) and exercises the
    # full session setup (channel auth capabilities, session challenge,
    # RAKP/activation), the same path power/boot actions rely on.
    cmd = (
        "timeout " + str(timeout) + " ipmitool -I lanplus -v "
        + "-H " + bmc_name
        + " -U " + user
        + " -P " + password
        + " chassis status"
    )
    try:
        cmd_call = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmd_call.communicate()
        exit_code = cmd_call.returncode
        stdout_text = stdout.decode(errors='replace')
        stderr_text = stderr.decode(errors='replace')
        combined = (stdout_text + stderr_text).lower()

        if exit_code == 0:
            logger.error(f'[{node}] IPMI handshake: succeeded, credentials for user "{user}" are valid '
                         f'and the BMC answered "chassis status".')
            first_lines = "\n".join(stdout_text.splitlines()[:6])
            if first_lines:
                logger.error(f'[{node}] chassis status output (truncated):\n{first_lines}')
        else:
            logger.error(f'[{node}] IPMI handshake: "chassis status" failed, exit code {exit_code}.')

            if 'unable to get channel authentication capabilities' in combined:
                logger.error(f'[{node}] Likely cause: the BMC did not answer the very first IPMI packet. '
                             f'Check the hostname/IP and that IPMI-over-LAN is enabled on the BMC - this '
                             f'is a connectivity issue, not a credentials problem.')
            if 'unable to establish' in combined and 'session' in combined:
                logger.error(f'[{node}] Likely cause: could not establish an IPMI v2/RMCP+ session. '
                             f'Common causes: UDP 623 blocked by a firewall, a cipher suite mismatch '
                             f'(try forcing one with "-C 3" or "-C 17"), or IPMI-over-LAN disabled on the BMC.')
            if 'invalid user name' in combined or 'get session challenge' in combined:
                logger.error(f'[{node}] Likely cause: username rejected. Check that user "{user}" exists '
                             f'on the BMC and has IPMI-over-LAN access enabled.')
            if 'rakp' in combined or 'activate session' in combined or 'password' in combined:
                logger.error(f'[{node}] Likely cause: authentication failed - wrong password, insufficient '
                             f'privilege level configured for this account, or an unsupported cipher suite.')
            if 'insufficient resources' in combined:
                logger.error(f'[{node}] Likely cause: BMC has no free IPMI sessions left. Some BMCs cap '
                             f'concurrent sessions and need a moment (or a BMC reset) to free one up.')

            logger.error(f'[{node}] Raw ipmitool stderr:\n{stderr_text.strip()}')
    except Exception as e:
        logger.error(f'[{node}] IPMI handshake: could not run ipmitool: {e}.')

    logger.error(f'[{node}] ----- End of BMC debug report -----')


def fail(node, node_configuration, parameters, logger, message):
    """
    Log an error, run the BMC debug report, and return the standard
    failure code (1). Centralised here so every failure path in power()
    and boot() automatically triggers debug_bmc().
    """
    logger.error(f'[{node}] {message}')
    debug_bmc(node, node_configuration, parameters, logger)
    return 1


def power(node, node_configuration, action_parameters, parameters, logger):
    if action_parameters[0] == "on":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power on", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Powered on.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not power on node.')

    elif action_parameters[0] == "off":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power off", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Powered off.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not power off node.')

    elif action_parameters[0] == "reset":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis power reset", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Reset.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not reset node.')

    elif action_parameters[0] == "status":
        exit_code, stdout = execute_ipmi_command(node, node_configuration, "chassis power status", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Power status: {stdout}')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not get node power status.')

    else:
        logger.error(f'[{node}] Error, unknown power action {action_parameters[0]}')
        return 1


def boot(node, node_configuration, action_parameters, parameters, logger):
    if action_parameters[0] == "disk":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev disk", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Next boot set to disk.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not set next boot to disk.')

    elif action_parameters[0] == "bios":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev bios", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Next boot set to BIOS.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not set next boot to BIOS.')

    elif action_parameters[0] == "pxe":
        exit_code, _ = execute_ipmi_command(node, node_configuration, "chassis bootdev pxe", logger, parameters)
        if exit_code == 0:
            logger.info(f'[{node}] Next boot set to PXE.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not set next boot to PXE.')

    else:
        logger.error(f'[{node}] Error, unknown boot action {action_parameters[0]}')
        return 1