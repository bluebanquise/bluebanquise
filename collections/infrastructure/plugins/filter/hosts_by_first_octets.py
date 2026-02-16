#!/usr/bin/python
from collections import defaultdict
from ansible.errors import AnsibleFilterError

class FilterModule(object):
    def filters(self):
        return {'hosts_by_first_octets': self.hosts_by_first_octets}

    def hosts_by_first_octets(self, hostvars, hosts_list, networks):
        ip_networks = defaultdict(list)
        _rsplit = str.rsplit 

        # #########################################
        # ############## Hosts & BMC

        for hostname in hosts_list:
            try:
                hv = hostvars.get(hostname, {})
                
                # Process Network Interfaces
                alias = hv.get("alias")
                is_first_nic = True
                for nic in hv.get("network_interfaces", []):
                    ip4 = nic.get("ip4")
                    net_name = nic.get("network")
                    
                    if ip4 and net_name:
                        ip_net, ip_host = _rsplit(ip4, '.', 1)
                        ip_networks[ip_net].append({
                            "hostname": hostname,
                            "network": net_name,
                            "ip4": ip4,
                            "ip_host": ip_host
                        })
                        
                        if is_first_nic and alias:
                            ip_networks[ip_net].append({
                                "hostname": alias,
                                "network": net_name,
                                "ip4": ip4,
                                "ip_host": ip_host
                            })
                            is_first_nic = False

                # Process BMC
                bmc = hv.get('bmc')
                if bmc:
                    ip4 = bmc.get("ip4")
                    net_name = bmc.get("network")
                    bmc_name = bmc.get("name")
                    if ip4 and net_name and bmc_name:
                        ip_net, ip_host = _rsplit(ip4, '.', 1)
                        ip_networks[ip_net].append({
                            "hostname": bmc_name,
                            "network": net_name,
                            "ip4": ip4,
                            "ip_host": ip_host
                        })

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
                            ip_networks[ip_net].append({
                                "hostname": svc_host,
                                "network": net_name,
                                "ip4": ip4,
                                "ip_host": ip_host
                            })
            
            except ValueError:
                raise AnsibleFilterError(
                    f"Invalid format in network services for '{net_name}'. "
                    f"Check services definitions, especially 'ip4'."
                )
            except Exception as e:
                raise AnsibleFilterError(f"Error processing network '{net_name}': {str(e)}")
        
        return dict(ip_networks)