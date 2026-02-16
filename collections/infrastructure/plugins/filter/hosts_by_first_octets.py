#!/usr/bin/python
from collections import defaultdict
from ansible.errors import AnsibleFilterError

class FilterModule(object):
    def filters(self):
        return {'hosts_by_first_octets': self.hosts_by_first_octets}

    def hosts_by_first_octets(self, hostvars, hosts_list, networks):

        reverse_data = defaultdict(list)  # List of ip prefixes for Reverse DNS
        forward_data = []  # List of primary entries for Forward DNS
        _rsplit = str.rsplit  # Nice optim

        # #########################################
        # ############## Hosts & BMC

        for hostname in hosts_list:
            try:
                hv = hostvars.get(hostname, {})
                alias = hv.get("alias")

                # Process Network Interfaces
                for index, nic in enumerate(hv.get("network_interfaces", [])):
                    ip4 = nic.get("ip4")
                    net_name = nic.get("network")
                    
                    if ip4 and net_name:
                        ip_net, ip_host = _rsplit(ip4, '.', 1)
                        entry = {
                            "hostname": hostname,
                            "network": net_name,
                            "ip4": ip4,
                            "ip_host": ip_host
                        }
                        
                        # 1. Everything goes to REVERSE
                        reverse_data[ip_net].append(entry)

                        # 2. Only the FIRST nic goes to FORWARD
                        if index == 0:
                            forward_data.append(entry)
                            if alias:
                                entry = {
                                    "hostname": alias,
                                    "network": net_name,
                                    "ip4": ip4,
                                    "ip_host": ip_host
                                }
                                reverse_data[ip_net].append(entry)
                                forward_data.append(entry)    

                # Process BMC
                bmc = hv.get('bmc')
                if bmc:
                    ip4 = bmc.get("ip4")
                    net_name = bmc.get("network")
                    bmc_name = bmc.get("name")
                    if ip4 and net_name and bmc_name:
                        ip_net, ip_host = _rsplit(ip4, '.', 1)
                        entry = {
                            "hostname": bmc_name,
                            "network": net_name,
                            "ip4": ip4,
                            "ip_host": ip_host
                        }
                        reverse_data[ip_net].append(entry)
                        forward_data.append(entry)

            except ValueError:
                raise AnsibleFilterError(
                    f"Invalid format found for host '{hostname}'. "
                    f"Check host values, especially 'ip4'."
                )
            except Exception as e:
                raise AnsibleFilterError(f"Error processing host '{hostname}': {str(e)}")

        # #########################################
        # ############## Network services

        for net_name, net_data in networks.items():
            try:
                services = net_data.get('services', {})
                for svc_name, service_ips in services.items():
                    for item in service_ips:
                        ip4 = item.get('ip4')
                        svc_host = item.get('hostname')
                        if ip4 and svc_host:
                            ip_net, ip_host = _rsplit(ip4, '.', 1)
                            entry = {
                                "hostname": svc_host,
                                "network": net_name,
                                "ip4": ip4,
                                "ip_host": ip_host
                            }
                            reverse_data[ip_net].append(entry)
                            forward_data.append(entry)
            
            except ValueError:
                raise AnsibleFilterError(
                    f"Invalid format in network services for '{net_name}'. "
                    f"Check services definitions, especially 'ip4'."
                )
            except Exception as e:
                raise AnsibleFilterError(f"Error processing network '{net_name}': {str(e)}")
        
        return {
            "forward": forward_data,
            "reverse": dict(reverse_data)
          }