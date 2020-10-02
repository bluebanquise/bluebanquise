#!/usr/bin/env python3

import sys
import yaml


# Indent list with PyYAML
# From https://web.archive.org/web/20170903201521/https://pyyaml.org/ticket/64#comment:5
class MyDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

    # Super neat hack to preserve the mapping key order.
    # See https://stackoverflow.com/a/52621703/1497385
    def represent_dict_preserve_order(self, data):
        return self.represent_dict(data.items())


# Search and convert network_interfaces from dict to list
#
def search_network_interfaces(dictionary):
    for key in dictionary.keys():
        if key == 'network_interfaces':
            netinf = list()
            for interface in dictionary[key]:

                # Create new dict with interface key
                newdict = {'interface': interface}

                # Add existing dict to this new dict
                newdict.update(dictionary[key][interface])

                # Add new dict as new element of new network_interfaces list
                netinf.append(newdict)

            # Overwrite
            dictionary[key] = netinf

        elif key != 'bmc':
            search_network_interfaces(dictionary[key])

    return dictionary


def usage(command):
    print(f"Usage: {command} /etc/bluebanquise/inventory/cluster/nodes/file.yml")


def main():

    MyDumper.add_representer(dict, MyDumper.represent_dict_preserve_order)

    if len(sys.argv) != 2:
        usage(sys.argv[0])
        exit(1)

    hostsfile = sys.argv[1]
    outfile = hostsfile + '-bluebanquise-1.3'

    with open(hostsfile, 'r') as fd:
        try:
            inventory = yaml.load(fd, Loader=yaml.SafeLoader)
            new_inventory = search_network_interfaces(inventory)
        except yaml.YAMLError as exc:
            print(exc)

    with open(outfile, 'w') as fd:
        fd.write(yaml.dump(new_inventory, Dumper=MyDumper, default_flow_style=False))

    print(f'''Next steps:
      $ diff -u {hostsfile} {outfile} | less
      $ mv {outfile} {hostsfile}''')


if __name__ == "__main__":
    main()
