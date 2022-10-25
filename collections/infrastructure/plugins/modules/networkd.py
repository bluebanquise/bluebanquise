#!/usr/bin/python

import re
import os
import pathlib
import subprocess
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text

class NetworkdModuleError(Exception):
    pass

def same_list_file(list1, filepath):
    same = True
    if os.path.exists(filepath):
        with open(filepath) as f:
            filepath_lines = f.readlines()
        if len(list1) != len(filepath_lines):
            same = False
        else:
            for i in range(0,len(list1),1):
                if list1[i] != filepath_lines[i].replace("\n", ""):
                    same = False
    else:
        same = False
    return same

def write_list_to_file(list1, filepath):
    path = pathlib.Path(filepath)
    os.makedirs(path.parent, mode = 0o755, exist_ok=True)
    f = open(filepath, "w")
    for it in list1:
        f.write(it + "\n")
    f.close()

class Networkd(object):

    def __init__(self, module):
        self.module = module
        self.conn_name = module.params['conn_name']
        self.master = module.params['master']
        self.state = module.params['state']
        self.ifname = module.params['ifname']
        self.type = module.params['type']
        self.ip4 = module.params['ip4']
        self.gw4 = module.params['gw4']
        self.routes4 = module.params['routes4']
        self.dns4 = module.params['dns4']
        self.method4 = module.params['method4']
        self.mode = module.params['mode']
        self.mtu = module.params['mtu']
        self.vlanid = module.params['vlanid']
        self.vlandev = module.params['vlandev']

    def generate_network(self):
        network = []

        # MATCH
        network.append("[Match]")
        if self.ifname is not None:
            network.append("Name=" + self.ifname)
        elif self.conn_name is not None:
            network.append("Name=" + self.conn_name)
#        elif self.mac is not None:
#            network.append("MACAddress=" + self.mac)

        # NETWORK
        network.append("[Network]")
        if self.method4 == "auto":
            network.append("DHCP=True")
        if self.dns4 is not None:
            for dns4 in self.dns4:
                network.append("DNS=" + dns4)
        if self.type == "bond-slave":
            if self.master is not None:
                network.append("Bond=" + self.master)

        # ADDRESS
        if self.method4 == "manual" or self.method4 is None:
            network.append("[Address]")
            if self.ip4 is not None:
                for ip4 in self.ip4:
                    network.append("Address=" + ip4)

        # ADDRESS
        if self.gw4 is not None:
            network.append("[Route]")
            network.append("Gateway=" + self.gw4)
        if self.routes4 is not None:
            for route4 in self.routes4:
                network.append("[Route]")
                network.append("Destination=" + route4.split(' ')[0])
                network.append("Gateway=" + route4.split(' ')[1])
                if len(route4.split(' ')) > 2:
                    network.append("Metric=" + route4.split(' ')[2])

        # LINK
        if self.mtu is not None:
            network.append("[Link]")
            network.append("MTUBytes=" + self.mtu)

        return network

    def generate_netdev(self):
        netdev = []

        # NETDEV
        netdev.append("[NetDev]")
        netdev.append("Name=" + self.conn_name)

        if self.type == "bond":
            netdev.append("Kind=bond")
        elif self.type == "vlan":
            netdev.append("Kind=vlan")

        # BOND
        if self.type == "bond":
            netdev.append("[Bond]")
            if self.mode is not None:
                netdev.append("Mode=" + self.mode)
            else:
                netdev.append("Mode=802.3ad")

        # VLAN
        if self.type == "vlan":
            netdev.append("[VLAN]")
            netdev.append("Id=" + str(self.vlanid))

        return netdev

def main():
    # Parsing argument file
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', required=True, choices=['absent', 'present']),
            conn_name=dict(type='str', required=True),
            master=dict(type='str'),
            ifname=dict(type='str'),
            type=dict(type='str',
                      choices=[
                          'bond',
                          'bond-slave',
                          'ethernet',
                          'infiniband',
                          'vlan',
                      ]),
            ip4=dict(type='list', elements='str'),
            gw4=dict(type='str'),
            routes4=dict(type='list', elements='str'),
            dns4=dict(type='list', elements='str'),
            method4=dict(type='str', choices=['auto', 'link-local', 'manual', 'shared', 'disabled']),
            mode=dict(type='str', default='balance-rr',
                      choices=['802.3ad', 'active-backup', 'balance-alb', 'balance-rr', 'balance-tlb', 'balance-xor', 'broadcast']),
            mtu=dict(type='str'),
            vlanid=dict(type='int'),
            vlandev=dict(type='str'),
        ),
        mutually_exclusive=[],
        required_if=[],
        supports_check_mode=True,
    )
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    networkd = Networkd(module)

    (rc, out, err) = (None, '', '')
    result = {'conn_name': networkd.conn_name, 'state': networkd.state}
    changed = False


    # check for issues
    if networkd.conn_name is None:
        networkd.module.fail_json(msg="Please specify a name for the connection")

    try:
        if networkd.state == 'absent':
            # Simply check no files are associated with this conn_name
            print("Absent")
        elif networkd.state == 'present':

            if networkd.type in ['ethernet','infiniband','bond-slave','vlan']:

                # Generate Network file
                network = networkd.generate_network()
                # Read current Network file if exist and compare if changes
                network_file = "/etc/systemd/network/" + networkd.conn_name +".network"
                # Check if content is the same
                changed = not same_list_file(network,network_file)
                # Write configuration if changes detected
                if changed:
                    write_list_to_file(network, network_file)

            if networkd.type in ['bond','vlan']:

                # Generate Netdev file
                netdev = networkd.generate_netdev()
                # Read current Network file if exist and compare if changes
                netdev_file = "/etc/systemd/network/" + networkd.conn_name +".netdev"
                # Check if content is the same
                changed = not same_list_file(netdev,netdev_file)
                # Write configuration if changes detected
                if changed:
                    write_list_to_file(netdev, netdev_file)

            if networkd.type in ['vlan']:

                # Ensure vlan is registered in main connection (vlandev) network file
                vlandev_file = "/etc/systemd/network/" + networkd.vlandev +".network"
                path = pathlib.Path(vlandev_file)
                os.makedirs(path.parent, mode = 0o755, exist_ok=True)
                f = open(vlandev_file)
                filepath_lines = f.readlines()
                vlan_present = False
                for i in range(0,len(filepath_lines),1):
                    if filepath_lines[i] == "VLAN=" + networkd.conn_name:
                        vlan_present = True
                if not vlan_present:
                    for i in range(0,len(filepath_lines),1):
                        if filepath_lines[i] == "[Network]\n":
                            filepath_lines.insert(i+1, "VLAN=" + networkd.conn_name)
                            f.close()
                            f = open(vlandev_file, "w")
                            for j in range(0,len(filepath_lines),1):
                                f.write(filepath_lines[j] + "\n")
                            break
                f.close()

            # Post actions
            #if changed == 1:
                #stdout, stderr = subprocess.Popen("networkctl reload", stdout=os.subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()
                #stdout, stderr = subprocess.Popen("networkctl reconfigure " + networkd.conn_name, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()


    except NetworkdModuleError as e:
        module.fail_json(name=networkd.conn_name, msg=str(e))

    if changed == 0:
        result['changed'] = False
    else:
        result['changed'] = True

    result['stdout'] = "COUCOU LES AMICHES"

    module.exit_json(**result)


if __name__ == '__main__':
    main()
