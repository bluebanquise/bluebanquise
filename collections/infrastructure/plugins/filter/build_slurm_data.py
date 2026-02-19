from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display

display = Display()

class FilterModule(object):
    def filters(self):
        return {
            'build_slurm_data': self.build_slurm_data
        }

    def build_slurm_data(self, hostvars, slurm_partitions_list, groups, hw_prefix='hw'):
        try:
            unique_all_nodes = set()
            partitions_output = {}
            nodes_packs = {}
            missing_hw_nodes = []
            
            hw_p = f"{hw_prefix}_"

            # 1. Map partitions and collect all involved nodes
            for part in slurm_partitions_list:
                p_name = part.get('partition_name')
                c_groups = part.get('computes_groups', [])
                
                part_nodes_set = set()
                for g_name in c_groups:
                    g_members = groups.get(g_name, [])
                    part_nodes_set.update(g_members)
                
                partitions_output[p_name] = sorted(list(part_nodes_set))
                unique_all_nodes.update(part_nodes_set)

            # 2. Pack unique nodes and validate hw_specs
            for node in unique_all_nodes:
                n_vars = hostvars.get(node)
                
                if n_vars is None:
                    missing_hw_nodes.append(node)
                    continue

                # Find the hardware group
                node_groups = n_vars.get('group_names', [])
                hw_group = next((g for g in node_groups if g.startswith(hw_p)), None)

                if not hw_group:
                    missing_hw_nodes.append(node)
                    continue

                if hw_group not in nodes_packs:
                    # VALIDATION: Check if hw_specs exists
                    # .get() returns None if the key is missing
                    specs = n_vars.get('hw_specs')
                    
                    if specs is None:
                        raise AnsibleFilterError(
                            f"Configuration Error: The hardware group '{hw_group}' is missing the mandatory 'hw_specs' key. "
                            f"(Detected on host: {node})"
                        )

                    nodes_packs[hw_group] = {
                        'nodes': [],
                        'hw_specs': specs
                    }
                
                nodes_packs[hw_group]['nodes'].append(node)

            # 3. Handle Warnings for missing HW group membership
            if missing_hw_nodes:
                display.warning(
                    f"The following nodes were found in slurm_partitions_list but do not "
                    f"belong to any '{hw_p}' group and will be excluded from NodesPacks: {', '.join(missing_hw_nodes)}"
                )

            return {
                'NodesPacks': nodes_packs,
                'Partitions': partitions_output
            }

        except AnsibleFilterError:
            # Re-raise AnsibleFilterErrors directly to preserve our custom message
            raise
        except Exception as e:
            # Catch unexpected Python exceptions
            raise AnsibleFilterError(f"Unexpected error in build_slurm_data filter: {str(e)}")