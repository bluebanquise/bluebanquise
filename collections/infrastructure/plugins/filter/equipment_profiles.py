from ansible.errors import AnsibleFilterError


class FilterModule(object):
    def filters(self):
        return {
            'equipment_profiles': self.equipment_profiles
        }

    def equipment_profiles(self, hostvars, hosts_list, groups, hw_prefix='hw', os_prefix='os'):

        try:
            bequipments = {}
            # Cache to store variable sets extracted from group leaders
            # This is critical for performance with 1000+ hosts
            group_vars_cache = {}

            # Pre-calculate prefixes to save string operations in the loop
            hw_p = f"{hw_prefix}_"
            os_p = f"{os_prefix}_"

            for host in hosts_list:
                try:
                    h_vars = hostvars.get(host)
                    if h_vars is None:
                        continue  # Skip hosts that aren't reachable/defined in hostvars

                    group_names = h_vars.get('group_names', [])

                    # 1. Identify HW and OS groups (Optimized search)
                    host_hw = None
                    host_os = None
                    for g in group_names:
                        if not host_hw and g.startswith(hw_p):
                            host_hw = g
                        elif not host_os and g.startswith(os_p):
                            host_os = g
                        if host_hw and host_os:
                            break

                    # 2. Skip logic: If the host doesn't have BOTH, we ignore it
                    if not host_hw or not host_os:
                        continue

                    # 3. Handle the combination
                    ep_key = f"{host_hw}_with_{host_os}"

                    if ep_key not in bequipments:
                        # Extract HW vars (Check cache first)
                        if host_hw not in group_vars_cache:
                            leader = groups.get(host_hw, [None])[0]
                            l_vars = hostvars.get(leader, {}) if leader else {}
                            group_vars_cache[host_hw] = {k: v for k, v in l_vars.items() if k.startswith(hw_p)}

                        # Extract OS vars (Check cache first)
                        if host_os not in group_vars_cache:
                            leader = groups.get(host_os, [None])[0]
                            l_vars = hostvars.get(leader, {}) if leader else {}
                            group_vars_cache[host_os] = {k: v for k, v in l_vars.items() if k.startswith(os_p)}

                        bequipments[ep_key] = {
                            'nodes': [],
                            'hw': group_vars_cache[host_hw],
                            'os': group_vars_cache[host_os],
                            'type': h_vars.get('hw_equipment_type')
                        }

                    # 4. Append current host
                    bequipments[ep_key]['nodes'].append(host)

                except Exception as e:
                    # Specific error for an individual host processing failure
                    raise AnsibleFilterError(f"Error processing host '{host}': {str(e)}")

            return bequipments

        except Exception as e:
            # Catch-all for general logic failures
            raise AnsibleFilterError(f"Critical failure in equipment_profiles filter: {str(e)}")
