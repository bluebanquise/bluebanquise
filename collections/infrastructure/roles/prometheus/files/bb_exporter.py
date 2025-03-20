#!/usr/bin/env python3.6

# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# bb exporter, to provide probes on remonte hosts
# 2020 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/bluebanquise/bluebanquise - MIT license

import os
import importlib.util
import time
import yaml

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY


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
    print(bcolors.OKBLUE+'[INFO] Loading '+filename+bcolors.ENDC)
    with open(filename, 'r') as f:
        # return yaml.load(f, Loader=yaml.FullLoader) ## Waiting for PyYaml 5.1
        return yaml.load(f)


if __name__ == '__main__':

    print('\nStarting BlueBanquise Exporter\n')

    exporter_configuration = load_file('/etc/bb_exporter/bb_exporter.yml')
    plugins_path = exporter_configuration['plugins_path']

    print(bcolors.OKBLUE+'[INFO] Loading plugins'+bcolors.ENDC)
    modules = {}
    for f in os.listdir(plugins_path+'/'):
        if os.path.isfile(plugins_path+'/'+f) and f.endswith('.py') and f != 'main.py' and f[:-3] in exporter_configuration['collectors']:
            modname = f[:-3]  # remove '.py' extension
            spec = importlib.util.spec_from_file_location(modname, plugins_path+'/'+f)
            modules[modname] = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modules[modname])

    print(bcolors.OKBLUE+'  Found:'+bcolors.ENDC)
    for plugin in modules:
        print(bcolors.OKBLUE+'    - '+plugin+bcolors.ENDC)

    print(bcolors.OKBLUE+'[INFO] Starting http server'+bcolors.ENDC)
    start_http_server(9777)

    print(bcolors.OKBLUE+'[INFO] Registering collector plugins...'+bcolors.ENDC)
    for coll in exporter_configuration['collectors']:
        if coll in modules:
            print(bcolors.OKBLUE+'    - Registering '+coll+bcolors.ENDC)
            REGISTRY.register(modules[coll].Collector(exporter_configuration['collectors'][coll]))
        else:
            print('Collector '+coll+' was defined in configuration file but could not be found.')

    while True:
        time.sleep(1)
