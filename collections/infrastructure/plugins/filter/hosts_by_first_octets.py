#!/usr/bin/python
from collections import defaultdict
from ansible.errors import AnsibleFilterError


class FilterModule(object):
    def filters(self):
        return {'hosts_by_first_octets': self.hosts_by_first_octets}

    def hosts_by_first_octets(self, hostvars, hosts_list, networks):
        # Nested structure: reverse_data[prefix]['base' or 'extended']
        reverse_data = defaultdict(lambda: {'base': [], 'extended': []})
        forward_data = {'base': [], 'extended': []}
        _rsplit = str.rsplit

        for hostname in hosts_list:
            try:
                hv = hostvars.get(hostname, {})
                alias = hv.get("alias")

                # --- Process Network Interfaces ---
                for index, nic in enumerate(hv.get("network_interfaces", []) or []):
                    ip4 = nic.get("ip4")
                    net_name = nic.get("network")

                    if ip4 and net_name:
                        ip_net, ip_host = _rsplit(ip4, '.', 1)

                        # 1. THE FIRST INTERFACE (Base Identity)
                        if index == 0:
                            entry = {"hostname": hostname, "network": net_name, "ip4": ip4, "ip_host": ip_host}
                            forward_data['base'].append(entry)
                            reverse_data[ip_net]['base'].append(entry)

                            if alias:
                                alias_entry = {"hostname": alias, "network": net_name, "ip4": ip4, "ip_host": ip_host}
                                forward_data['base'].append(alias_entry)

                        # 2. EXTENDED NAMING (Every interface gets a hostname-network record)
                        ext_name = f"{hostname}-{net_name}"
                        ext_entry = {"hostname": ext_name, "network": net_name, "ip4": ip4, "ip_host": ip_host}
                        forward_data['extended'].append(ext_entry)

                        # If it wasn't the first NIC, its PTR belongs in 'extended'
                        if index > 0:
                            reverse_data[ip_net]['extended'].append(ext_entry)

                # --- Process BMC ---
                bmc = hv.get('bmc')
                if bmc:
                    ip4, net_name, bmc_name = bmc.get("ip4"), bmc.get("network"), bmc.get("name")
                    if ip4 and net_name and bmc_name:
                        ip_net, ip_host = _rsplit(ip4, '.', 1)
                        entry = {"hostname": bmc_name, "network": net_name, "ip4": ip4, "ip_host": ip_host}
                        # BMCs are usually considered 'base' identity
                        forward_data['base'].append(entry)
                        reverse_data[ip_net]['base'].append(entry)

            except Exception as e:
                raise AnsibleFilterError(f"Error processing host '{hostname}': {str(e)}")

        # --- Process Network Services ---
        for net_name, net_data in networks.items():
            try:
                services = net_data.get('services', {})
                for svc_name, service_ips in services.items():
                    for item in service_ips:
                        ip4, svc_host = item.get('ip4'), item.get('hostname')
                        if ip4 and svc_host:
                            ip_net, ip_host = _rsplit(ip4, '.', 1)
                            entry = {"hostname": svc_host, "network": net_name, "ip4": ip4, "ip_host": ip_host}
                            # Services are typically base records
                            forward_data['base'].append(entry)
                            # reverse_data[ip_net]['base'].append(entry) # Do not add services in reverse
            except Exception as e:
                raise AnsibleFilterError(f"Error processing network '{net_name}': {str(e)}")

        return {
            "forward": forward_data,
            "reverse": dict(reverse_data)
        }
