#!/usr/bin/env python3

# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# booset tool, to manage nodes PXE boot
# 2019 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
#        Adrien Ribeiro <adrien.ribeiro@atos.net>
# https://github.com/bluebanquise/bluebanquise - MIT license

from ClusterShell.NodeSet import NodeSet
from argparse import ArgumentParser
import grp
import logging
import os
import pwd
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


def load_file(filename):
    logging.info(bcolors.OKBLUE+'Loading '+filename+bcolors.ENDC)
    with open(filename, 'r') as f:
        # return yaml.load(f, Loader=yaml.FullLoader) ## Waiting for PyYaml 5.1
        return yaml.load(f)


def set_default_boot(node, boot, node_image=None, extra_parameters=None):
    logging.info('    ├── '+bcolors.OKBLUE+'Switching boot to '+boot+bcolors.ENDC)
    logging.info('    ├── '+bcolors.OKBLUE+'Editing file /var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe'+bcolors.ENDC)
    with open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe', 'r') as f:
        filebuffer = f.readlines()
    for i in range(len(filebuffer)):
        if 'menu-default' in filebuffer[i]:
            filebuffer[i] = 'set menu-default boot{}\n'.format(boot)
        if ('node-image' in filebuffer[i]) and (node_image is not None):
            filebuffer[i] = 'set node-image {}\n'.format(node_image)
        if ('extra-parameters' in filebuffer[i]) and (extra_parameters is not None):
            filebuffer[i] = 'set extra-parameters {}\n'.format(extra_parameters)
    with open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe', 'w') as f:
        f.writelines(filebuffer)
    logging.info('    └── '+bcolors.OKGREEN+'[OK] Done.'+bcolors.ENDC)


# Get arguments passed to bootset
parser = ArgumentParser()
parser.add_argument("-n", "--nodes", dest="nodes",
                    help="Target node(s). Use nodeset format for ranges.", metavar="NODE")
parser.add_argument("-b", "--boot", dest="boot",
                    help="Next pxe boot: can be osdeploy, diskless, clone, clonedeploy, or disk.")
parser.add_argument("-f", "--force", dest="force", default=" ",
                    help="Force. 'update' = files update, 'dhcp' = better dracut dhcp, 'network' = static ip. Combine using comma separator.")
parser.add_argument("-i", "--image", dest="image", default="none",
                    help="Specify diskless or clone image to be used, if using diskless/clone/clonedeploy boot.")
parser.add_argument("-e", "--extra-parameters", dest="extra_parameters", default="none",
                    help="Add extra parameters for boot chain, some addons may need some.")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="Do not print INFO messages.")

passed_arguments = parser.parse_args()

# Enable logging
loglevel = logging.INFO
if passed_arguments.quiet:
    loglevel = logging.WARNING
logging.basicConfig(format='[%(levelname)s] %(message)s', level=loglevel)

# Load and extract configuration files
nodes_parameters = load_file('/etc/bluebanquise/pxe/nodes_parameters.yml')
pxe_parameters = load_file('/etc/bluebanquise/pxe/pxe_parameters.yml')

apache_uid = pwd.getpwnam(pxe_parameters["pxe_parameters"]["apache_uid"]).pw_uid
apache_gid = grp.getgrnam(pxe_parameters["pxe_parameters"]["apache_gid"]).gr_gid

# Ensure passed boot argument exists
if 'osdeploy' not in passed_arguments.boot and 'diskless' not in passed_arguments.boot and 'clone' not in passed_arguments.boot and 'clonedeploy' not in passed_arguments.boot and 'disk' not in passed_arguments.boot:
    logging.error(bcolors.FAIL+'Passed argument "'+passed_arguments.boot+'" for boot not know. Please check syntax.'+bcolors.ENDC)
    quit()

# Iteration on nodes
for node in NodeSet(passed_arguments.nodes):

    # Check if node exist in Ansible generated file
    logging.info(bcolors.OKBLUE+'Cheking if node '+str(node)+' exist...'+bcolors.ENDC)
    if str(node) in nodes_parameters:

        logging.info(bcolors.OKGREEN+'[OK] Working on node '+str(node)+' ...'+bcolors.ENDC)
        # Check if we need to create or update files
        logging.info('    ├── '+bcolors.OKBLUE+'Checking '+str(node)+' files...'+bcolors.ENDC)
        if str(os.path.exists('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe')) == 'False' or 'update' in passed_arguments.force:
            logging.info('    ├── '+bcolors.OKBLUE+'Creating file /var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe'+bcolors.ENDC)
            dedicated_parameters = str('')
            if 'network' in passed_arguments.force:
                dedicated_parameters = str('ip='+nodes_parameters[str(node)]["network"]["node_main_network_interface_ip"]+'::'+nodes_parameters[str(node)]["network"]["node_main_network_gateway"]+':'+nodes_parameters[str(node)]["network"]["node_main_network_netmask"]+':'+str(node)+':'+nodes_parameters[str(node)]["network"]["node_main_network_interface"]+':none')
            if 'dhcp' in passed_arguments.force:
                dedicated_parameters = dedicated_parameters + ' rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4 '

            generic_node_ipxe = '\n'.join((
                '#!ipxe',
                'echo | Entering {}.ipxe file.'.format(node),
                'echo |',
                'echo | Getting host specific variables...',
                '# Current default action',
                'set menu-default bootdisk',
                '# Current node parameters:',
                'set equipment-profile {}'.format(nodes_parameters[str(node)]['equipment_profile']),
                'set dedicated-kernel-parameters {}'.format(dedicated_parameters),
                'set node-image none',
                'set extra-parameters none',
                'echo |',
                '# Now chain to menu menu',
                'echo | Now chaining to --> equipment_profiles/${equipment-profile}.ipxe',
                'sleep 2',
                'chain http://${next-server}/preboot_execution_environment/equipment_profiles/${equipment-profile}.ipxe || shell'))

            with open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe', 'w') as ff:
                ff.write(generic_node_ipxe)
            os.chown('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe', apache_uid, apache_gid)
            if pxe_parameters["pxe_parameters"]["ansible_selinux_status"] == "enabled":
                os.system('restorecon -v /var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe')
        logging.info('    ├── '+bcolors.OKGREEN+'[OK] Done.'+bcolors.ENDC)

        set_default_boot(node=node, boot=passed_arguments.boot, node_image=passed_arguments.image, extra_parameters=passed_arguments.extra_parameters)

    else:
        logging.warning(bcolors.WARNING+'Node '+str(node)+' do not exist. Skipping.'+bcolors.ENDC)
