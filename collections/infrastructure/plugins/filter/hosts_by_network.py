class FilterModule(object):
    def filters(self):
        return {
            "hosts_by_network": self.hosts_by_network
        }

    def hosts_by_network(self, hostvars, host_list):
        """
        Build a mapping:
            network_name → list of { host, nic, type }

        So something like that:

            netA:
                - { host: "node1",     nic: {...}, type: "host" }
                - { host: "node1-bmc", nic: {...}, type: "bmc" }
                - { host: "node2",     nic: {...}, type: "host" }
            netB:
                - { host: "node3",     nic: {...}, type: "host" }

        Includes:
            - host NICs
            - BMC NICs

        Onjective is to go fast, all these loops in templates over networks then
        over hosts takes a lot of ressoucres when in Jinja2.

        """

        result = {}

        for hostname in host_list:
            hv = hostvars.get(hostname, {})

            # ----------------------------
            # Host NICs
            # ----------------------------
            for nic in (hv.get("network_interfaces", []) or []):
                net = nic.get("network")
                if not net:
                    continue

                entry = {
                    "host": hostname,
                    "nic": nic,
                    "type": "host"
                }

                result.setdefault(net, []).append(entry)

            # ----------------------------
            # BMC
            # ----------------------------
            bmc = hv.get("bmc")
            if bmc:
                net = bmc.get("network")
                if net:
                    entry = {
                        "host": bmc.get("name"),
                        "nic": bmc,
                        "type": "bmc"
                    }
                    result.setdefault(net, []).append(entry)

        return result
