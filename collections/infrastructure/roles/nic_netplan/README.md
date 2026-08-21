# BlueBanquise NIC Role (Netplan Backend)

This role configures network interfaces using **Netplan** as the declarative backend, replacing the legacy imperative `NetworkManager` (nmcli) approach. It maintains backward compatibility with the existing BlueBanquise inventory structure while leveraging robust YAML generation.

## Implementation Decisions

1. **Dictionary-Based YAML Generation (`to_nice_yaml`)**
   Instead of manually writing raw YAML loops and managing indentation/quotes, the Jinja2 template constructs a native Python dictionary in memory. It then uses the `to_nice_yaml` filter to dump the configuration. This guarantees:
   * **Strict Type Safety:** MTUs and metrics are correctly cast as integers, IPs as strings, and DHCP flags as booleans.
   * **Formatting Reliability:** Eliminates trailing comma errors and indentation mismatch issues inherent to Jinja2 `for` loops.

2. **Routing Modernization**
   Netplan has deprecated the top-level `gateway4` and `gateway6` directives. The template automatically translates these legacy BlueBanquise variables into standard `routes` (e.g., `{to: default, via: <IP>}`) and natively attaches `route_metric4`/`route_metric6` or `metric` directly to these routes.

3. **InfiniBand Isolation (``02-bluebanquise_ipoib.yaml)**
   Because Netplan's native `infiniband` renderer is experimental and Udev MAC matching often breaks IPoIB driver bindings, InfiniBand interfaces are skipped in the primary template. Instead, they are rendered in a secondary configuration file treated strictly as standard `ethernets` with **only** IP configurations applied (no `match` or `set-name` directives).

## Variable Structure Restrictions & Edge Cases

To ensure successful Netplan generation, the following structural rules apply to your inventory:

* **MAC Address Matching is for Physical NICs Only:** 
  In Netplan (via `systemd-networkd`), Udev `match: {macaddress: ...}` directives are only valid for physical hardware. If you define `type: vlan`, `bond`, or `bridge`, the template will deliberately ignore the `mac` variable to prevent fatal Netplan parsing errors.
* **Custom Routing Structure (`routes4` / `routes6`):**
  Custom routes must be provided as lists of space-separated strings following the pattern `"DESTINATION VIA [METRIC]"`. The template dynamically parses these via `.split()`.
  * *Example:* `- "10.11.0.0/24 10.10.0.2 300"`
* **Virtual Interface Linkages:**
  * **VLANs:** Must define `vlan_id` and either `vlandev` or `link` to bind to a physical parent.
  * **Bonds:** The template natively merges legacy naming (`bond_slaves`, `slaves`, `bridge_ports`, `ports`) into Netplan's strict `interfaces: []` list. Also bond-slaves have be be strictly declared after bond master as usual.
* **DNS Nameservers:**
  Lists provided in `nameservers` or `dns4` are automatically nested under Netplan's required `nameservers: { addresses: [], search: [] }` format.


## TODO
- Integrate with nic role
- Review better usage of j2 variables instead of inventory looping


## Not implemented
- no IPv6 support
- no bridge type support
