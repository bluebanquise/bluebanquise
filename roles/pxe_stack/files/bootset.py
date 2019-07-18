#!/usr/bin/env python3

# Import dependances
from ClusterShell.NodeSet import NodeSet
from argparse import ArgumentParser
from shutil import copy2
import yaml
import os
import re

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

print(bcolors.OKBLUE+'[INFO] Loading /etc/bluebanquise/pxe/nodes_parameters.yml'+bcolors.ENDC)
with open('/etc/bluebanquise/pxe/nodes_parameters.yml', 'r') as f:
    nodes_parameters = yaml.load(f)

for node in NodeSet(passed_arguments.nodes):
    if str(node) in nodes_parameters:
        print(bcolors.OKGREEN+'[OK] Checking '+str(node)+' files...'+bcolors.ENDC)
        if str(os.path.exists('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe')) == 'False':
            print(bcolors.OKBLUE+'[INFO] Creating file /var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe'+bcolors.ENDC)
            file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe','w')
            file.write("#!ipxe\n\n")
            file.write("# Current default action\n\n")
            file.write("set menu-default bootdisk\n\n")
            file.write("# Now chain to menu menu\n\n")
            file.write("chain http://${next-server}/preboot_execution_environment/menu.ipxe || shell\n\n")
            file.write("exit\n")
            file.close()
        if str(os.path.exists('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'_bootosdeploy.ipxe')) == 'False':
            print(bcolors.OKBLUE+'[INFO] Creating file /var/www/html/preboot_execution_environment/nodes/'+str(node)+'_bootosdeploy.ipxe'+bcolors.ENDC)
            print(bcolors.OKBLUE+'[INFO] Copy from /var/www/html/preboot_execution_environment/ipxe_configurations/'+nodes_parameters[str(node)]["equipment_profile"]+'.ipxe'+bcolors.ENDC)
            copy2('/var/www/html/preboot_execution_environment/ipxe_configurations/'+nodes_parameters[str(node)]["equipment_profile"]+'.ipxe', '/var/www/html/preboot_execution_environment/nodes/'+str(node)+'_bootosdeploy.ipxe')
        print(bcolors.OKGREEN+'[OK] Done.'+bcolors.ENDC)
        if passed_arguments.boot == 'disk':
            print(bcolors.OKBLUE+'[INFO] Switching boot to disk'+bcolors.ENDC)
            print(bcolors.OKBLUE+'[INFO] Editing file /var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe'+bcolors.ENDC)
            file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe','r')
            filebuffer = file.readlines()
            for i in range(len(filebuffer)):
                if 'menu-default' in filebuffer[i]:
                    filebuffer[i] = 'set menu-default bootdisk\n'
            file.close
            file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe','w')
            file.writelines(filebuffer)
            file.close
            print(bcolors.OKBLUE+'[INFO] Done.'+bcolors.ENDC)
            continue

        if passed_arguments.boot == 'osdeploy':
            print(bcolors.OKBLUE+'[INFO] Switching boot to osdeploy'+bcolors.ENDC)
            print(bcolors.OKBLUE+'[INFO] Editing file /var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe'+bcolors.ENDC)
            file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe','r')
            filebuffer = file.readlines()
            for i in range(len(filebuffer)):
                if 'menu-default' in filebuffer[i]:
                    filebuffer[i] = 'set menu-default osdeploy\n'
            file.close
            file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe','w')
            file.writelines(filebuffer)
            file.close
            print(bcolors.OKBLUE+'[INFO] Done.'+bcolors.ENDC)
            continue

    else:
        print(bcolors.WARNING+'[WARNING] Node '+str(node)+' do not exist. Skipping.'+bcolors.ENDC)
        continue


