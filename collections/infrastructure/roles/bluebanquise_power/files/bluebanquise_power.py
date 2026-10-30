#!/usr/lib/bluebanquise/venv/bin/python3
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from concurrent.futures import ThreadPoolExecutor
import os
import random
import threading
import time
import yaml
import importlib.util
from ClusterShell.NodeSet import NodeSet, NodeSetParseError
import logging
import sys

# usage: bluebanquise-power c001 power on

print("""\

                (o_
      (o_  (o_  //\\
      (/)_ (/)_ V_/_

   BlueBanquise power
   v1.0.0
   https://github.com/bluebanquise/bluebanquise/

""", flush=True)  # flush: banner must appear before logs (stderr) when output is piped

# Valid parameters for each action. Each protocol plugin implements one function per action.
ACTIONS = {
    'power': ['on', 'off', 'reset', 'status'],
    'boot': ['disk', 'pxe', 'bios'],
}

# Get arguments
parser = ArgumentParser(
    prog="bluebanquise-power",
    description="Manage hosts power and next boot device through their BMC (IPMI or Redfish).",
    formatter_class=RawDescriptionHelpFormatter,
    epilog="""actions:
  power on|off|reset|status   power on, hard power off, hard reset, or display power state
  boot disk|pxe|bios          set next boot device (one time)

examples:
  bluebanquise-power c001 power status
  bluebanquise-power c[001-004] boot pxe
  bluebanquise-power --dryrun c[001-004] power reset
  bluebanquise-power --delay 2 --random c[001-100] power on
""")
parser.add_argument("nodes", help="Target node(s), using nodeset format (c001, c[001-004], c001,login1).")
parser.add_argument("action", choices=sorted(ACTIONS), help="Action to perform.")
parser.add_argument("parameter", help="Action parameter, see actions below.")
parser.add_argument("--dryrun", action='store_true', dest='dryrun', help="Enable dryrun mode")
parser.add_argument("--debug", action='store_true', dest='debug',
                    help="Enable debug mode. WARNING: prints executed commands in plain text, BMC passwords included.")
parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds for module operations. Default is 10 (seconds).")
parser.add_argument("--parallel", type=int, default=16, help="Maximum number of nodes handled at the same time. Default is 16.")
parser.add_argument("--delay", type=float, default=0,
                    help="power on/reset only: minimum delay in seconds between two nodes starting, to limit "
                         "the power surge when powering many nodes at once. Default is 0 (no delay).")
parser.add_argument("--random", action='store_true', dest='random',
                    help="Process nodes in random order, for example to spread power on across racks/PDUs.")

# parameters is a dict: parameters['action'], parameters['debug'], parameters['timeout']...
parameters = vars(parser.parse_args())
action = parameters['action']
parameter = parameters['parameter']

if parameter not in ACTIONS[action]:
    parser.error(f"invalid parameter '{parameter}' for action '{action}' "
                 f"(choose from {', '.join(ACTIONS[action])})")
if parameters['parallel'] < 1:
    parser.error("--parallel must be 1 or more")
if parameters['delay'] < 0:
    parser.error("--delay cannot be negative")

try:
    nodes = NodeSet(parameters['nodes'])
except NodeSetParseError as e:
    parser.error(f"invalid nodeset '{parameters['nodes']}': {e}")

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG if parameters['debug'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only log to the terminal
    ]
)
logger = logging.getLogger('bluebanquise-power')

# Define the path to the YAML file
configuration_file_path = '/etc/bluebanquise/bluebanquise-power/bluebanquise-power.yml'

if not os.path.exists(configuration_file_path):
    logger.error(f'No configuration file found at {configuration_file_path}. Deploy the bluebanquise_power role first.')
    sys.exit(1)
try:
    with open(configuration_file_path, 'r') as file:
        power_configuration = yaml.safe_load(file)
except PermissionError:
    logger.error(f'Cannot read {configuration_file_path} (it contains BMC credentials). '
                 f'Run this tool as root or as a member of the bluebanquise group.')
    sys.exit(1)
except yaml.YAMLError as e:
    logger.error(f'Invalid configuration file {configuration_file_path}: {e}')
    sys.exit(1)

if not isinstance(power_configuration, dict) or not power_configuration.get('nodes'):
    logger.error('No nodes defined in configuration. Check that hosts have a bmc entry and '
                 'hw_board_authentication credentials in the inventory, then re-run the role.')
    sys.exit(1)

plugins_dir = '/usr/lib/bluebanquise/bluebanquise-power/plugins'

# Load plugins from the specified directory
power_modules = {}
for file_path in os.listdir(plugins_dir):
    if file_path.endswith('.py'):
        module_name = file_path[:-3]
        full_path = os.path.join(plugins_dir, file_path)

        spec = importlib.util.spec_from_file_location(module_name, full_path)
        module = importlib.util.module_from_spec(spec)
        # A plugin needing a missing Python module (for example requests for REDFISH) must not
        # prevent other protocols from working: report it, and continue without this plugin.
        try:
            spec.loader.exec_module(module)
        except ImportError as e:
            logger.warning(f'Could not load protocol plugin {module_name} ({full_path}): {e}. '
                           f'Nodes using protocol {module_name} cannot be managed.')
            continue

        power_modules[module_name] = module

# --delay only applies to actions that make nodes draw power at start (inrush current)
use_delay = (parameters['delay'] > 0 and action == 'power' and parameter in ['on', 'reset']
             and not parameters['dryrun'])
start_lock = threading.Lock()
next_start_time = 0


def wait_for_start_slot():
    """
    Make sure two nodes never start less than --delay seconds apart, whatever the number of
    parallel threads: each thread takes the lock in turn, waits for its start time, and sets
    the start time of the next one.
    """
    global next_start_time
    with start_lock:
        wait = next_start_time - time.time()
        if wait > 0:
            time.sleep(wait)
        next_start_time = time.time() + parameters['delay']


def run_node(node):
    """
    Run the requested action on one node. Called in parallel for several nodes (one thread per
    node, up to --parallel at the same time). Returns a (return_code, detail) tuple.
    """
    if node not in power_configuration['nodes']:
        logger.error(f'[{node}] Node not found in configuration file. Skipping.')
        return 1, 'not found in configuration'

    node_configuration = power_configuration['nodes'][node]
    # BMC is reached by its ip4 when set, else by its name. Some BMCs refuse unknown names (Dell
    # iDRAC9 5.10+ HostHeaderCheck rejects HTTP requests not using its own name or IP address).
    if isinstance(node_configuration.get('bmc'), dict):
        bmc = node_configuration['bmc']
        if bmc.get('ip4'):
            bmc['address'] = str(bmc['ip4']).split('/')[0]
        else:
            bmc['address'] = bmc.get('name')

    node_protocol = node_configuration.get('protocol')
    if node_protocol not in power_modules:
        logger.error(f'[{node}] Unknown protocol "{node_protocol}" (available: {", ".join(sorted(power_modules))}). '
                     f'Check hw_board_authentication protocol value in the inventory. Skipping.')
        return 1, f'unknown protocol {node_protocol}'

    if use_delay:
        wait_for_start_slot()

    # An unexpected error on one node (incomplete configuration, plugin bug...) must not stop
    # the whole run: report it, and continue with other nodes. Full traceback in debug mode.
    module = power_modules[node_protocol]
    try:
        if action == 'power':
            return module.power(node, node_configuration, parameter, parameters, logger)
        else:
            return module.boot(node, node_configuration, parameter, parameters, logger)
    except Exception as e:
        logger.error(f'[{node}] Unexpected error: {type(e).__name__}: {e}')
        logger.debug(f'[{node}] Traceback:', exc_info=True)
        return 1, f'unexpected error: {type(e).__name__}: {e}'


nodes_to_process = list(nodes)
if parameters['random']:
    random.shuffle(nodes_to_process)

# Run all nodes in parallel, at most --parallel at the same time
results = {}
with ThreadPoolExecutor(max_workers=parameters['parallel']) as executor:
    running = {}
    for node in nodes_to_process:
        running[node] = executor.submit(run_node, node)
    for node in nodes_to_process:
        results[node] = running[node].result()

# Final status table, in nodeset order. Colors only when writing to a terminal, so that
# redirecting output to a file does not fill it with color codes.
if sys.stdout.isatty():
    GREEN, RED, RESET = '\033[92m', '\033[91m', '\033[0m'
else:
    GREEN, RED, RESET = '', '', ''
# Width of the first column: longest node name
width = len('NODE')
for node in nodes:
    if len(node) > width:
        width = len(node)
print()
print('NODE'.ljust(width) + '  RESULT  DETAILS')
failed_nodes = []
for node in nodes:
    return_code, detail = results[node]
    if return_code == 0:
        result = GREEN + 'OK'.ljust(6) + RESET
    else:
        result = RED + 'ERROR'.ljust(6) + RESET
        failed_nodes.append(node)
    print(node.ljust(width) + '  ' + result + '  ' + str(detail))
print(flush=True)

# Exit code allows scripts to detect a failure: 1 if the action failed on at least one node
if failed_nodes:
    logger.error(f'Action failed on {len(failed_nodes)}/{len(nodes)} node(s): {NodeSet.fromlist(failed_nodes)}')
    sys.exit(1)
sys.exit(0)
