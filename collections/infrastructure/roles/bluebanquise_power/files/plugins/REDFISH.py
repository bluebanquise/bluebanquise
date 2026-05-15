import requests
import json
from requests.auth import HTTPBasicAuth

# Disable SSL warnings for simplicity in this example
# In production, handle SSL certificates properly
requests.packages.urllib3.disable_warnings()

def execute_redfish_request(node, node_configuration, endpoint, logger, method='GET', payload=None):
    url = f"https://{node_configuration['bmc']['name']}/redfish/v1/{endpoint}"
    auth = HTTPBasicAuth(node_configuration['user'], node_configuration['password'])
    headers = {'Content-Type': 'application/json'}

    if not parameters.get('dryrun', False):
        try:
            response = requests.request(method, url, auth=auth, headers=headers, json=payload, verify=False)
            response.raise_for_status()
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            logger.error(f'[{node}] Error executing Redfish request: {e}')
            return None, getattr(e.response, 'status_code', None)
    else:
        logger.info(f'[{node}] Dryrun. url: {url}, payload: {payload}')
        return 0, 200

def power(node, node_configuration, action_parameters, parameters, logger):
    if action_parameters[0] == "on":
        _, status_code = execute_redfish_request(node, node_configuration, 'Systems/System.Embedded.1/Actions/ComputerSystem.Reset', logger, method='POST', payload={"ResetType": "On"})
        if status_code == 200:
            logger.info(f'[{node}] Powered on.')
            return 0
        else:
            logger.error(f'[{node}] Error, could not power on node.')
            return 1

    elif action_parameters[0] == "off":
        _, status_code = execute_redfish_request(node, node_configuration, 'Systems/System.Embedded.1/Actions/ComputerSystem.Reset', logger, method='POST', payload={"ResetType": "ForceOff"})
        if status_code == 200:
            logger.info(f'[{node}] Powered off.')
            return 0
        else:
            logger.error(f'[{node}] Error, could not power off node.')
            return 1

    elif action_parameters[0] == "reset":
        _, status_code = execute_redfish_request(node, node_configuration, 'Systems/System.Embedded.1/Actions/ComputerSystem.Reset', logger, method='POST', payload={"ResetType": "Reset"})
        if status_code == 200:
            logger.info(f'[{node}] Reset.')
            return 0
        else:
            logger.error(f'[{node}] Error, could not reset node.')
            return 1

    elif action_parameters[0] == "status":
        response, status_code = execute_redfish_request(node, node_configuration, 'Systems/System.Embedded.1', logger)
        if status_code == 200:
            power_state = response.get('PowerState', 'Unknown')
            logger.info(f'[{node}] Power status: {power_state}')
            return 0
        else:
            logger.error(f'[{node}] Error, could not get node power status.')
            return 1

    else:
        logger.error(f'[{node}] Error, unknown power action {action_parameters[0]}')
        return 1

def boot(node, node_configuration, action_parameters, parameters):
    if action_parameters[0] == "disk":
        _, status_code = execute_redfish_request(node, node_configuration, 'Systems/System.Embedded.1/Actions/ComputerSystem.SetDefaultBootOrder', logger, method='POST')
        if status_code == 200:
            logger.info(f'[{node}] Next boot set to disk.')
            return 0
        else:
            logger.error(f'[{node}] Error, could not set next boot to disk.')
            return 1

    elif action_parameters[0] == "bios":
        _, status_code = execute_redfish_request(node, node_configuration, 'Systems/System.Embedded.1/Actions/ComputerSystem.ChangeBootOrder', logger, method='POST', payload={"Boot": {"BootSourceOverrideTarget": "Bios"}})
        if status_code == 200:
            logger.info(f'[{node}] Next boot set to BIOS.')
            return 0
        else:
            logger.error(f'[{node}] Error, could not set next boot to BIOS.')
            return 1

    elif action_parameters[0] == "pxe":
        _, status_code = execute_redfish_request(node, node_configuration, 'Systems/System.Embedded.1/Actions/ComputerSystem.ChangeBootOrder', logger, method='POST', payload={"Boot": {"BootSourceOverrideTarget": "Pxe"}})
        if status_code == 200:
            logger.info(f'[{node}] Next boot set to PXE.')
            return 0
        else:
            logger.error(f'[{node}] Error, could not set next boot to PXE.')
            return 1

    else:
        logger.error(f'[{node}] Error, unknown boot action {action_parameters[0]}')
        return 1

