#!/usr/bin/env python3

# Import dependances
from ClusterShell.NodeSet import NodeSet
import yaml

# Colors, from https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = ArgumentParser()
parser.add_argument("-n", "--nodes", dest="nodes",
                    help="Target node(s). Use nodeset format for ranges.", metavar="NODE")
parser.add_argument("-b", "--boot", dest="boot",
                    help="Next pxe boot: can be osdeploy or disk.")
passed_arguments = parser.parse_args()

print(bcolors.OKBLUE+'Loading /etc/bluebanquise/pxe/nodes_parameters.yml'+bcolors.ENDC)
with open('/etc/bluebanquise/pxe/node_parameters.yml', 'r') as f:
    nodes_parameters = yaml.load(f)

for node in NodeSet(passed_arguments.nodes):
    print(str(node))

