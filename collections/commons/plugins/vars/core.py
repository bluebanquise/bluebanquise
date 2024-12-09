from ansible.plugins.vars import BaseVarsPlugin

class VarsModule(BaseVarsPlugin):

    def get_vars(self, loader, path, entities, cache=True):

        super(VarsModule, self).get_vars(loader, path, entities)
        data = {
            'bb_core_iceberg_naming': 'iceberg',
            'bb_core_equipment_naming': 'equipment',
            'bb_core_os_naming': 'os',
            'bb_core_hw_naming': 'hw',
            'bb_core_management_networks_naming': 'net',
            'bb_core_master_groups_naming': 'fn',
            'bb_core_managements_group_name': 'fn_management',
            'bb_core_herd_naming': 'herd',

            #############################################################
            ############ J2_ LOGIC
            #####

            ### Groups
            # List of master groups.
            'j2_master_groups_list': "{{ groups | select('match','^'+bb_core_master_groups_naming+'_.*') | list | unique | sort }}",
            # List of equipment groups.
            # Deprecated
            'j2_equipment_groups_list': "{{ (groups | select('match','^'+bb_core_equipment_naming+'_.*') | list | length | int > 0) | ternary(groups | select('match','^'+bb_core_equipment_naming+'_.*') | list | unique | sort, ['all']) }}",
            # Host current equipment group.
            # Deprecated
            'j2_node_equipment': "{{ (groups | select('match','^'+bb_core_equipment_naming+'_.*') | list | length | int > 0) | ternary(group_names | select('match','^'+bb_core_equipment_naming+'_.*') | list | unique | sort | first | default('') | replace(bb_core_equipment_naming + '_',''), 'all') }}",

            ## Equipments
            # Generate the list of nodes with their associated os and hw groups as values
            # Example:
            #   c001:
            #     hw: hw_supermicro_XXX
            #     os: os_ubuntu_22.04_gpu
            #     ep: hw_supermicro_XXX_with_os_ubuntu_22.04_gpu
            # This is a transverse j2 (j2_bb_), used as a cache fact
            'j2_bb_nodes_profiles': """{%- set bnodes_profiles = {} -%}
{%- for host in j2_hosts_range -%}
  {%- set host_hw = (hostvars[host]['group_names'] | select('match','^'+bb_core_hw_naming+'_.*') | list | unique | sort | first) | default(none, true) -%}
  {%- set host_os = (hostvars[host]['group_names'] | select('match','^'+bb_core_os_naming+'_.*') | list | unique | sort | first) | default(none, true) -%}
  {%- if host_hw is not none and host_os is not none -%}
    {%- set host_ep = (host_hw + '_with_' + host_os) -%}
  {%- else -%}
    {%- set host_ep = none -%}
  {%- endif -%}
  {%- do bnodes_profiles.update({host: {'hw': host_hw, 'os': host_os, 'ep': host_ep}}) -%}
{%- endfor -%}
{{ bnodes_profiles }}""",

            # Generate the equipments that are existing combination of hardware and os profiles
            # and store the list of associated nodes inside these equipments. Nodes without both hw_ and os_ are ignored.
            # This dict also contains all os_ and hw_ values for this equipment profile ep.
            # This is based on the BlueBanquise rule that os_ and hw_ values MUST be set at these groups level only.
            # Example:
            #   hw_supermicro_XXX_with_os_ubuntu_22.04_gpu: # -> can easily deduce hw and os group names from that
            #     nodes:
            #       - c001
            #       - c002
            #     hw:
            #       hw_equipment_type: server
            #       hw_console: ...
            #     os:
            #       os_operating_system: ...
            # This is a transverse j2 (j2_bb_), used as a cache fact
            # It is expected that the dependency fact be bb_nodes_profiles
            # If the dependency fact was not already cached, it will not be used but that implies longuer calculations
            # generic equipment does not inherit any hw or os values, so should rely on the roles default ones
            'j2_bb_equipments': """{%- set bequipments = {} -%}
{%- if bb_nodes_profiles is defined -%}
  {%- set bnodes_profiles = bb_nodes_profiles -%}
{%- else -%}{# Calculate since not cached #}
  {%- set bnodes_profiles = j2_bb_nodes_profiles -%}
{%- endif -%}
{%- for host, host_keys in bnodes_profiles.items() -%}
  {%- if host_keys['ep'] is not none -%}
    {%- if host_keys['ep'] not in bequipments -%}
      {%- set os_settings = {} -%}
      {%- set first_host_of_group_vars = hostvars[groups[host_keys['os']][0]] -%}
      {%- for osvalue in (first_host_of_group_vars | select('match','^os_.*')) -%}
        {%- do os_settings.update({osvalue: first_host_of_group_vars[osvalue]}) -%}
      {%- endfor -%}
      {%- set hw_settings = {} -%}
      {%- set first_host_of_group_vars = hostvars[groups[host_keys['hw']][0]] -%}
      {%- for hwvalue in (first_host_of_group_vars | select('match','^hw.*')) -%}
        {%- do hw_settings.update({hwvalue: first_host_of_group_vars[hwvalue]}) -%}
      {%- endfor -%}
      {%- do bequipments.update({host_keys['ep']: {'nodes': [], 'hw': hw_settings, 'os': os_settings}}) -%}
    {%- endif -%}
{{ bequipments[host_keys['ep']]['nodes'].append(host) }}
  {%- else -%}
    {%- if 'generic' not in bequipments -%}
      {%- do bequipments.update({'generic': {'nodes': [], 'hw': {}, 'os': {}}}) -%}
    {%- endif -%}
{{ bequipments['generic']['nodes'].append(host) }}
  {%- endif -%}
{%- endfor -%}
{{ bequipments }}""",

            ### Network

            ## Resolution
            # Resolution network. The network on which host can be ping by direct name. (ex: ping c001).
            'j2_node_main_resolution_network': "{{ network_interfaces[0].network | default(none) }}",
            # Resolution address.
            'j2_node_main_resolution_address': "{{ (network_interfaces[0].ip4 | default('')).split('/')[0] | default(none) }}",

            ## Main network
            # The network used by Ansible to deploy configuration (related to ssh).
            # Also the network used by the host to get services ip.
            'j2_node_main_network': "{{ network_interfaces | default([]) | selectattr('network','defined') | selectattr('interface','defined') | selectattr('ip4','defined') |selectattr('network','match','^'+j2_current_iceberg_network+'-[a-zA-Z0-9]+') | map(attribute='network') | list | first | default(none) }}",
            # Main network interface.
            'j2_node_main_network_interface': "{{ network_interfaces[j2_node_main_network].interface | default(none) }}",
            # Main address, same concept.
            'j2_node_main_address': "{{ network_interfaces[j2_node_main_network].ip4 | default(none) }}",

            # Generate the nodes list, as a cache for network_interfaces
            # Example:
            # c001:
            #     alias: null
            #     bmc:
            #         ip4: 10.10.103.1
            #         mac: 2a:2b:3c:2d:5e:6f
            #         name: bc001
            #         network: net-admin
            #     current_iceberg: iceberg1
            #     global_alias: null
            #     icebergs_main_network_dict: null
            #     network_interfaces:
            #     - interface: enp1s0
            #         ip4: 10.10.3.1
            #         mac: 1a:2b:3c:4d:5e:9f
            #         network: net-admin
            #     node_main_resolution_address: 10.10.3.1
            # This is a transverse j2 (j2_bb_), used as a cache fact
            'j2_bb_nodes': """{%- set bnodes = {} -%}
{% set mgt = groups['fn_management'] %}
{%- for host in j2_hosts_range -%}
  {% set hostvars_buffer = hostvars[host] %}
  {%- if host in mgt -%}
    {%- do bnodes.update({
    host: {
      'network_interfaces': hostvars_buffer['network_interfaces'] | default(none, true),
      'node_main_resolution_address': hostvars_buffer['j2_node_main_resolution_address'] | default(none, true),
      'current_iceberg': hostvars_buffer['j2_current_iceberg'] | default(none, true),
      'current_herd': hostvars_buffer['j2_current_herd'] | default(none, true),
      'icebergs_main_network_dict': hostvars_buffer['j2_icebergs_main_network_dict'] | default({}, true),
      'bmc': hostvars_buffer['bmc'] | default(none, true),
      'alias': hostvars_buffer['alias'] | default(none, true),
      'global_alias': hostvars_buffer['alias'] | default(none, true)
    }
  }) -%}
  {%- else -%}
    {%- do bnodes.update({
    host: {
      'network_interfaces': hostvars_buffer['network_interfaces'] | default(none, true),
      'node_main_resolution_address': hostvars_buffer['j2_node_main_resolution_address'] | default(none, true),
      'current_iceberg': hostvars_buffer['j2_current_iceberg'] | default(none, true),
      'current_herd': hostvars_buffer['j2_current_herd'] | default(none, true),
      'icebergs_main_network_dict': {},
      'bmc': hostvars_buffer['bmc'] | default(none, true),
      'alias': hostvars_buffer['alias'] | default(none, true),
      'global_alias': hostvars_buffer['alias'] | default(none, true)
    }
  }) -%}
  {%- endif -%}
{%- endfor -%}
{{ bnodes }}""",

            ## Other
            # List of management networks.
            'j2_management_networks': "{{ networks | select('match','^'+j2_current_iceberg_network+'-[a-zA-Z0-9]+') | list | unique | sort }}",

            ### Icebergs engine file
            # List all icebergs
            'j2_icebergs_groups_list': "{{ groups | select('match','^'+bb_core_iceberg_naming+'[a-zA-Z0-9]+') | list }}",
            # Get total number of icebergs
            'j2_number_of_icebergs': "{{ groups | select('match','^'+bb_core_iceberg_naming+'[a-zA-Z0-9]+') | list | length }}",
            # Grab current iceberg group
            'j2_current_iceberg': "{{ bb_icebergs_system | default(false) | ternary( group_names | select('match','^'+bb_core_iceberg_naming+'[a-zA-Z0-9]+') | list | unique | sort | first | default(bb_core_iceberg_naming+'1'), bb_core_iceberg_naming+'1') }}",
            # Grab current iceberg number
            'j2_current_iceberg_number': "{{ j2_current_iceberg | replace(bb_core_iceberg_naming,' ') | trim }}",
            # Grab current iceberg networks pattern
            'j2_current_iceberg_network': "{{ bb_icebergs_system | default(false) | ternary(bb_core_management_networks_naming + (j2_current_iceberg_number | string), bb_core_management_networks_naming) }}",
            # Generate list of managements connected to this iceberg from sub icebergs
            'j2_iceberg_sub_managements_members': "{% set range = [] %}{% for host in (groups[bb_core_managements_group_name] | default([])) %}{% if (hostvars[host]['bb_iceberg_master'] | default(none))  == j2_current_iceberg %}{{ range.append(host) }}{% endif %}{% endfor %}{{ range }}",
            # Generate range of hosts to include in current configurations
            'j2_hosts_range': "{{ ((bb_icebergs_system | default(false)) == true and (bb_iceberg_hosts_range | default('all')) == 'iceberg') | ternary( j2_iceberg_sub_managements_members + groups[j2_current_iceberg] | default([]), groups['all']) }}",
            # Generate a dict that contains host main network for each iceberg
            'j2_icebergs_main_network_dict': "{{ '{' }}{% for iceberg in (j2_icebergs_groups_list | default([])) %}{% if not loop.first %},{% endif %}'{{ iceberg }}':'{{ network_interfaces | default([]) | selectattr('network', 'defined') | selectattr('network', 'match', '^'+(bb_icebergs_system | default(false) | ternary(bb_core_management_networks_naming + (iceberg | replace(bb_core_iceberg_naming, ' ') | trim | string), bb_core_management_networks_naming) )+'-[a-zA-Z0-9]+') | map(attribute='network') | list | first | default(none) }}'{% endfor %}{{ '}' }}",
        }
        return data
    
