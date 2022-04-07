Advanced DHCP server
--------------------

Description
^^^^^^^^^^^

This role provides an advanced dhcp server combined with the iPXE roms of
BlueBanquise.
Features like shared_network, opt82, opt61 or snp/snponly roms are provided here
for very specific configurations or needs.

Instructions
^^^^^^^^^^^^

Please read first documentation of the standard dhcp server role. Advanced dhcp
server provides same features than standard dhcp server role, but with more
options.

Dhcp will only take into account networks from the current iceberg, and with
naming related to administration network (by default iceX-Y).

Also, ensure dhcp is set to true for your network.

Finally, note that the following parameters can be set in the inventory, to
override default ones:

* advanced_dhcp_server_default_lease_time (default to 600)
* advanced_dhcp_server_max_lease_time (default to 7200)

Consider increasing the default values once your network is production ready.

Multiple entries
""""""""""""""""

It is possible to have multiple entries for an host interface in the
configuration.

For example, set a mac address and a dhcp_client_identifier this way:

.. code-block:: yaml

      hosts:
        c001:
          network_interfaces:
            - interface: eth0
              ip4: 10.10.3.1
              mac: 08:00:27:36:c0:ac
              dhcp_client_identifier: 00:40:1c
              network: ice1-1

This will create an entry related to mac address and one to dhcp client
identifier.

Shared network
""""""""""""""

It is possible to combine networks into shared-networks when multiple subnets
are on the same NIC, or when using opt82/option_match parameter.
To do so, add a variable in the network definition.

For example to add ice1-1 and ice1-2 into the same shared network, define them
this way:

Ice1-1:

.. code-block:: yaml

  networks:
    ice1-1:
      subnet: 10.10.0.0
      prefix: 16
      shared_network: wolf
      ...

And ice1-2:

.. code-block:: yaml

  networks:
    ice1-2:
      subnet: 10.30.0.0
      prefix: 16
      shared_network: wolf
      ...

shared_network variable is optional and is simply ignored if not set.

opt 61 and opt 82
"""""""""""""""""

It is possible to use advanced dhcp features to identify an host. The following
parameters are available, for the host and its BMC:

- mac: identify based on MAC address. Same than standard dhcp server.
- dhcp_client_identifier: identify based on a pattern (string, etc) to recognize an host. Also known as option 61.
- host_identifier: identify based on an option (agent.circuit-id, agent.remote-id, etc) to recognize an host. Also known as option 82.
- match: identify based on multiple options in combination to recognize an host. Also known as option 82 with hack.

If using match, because this features is using a specific 'hack' in the dhcp
server, you **must** define this host in a shared network, even if this shared
network contains a single network (see this very well made page for more
information: http://www.miquels.cistron.nl/isc-dhcpd/).

Add dhcp options
""""""""""""""""

It is possible to add specific dhcp options to an host interface, which can be
useful in some specific cases.
This is achieved adding a list named dhcp_options inside the NIC definition.

For example:

.. code-block:: yaml

      hosts:
        c001:
          network_interfaces:
            - interface: eth0
              ip4: 10.10.3.1
              dhcp_client_identifier: 00:40:1c
              dhcp_options:
                - pxelinux.magic code 208 = string
                - pxelinux.configfile code 209 = text
              network: ice1-1

Use patterns
""""""""""""

It is possible, for advanced dhcp patterns, to enable capability to use external
macros to write hosts configuration into the dhcp configuration.

Then, adding a pattern variable to an host NIC definition will trigger the
associated macro.

For example:

.. code-block:: yaml

      hosts:
        c001:
          network_interfaces:
            - interface: eth0
              ip4: 10.10.3.1
              mac: 08:00:27:36:c0:ac
              network: ice1-1
              pattern: my_equipment_x

Will trigger macro called *my_equipment_x*.

To enable this feature, define *advanced_dhcp_server_enable_patterns* to
**true**. The role will now look for a file called *patterns.j2* in files folder
of the role (and fail if the file do not exist).

patterns.j2 file should contains the macro to be used, named like the pattern
targeted in the node definition.
Each macro have 3 input, in this order:

1. hostname of the host to be written
2. dictionary of the nic to be written
3. filename of the host to be written

An example of macro would be, for the pattern *my_equipment_x* defined above:

.. code-block:: text

{% macro my_equipment_x(macro_host, macro_nic, macro_filename) %}
host {{ macro_host }} {
  option host-name "{{macro_host}}";
    hardware ethernet {{macro_nic.mac}};
    fixed-address {{macro_nic.ip4}};
    filename "{{macro_filename}}";
}
{% endmacro %}

Changelog
^^^^^^^^^

* 1.1.1: Allows usage of time_ip list. Thiago Cardozo <thiago.cardozo@yahoo.com.br>
* 1.1.0: Update to pip Ansible. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.6: Prevent unsorted ranges. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.5: Improve performances. Add dhcp_options and patterns features. Allow multiple entries per host. Benoit Leveugle <benoit.leveugle@atos.net>
* 1.0.4: Update to new network_interfaces syntax. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.3: Added support of multiple DNS servers. Bruno Travouillon <devel@travouillon.fr>
* 1.0.2: Added Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
