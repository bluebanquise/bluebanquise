#!/usr/bin/python
# noqa: E501

import os
import pathlib
from ansible.module_utils.basic import AnsibleModule


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
            for i in range(0, len(list1), 1):
                if list1[i] != filepath_lines[i].replace("\n", ""):
                    same = False
    else:
        same = False
    return same


def write_list_to_file(list1, filepath, check_mode):
    if check_mode:
        return
    path = pathlib.Path(filepath)
    os.makedirs(path.parent, mode=0o755, exist_ok=True)
    f = open(filepath, "w")
    for it in list1:
        f.write(it + "\n")
    f.close()


def check_milliseconds_field_is_digit(networkd,  name):
    networkd_field = getattr(networkd, name)
    if networkd_field is not None and not networkd_field.isdigit():
        msg = name + " should only contain numbers representing milliseconds"
        networkd.module.fail_json(msg=msg)


class Networkd(object):

    def __init__(self, module):
        self.module = module
        self.conn_name = module.params['conn_name']
        self.master = module.params['master']
        self.state = module.params['state']
        self.arp_interval = module.params['arp_interval']
        self.arp_ip_target = module.params['arp_ip_target']
        self.downdelay = module.params['downdelay']
        self.ifname = module.params['ifname']
        self.type = module.params['type']
        self.ip4 = module.params['ip4']
        self.gw4 = module.params['gw4']
        self.routes4 = module.params['routes4']
        self.dns4 = module.params['dns4']
        self.method4 = module.params['method4']
        self.miimon = module.params['miimon']
        self.mode = module.params['mode']
        self.mtu = module.params['mtu']
        self.updelay = module.params['updelay']
        self.vlanid = module.params['vlanid']
        self.vlandev = module.params['vlandev']
        self.vlan_mapping = module.params['vlan_mapping']

    def generate_network(self):
        network = []

        # MATCH
        network.append("[Match]")
        if self.ifname is not None:
            ifname = self.ifname
        elif self.conn_name is not None:
            ifname = self.conn_name
        network.append("Name=" + ifname)
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
        if self.vlan_mapping is not None and len(self.vlan_mapping) > 0:
            for id in self.vlan_mapping:
                network.append("VLAN=" + ifname + "." + str(id))

        # ADDRESS
        if self.method4 == "manual" or self.method4 is None:
            if self.ip4 is not None:
                for ip4 in self.ip4:
                    network.append("[Address]")
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
            network.append("MTUBytes=" + str(self.mtu))

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
            if self.miimon is not None:
                netdev.append("MIIMonitorSec=" + self.miimon + "ms")
            if self.updelay is not None:
                netdev.append("UpDelaySec=" + self.updelay + "ms")
            if self.downdelay is not None:
                netdev.append("DownDelaySec=" + self.downdelay + "ms")
            if self.arp_interval is not None:
                netdev.append("ARPIntervalSec=" + self.arp_interval + "ms")
            if self.arp_ip_target is not None:
                netdev.append("ARPIPTargets=" + self.arp_ip_target)

        # VLAN
        if self.type == "vlan":
            netdev.append("[VLAN]")
            netdev.append("Id=" + str(self.vlanid))

        return netdev


def main():
    # Parsing argument file
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', required=True,
                       choices=['absent', 'present']),
            conn_name=dict(type='str', required=True),
            master=dict(type='str'),
            arp_interval=dict(type='str'),
            arp_ip_target=dict(type='str'),
            downdelay=dict(type='str'),
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
            method4=dict(type='str',
                         choices=[
                          'auto',
                          'link-local',
                          'manual',
                          'shared',
                          'disabled'
                         ]),
            mode=dict(type='str', default='balance-rr',
                      choices=[
                          '802.3ad',
                          'active-backup',
                          'balance-alb',
                          'balance-rr',
                          'balance-tlb',
                          'balance-xor',
                          'broadcast'
                      ]),
            miimon=dict(type='str'),
            mtu=dict(type='int'),
            updelay=dict(type='str'),
            vlanid=dict(type='int'),
            vlandev=dict(type='str'),
            vlan_mapping=dict(type='list', elements='int'),
        ),
        mutually_exclusive=[],
        required_if=[],
        supports_check_mode=True,
    )
    module.run_command_environ_update = dict(
        LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    networkd = Networkd(module)

    result = {'conn_name': networkd.conn_name, 'state': networkd.state}
    changed = False

    # check for issues
    if networkd.conn_name is None:
        networkd.module.fail_json(
            msg="Please specify a name for the connection")
    check_milliseconds_field_is_digit(networkd, "miimon")
    check_milliseconds_field_is_digit(networkd, "updelay")
    check_milliseconds_field_is_digit(networkd, "downdelay")
    check_milliseconds_field_is_digit(networkd, "arp_interval")

    try:
        if networkd.state == 'absent':
            # Simply check no files are associated with this conn_name
            print("Absent")
        elif networkd.state == 'present':

            if networkd.type in [
                    'ethernet',
                    'infiniband',
                    'bond-slave',
                    'vlan']:

                # Generate Network file
                network = networkd.generate_network()
                # Read current Network file if exist and compare if changes
                network_file = "/etc/systemd/network/" +\
                    networkd.conn_name + ".network"
                # Check if content is the same
                changed = not same_list_file(network, network_file)
                # Write configuration if changes detected
                if changed:
                    write_list_to_file(network, network_file, module.check_mode)

            if networkd.type in ['bond', 'vlan']:

                # Generate Netdev file
                netdev = networkd.generate_netdev()
                # Read current Network file if exist and compare if changes
                netdev_file = "/etc/systemd/network/" +\
                    networkd.conn_name + ".netdev"
                # Check if content is the same
                changed = not same_list_file(netdev, netdev_file)
                # Write configuration if changes detected
                if changed:
                    write_list_to_file(netdev, netdev_file, module.check_mode)

# Post actions
# if changed == 1:
    # stdout, stderr = subprocess.Popen("networkctl reload",
    # stdout=os.subprocess.PIPE, stderr=subprocess.STDOUT,
    # shell=True).communicate()
    # stdout, stderr = subprocess.Popen("networkctl reconfigure " +
    # networkd.conn_name, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    # shell=True).communicate()

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
