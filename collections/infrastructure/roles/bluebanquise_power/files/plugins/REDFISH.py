import socket
import subprocess

import requests
from requests.auth import HTTPBasicAuth

# Disable SSL warnings for simplicity in this example
# In production, handle SSL certificates properly
requests.packages.urllib3.disable_warnings()


def execute_redfish_request(node, node_configuration, endpoint, logger, parameters, method='GET', payload=None, extra_headers=None):
    url = f"https://{node_configuration['bmc']['name']}/redfish/v1/{endpoint}"
    auth = HTTPBasicAuth(node_configuration['user'], node_configuration['password'])
    headers = {'Content-Type': 'application/json'}
    if extra_headers:
        headers.update(extra_headers)

    if not parameters.get('dryrun', False):
        try:
            response = requests.request(method, url, auth=auth, headers=headers, json=payload, verify=False)
            response.raise_for_status()
            if not response.content:
                # Some BMCs return 204 No Content (or a 200 with empty body)
                # on successful PATCH/POST actions - there's nothing to parse.
                return {}, response.status_code
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            logger.error(f'[{node}] Error executing Redfish request: {e}')
            return None, getattr(e.response, 'status_code', None)
        except ValueError as e:
            # response.json() failed despite a 2xx/success status and non-empty
            # content-length header (e.g. whitespace-only body from some BMCs).
            logger.error(f'[{node}] Error, could not decode Redfish JSON response for {url}: {e}')
            return {}, response.status_code
    else:
        logger.info(f'[{node}] Dryrun. url: {url}, payload: {payload}')
        return 0, 200


def is_success(status_code):
    return status_code is not None and 200 <= status_code < 300


def debug_bmc(node, node_configuration, parameters, logger):
    """
    Best-effort diagnostic report, run automatically whenever a power/boot
    action fails. Walks through increasingly specific checks so the log
    tells you *where* things break rather than just that they did:

      1. DNS resolution of the BMC hostname
      2. ICMP reachability (informational only, many BMCs/firewalls block it)
      3. HTTPS / Redfish service root reachability (no auth required)
      4. Credential validity
      5. A few extra fields (firmware, model, health) to help spot the cause

    Each step is independent and wrapped so that one failure doesn't stop
    later steps from being skipped when they could still run (e.g. a ping
    failure shouldn't prevent trying HTTPS, since ICMP is often filtered).
    Steps that make later ones meaningless (DNS failure, SSL/connection
    failure) do stop the report early, since there's nothing more to learn.
    """
    if parameters.get('dryrun', False):
        return

    bmc_config = node_configuration.get('bmc', {})
    bmc_name = bmc_config.get('name')
    user = node_configuration.get('user')
    password = node_configuration.get('password')

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
    # and does not necessarily mean the BMC/HTTPS is down)
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            logger.error(f'[{node}] Ping: {ip} responds to ICMP.')
        else:
            logger.error(f'[{node}] Ping: {ip} did not reply to ICMP '
                         f'(inconclusive on its own, ICMP is often blocked while HTTPS still works).')
    except Exception as e:
        logger.error(f'[{node}] Ping: could not run ping command: {e}.')

    # 3. HTTPS / Redfish service root reachability, no auth required
    root_url = f"https://{bmc_name}/redfish/v1/"
    try:
        response = requests.get(root_url, verify=False, timeout=5)
        logger.error(f'[{node}] Redfish root: {root_url} reachable, HTTP {response.status_code}.')
        try:
            root_data = response.json()
            logger.error(f'[{node}] Redfish version: {root_data.get("RedfishVersion", "unknown")}.')
            product = root_data.get('Product') or root_data.get('Vendor')
            if product:
                logger.error(f'[{node}] Product/Vendor: {product}.')
        except ValueError:
            logger.error(f'[{node}] Redfish root did not return valid JSON.')
    except requests.exceptions.SSLError as e:
        logger.error(f'[{node}] Redfish root: SSL/TLS error reaching {root_url}: {e}.')
        logger.error(f'[{node}] ----- End of BMC debug report -----')
        return
    except requests.exceptions.RequestException as e:
        logger.error(f'[{node}] Redfish root: could not reach {root_url}: {e}.')
        logger.error(f'[{node}] Check network routing/firewall to the BMC on TCP/443, and that the '
                     f'Redfish service is enabled on the BMC.')
        logger.error(f'[{node}] ----- End of BMC debug report -----')
        return

    # 4. Credential validity
    auth = HTTPBasicAuth(user, password)
    credentials_ok = False
    try:
        response = requests.get(f"https://{bmc_name}/redfish/v1/Systems", auth=auth, verify=False, timeout=5)
        if response.status_code == 200:
            logger.error(f'[{node}] Auth: credentials for user "{user}" are valid.')
            credentials_ok = True
        elif response.status_code == 401:
            logger.error(f'[{node}] Auth: credentials for user "{user}" were REJECTED (HTTP 401). '
                         f'Check username/password. Repeated failures can also lock the BMC account '
                         f'out for several minutes on some vendors.')
        else:
            logger.error(f'[{node}] Auth: unexpected HTTP {response.status_code} while checking credentials.')
    except requests.exceptions.RequestException as e:
        logger.error(f'[{node}] Auth: error while checking credentials: {e}.')

    # 5. A few extra fields to help spot the cause, only if credentials work
    if credentials_ok:
        try:
            response = requests.get(f"https://{bmc_name}/redfish/v1/Managers", auth=auth, verify=False, timeout=5)
            if response.status_code == 200:
                for member in response.json().get('Members', []):
                    m_id = member.get('@odata.id')
                    if not m_id:
                        continue
                    m_resp = requests.get(f"https://{bmc_name}{m_id}", auth=auth, verify=False, timeout=5)
                    if m_resp.status_code == 200:
                        m_data = m_resp.json()
                        health = m_data.get('Status', {}).get('Health', 'unknown')
                        logger.error(f'[{node}] Manager "{m_data.get("Name", "?")}": '
                                     f'FirmwareVersion={m_data.get("FirmwareVersion", "unknown")}, '
                                     f'Model={m_data.get("Model", "unknown")}, Health={health}.')
        except requests.exceptions.RequestException as e:
            logger.error(f'[{node}] Managers: could not fetch manager info: {e}.')

        try:
            system_endpoint = node_configuration.get('_redfish_system_endpoint')
            if system_endpoint:
                response = requests.get(f"https://{bmc_name}/redfish/v1/{system_endpoint}",
                                        auth=auth, verify=False, timeout=5)
                if response.status_code == 200:
                    s_data = response.json()
                    logger.error(f'[{node}] System "{system_endpoint}": '
                                 f'PowerState={s_data.get("PowerState", "unknown")}, '
                                 f'Health={s_data.get("Status", {}).get("Health", "unknown")}, '
                                 f'BootSourceOverrideTarget={s_data.get("Boot", {}).get("BootSourceOverrideTarget", "unknown")}.')
        except requests.exceptions.RequestException as e:
            logger.error(f'[{node}] System: could not fetch system info: {e}.')

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


def get_system_endpoint(node, node_configuration, parameters, logger):
    """
    Discover the Systems resource path for this BMC instead of assuming a
    vendor-specific ID (e.g. Dell's 'System.Embedded.1'). Some BMCs use '1',
    others 'Self', others something else entirely.

    Result is cached on node_configuration so discovery only happens once
    per run for a given node.

    An optional bmc.system_id can be set in node_configuration to pin down
    a specific system when a BMC exposes several (e.g. a blade chassis).
    """
    cached = node_configuration.get('_redfish_system_endpoint')
    if cached:
        return cached

    logger.info(f'[{node}] Discovering Redfish system endpoint')
    response, status_code = execute_redfish_request(node, node_configuration, 'Systems', logger, parameters)

    if not is_success(status_code) or not response:
        fail(node, node_configuration, parameters, logger, 'Error, could not discover Systems collection.')
        return None

    # Dryrun never actually calls the BMC, so there's nothing to discover.
    # This is a placeholder value only, real discovery happens on a live run.
    if not isinstance(response, dict):
        logger.info(f'[{node}] Dryrun, using placeholder system endpoint Systems/1.')
        return 'Systems/1'

    members = response.get('Members', [])
    if not members:
        fail(node, node_configuration, parameters, logger, 'Error, Systems collection is empty.')
        return None

    target_id = node_configuration.get('bmc', {}).get('system_id')
    system_odata_id = None

    if target_id:
        for member in members:
            if member.get('@odata.id', '').rstrip('/').endswith(f'/{target_id}'):
                system_odata_id = member['@odata.id']
                break
        if not system_odata_id:
            fail(node, node_configuration, parameters, logger,
                 f'Error, configured system_id "{target_id}" not found in Systems collection.')
            return None
    else:
        if len(members) > 1:
            logger.info(f'[{node}] Multiple systems found in Systems collection, using the first one. '
                        f'Set bmc.system_id in configuration to pick a specific one.')
        system_odata_id = members[0]['@odata.id']

    # system_odata_id looks like /redfish/v1/Systems/Self or /redfish/v1/Systems/System.Embedded.1
    # execute_redfish_request already prefixes /redfish/v1/, so strip that off.
    endpoint = system_odata_id.split('/redfish/v1/', 1)[-1].strip('/')

    node_configuration['_redfish_system_endpoint'] = endpoint
    logger.info(f'[{node}] Discovered Redfish system endpoint: {endpoint}')
    return endpoint


def get_etag(node, node_configuration, endpoint, parameters, logger):
    """
    Some BMCs require an If-Match header (RFC 7232 precondition) on PATCH
    requests, carrying the resource's current @odata.etag, and will reject
    the request with HTTP 428 Precondition Required otherwise. Fetch the
    etag with a plain GET right before the PATCH.
    """
    logger.info(f'[{node}] Fetching current etag for {endpoint}')
    response, status_code = execute_redfish_request(node, node_configuration, endpoint, logger, parameters)
    if not is_success(status_code) or not isinstance(response, dict):
        logger.error(f'[{node}] Error, could not fetch etag for {endpoint}.')
        return None
    return response.get('@odata.etag')


def get_power_state(node, node_configuration, system_endpoint, parameters, logger):
    """
    Fetch the current PowerState of the system. Used to make on/off
    idempotent: some BMCs (e.g. this AMI implementation) reject a
    ResetType with HTTP 400 if the system is already in that requested
    state, instead of treating it as a harmless no-op.
    """
    logger.info(f'[{node}] Checking current power state')
    response, status_code = execute_redfish_request(node, node_configuration, system_endpoint, logger, parameters)
    if not is_success(status_code) or not isinstance(response, dict):
        return None
    return response.get('PowerState')


def power(node, node_configuration, action_parameters, parameters, logger):
    system_endpoint = get_system_endpoint(node, node_configuration, parameters, logger)
    if not system_endpoint:
        return 1

    if action_parameters[0] == "on":
        current_state = get_power_state(node, node_configuration, system_endpoint, parameters, logger)
        if current_state == 'On':
            logger.info(f'[{node}] Already powered on.')
            return 0

        logger.info(f'[{node}] Sending power on request')
        _, status_code = execute_redfish_request(
            node, node_configuration, f'{system_endpoint}/Actions/ComputerSystem.Reset',
            logger, parameters, method='POST', payload={"ResetType": "On"})
        if is_success(status_code):
            logger.info(f'[{node}] Powered on.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not power on node.')

    elif action_parameters[0] == "off":
        current_state = get_power_state(node, node_configuration, system_endpoint, parameters, logger)
        if current_state == 'Off':
            logger.info(f'[{node}] Already powered off.')
            return 0

        logger.info(f'[{node}] Sending power off request')
        _, status_code = execute_redfish_request(
            node, node_configuration, f'{system_endpoint}/Actions/ComputerSystem.Reset',
            logger, parameters, method='POST', payload={"ResetType": "ForceOff"})
        if is_success(status_code):
            logger.info(f'[{node}] Powered off.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not power off node.')

    elif action_parameters[0] == "reset":
        # NOTE: "Reset" is not a valid Redfish ResetType value. Valid values
        # are vendor-dependent but "ForceRestart" is the closest to a hard
        # reset and is widely supported. Adjust if your BMC's
        # ResetActionInfo advertises something else.
        logger.info(f'[{node}] Sending reset request')
        _, status_code = execute_redfish_request(
            node, node_configuration, f'{system_endpoint}/Actions/ComputerSystem.Reset',
            logger, parameters, method='POST', payload={"ResetType": "ForceRestart"})
        if is_success(status_code):
            logger.info(f'[{node}] Reset.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not reset node.')

    elif action_parameters[0] == "status":
        logger.info(f'[{node}] Fetching power status')
        response, status_code = execute_redfish_request(
            node, node_configuration, system_endpoint, logger, parameters)
        if is_success(status_code):
            power_state = response.get('PowerState', 'Unknown') if isinstance(response, dict) else 'Unknown'
            logger.info(f'[{node}] Power status: {power_state}')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not get node power status.')

    else:
        logger.error(f'[{node}] Error, unknown power action {action_parameters[0]}')
        return 1


def boot(node, node_configuration, action_parameters, parameters, logger):
    system_endpoint = get_system_endpoint(node, node_configuration, parameters, logger)
    if not system_endpoint:
        return 1

    if action_parameters[0] == "disk":
        logger.info(f'[{node}] Setting next boot device to disk')
        _, status_code = execute_redfish_request(
            node, node_configuration, f'{system_endpoint}/Actions/ComputerSystem.SetDefaultBootOrder',
            logger, parameters, method='POST')
        if is_success(status_code):
            logger.info(f'[{node}] Next boot set to disk.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not set next boot to disk.')

    elif action_parameters[0] == "bios":
        etag = get_etag(node, node_configuration, system_endpoint, parameters, logger)
        extra_headers = {'If-Match': etag} if etag else None
        logger.info(f'[{node}] Setting next boot device to BIOS setup')
        _, status_code = execute_redfish_request(
            node, node_configuration, system_endpoint,
            logger, parameters, method='PATCH',
            payload={"Boot": {"BootSourceOverrideTarget": "BiosSetup", "BootSourceOverrideEnabled": "Once"}},
            extra_headers=extra_headers)
        if is_success(status_code):
            logger.info(f'[{node}] Next boot set to BIOS.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not set next boot to BIOS.')

    elif action_parameters[0] == "pxe":
        etag = get_etag(node, node_configuration, system_endpoint, parameters, logger)
        extra_headers = {'If-Match': etag} if etag else None
        logger.info(f'[{node}] Setting next boot device to PXE')
        _, status_code = execute_redfish_request(
            node, node_configuration, system_endpoint,
            logger, parameters, method='PATCH',
            payload={"Boot": {"BootSourceOverrideTarget": "Pxe", "BootSourceOverrideEnabled": "Once"}},
            extra_headers=extra_headers)
        if is_success(status_code):
            logger.info(f'[{node}] Next boot set to PXE.')
            return 0
        else:
            return fail(node, node_configuration, parameters, logger, 'Error, could not set next boot to PXE.')

    else:
        logger.error(f'[{node}] Error, unknown boot action {action_parameters[0]}')
        return 1
