Snmp_exporter
=============

The snmp_exporter can be found here:
https://github.com/prometheus/snmp_exporter

By default, the snmp_exorter runs under the port 9116.

This exporter, along with the ipmi exporter, is a little special, as it executes
snmp commands on the targets. So we can get the metrics of all the targets with
the exporter running locally on our management server.

To access the metrics, do:

  curl 'http://localhost:9116/snmp?target=switch-001'

.. note::

  here, the request is http://<ip address of where the exporter is located>/snmp?target=<ip address of the switch that we want the metrics from>

Otherwise we can  access it directly in a browser. However, using curl can be
handy, because you can grep the output, and do other nice things with it.

You should get something like this:

.. code-block:: text

  # HELP ifAdminStatus The desired state of the interface - 1.3.6.1.2.1.2.2.1.7
  # TYPE ifAdminStatus gauge
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="1",ifName="Gi0/0"} 2
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="10",ifName="Gi1/0/3"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="11",ifName="Gi1/0/4"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="12",ifName="Gi1/0/5"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="13",ifName="Gi1/0/6"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="2",ifName="Nu0"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="20",ifName="Gi1/0/13"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="27",ifName="Gi1/0/20"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="29",ifName="Gi1/0/22"} 1
  ifAdminStatus{ifAlias="",ifDescr="",ifIndex="3",ifName="VLAN-1"} 1

Snmp_exporter setup
-------------------

The setup of this exporter is a little tricky.

By default, we provide a configuration file for this exporter only for cisco
switches.

This is because snmp needs specific OIDS, in order to query the switches.
These OIDS can vary depending on the switch you use.

You can have a look at all OIDS available here:
https://cric.grenoble.cnrs.fr/Administrateurs/Outils/MIBS/

You can find this file under /etc/snmp_exporter/snmp.yml

It should look something like this::

.. code-block:: yaml

  if_mib:
    walk:
      - 1.3.6.1.2.1.2
      - 1.3.6.1.2.1.31.1.1
      - 1.3.6.1.4.1.25461.2.1.2.3.11.1.2
  get:
    - 1.3.6.1.2.1.1.3.0
  metrics:
    - name: sysUpTime
      oid: 1.3.6.1.2.1.1.3
      type: gauge
      help: The time (in hundredths of a second) since the network management portion of the system was last re-initialized. - 1.3.6.1.2.1.1.3
    - name: ifNumber
      oid: 1.3.6.1.2.1.2.1
      type: gauge
      help: The number of network interfaces (regardless of their current state) present on this system. - 1.3.6.1.2.1.2.1
    - name: ifIndex
      oid: 1.3.6.1.2.1.2.2.1.1
      type: gauge
      help: A unique value, greater than zero, for each interface - 1.3.6.1.2.1.2.2.1.1
      indexes:

If you have another switch you want to query, you can generate another file than
the one we provide.

By installing snmp_exporter, you should have a generator installed under
/usr/local/go/src/github.com/prometheus/snmp_exporter/generator

Here, you have a file, generator.yml that you have to change, according to what
you want.

By default, it looks like this:

.. code-block:: text

  modules:
  # Default IF-MIB interfaces table with ifIndex.
  if_mib:
    walk: [sysUpTime, interfaces,ifXTable]
    version: 1
    auth:
      community: cluster
    lookups:
      - source_indexes: [ifIndex]
        lookup: ifAlias
      - source_indexes: [ifIndex]
        lookup: ifDescr
      - source_indexes: [ifIndex]
        # Use OID to avoid conflict with Netscaler NS-ROOT-MIB.
        lookup: 1.3.6.1.2.1.31.1.1.1.1 # ifName
    overrides:
      ifAlias:
        ignore: true # Lookup metric
      ifDescr:
        ignore: true # Lookup metric
      ifName:
        ignore: true # Lookup metric
      ifType:
        type: EnumAsInfo

.. note:: Notice the auth section, by default, we setup the switches with the cluster community with no password required. See the switch setup section for more info.

You can tune it as you want, as long as you follow this syntax:

.. code-block:: text

  modules:
  module_name:  # The module name. You can have as many modules as you want.
    walk:       # List of OIDs to walk. Can also be SNMP object names or specific instances.
      - 1.3.6.1.2.1.2              # Same as "interfaces"
      - sysUpTime                  # Same as "1.3.6.1.2.1.1.3"
      - 1.3.6.1.2.1.31.1.1.1.6.40  # Instance of "ifHCInOctets" with index "40"

    version: 2  # SNMP version to use. Defaults to 2.
                # 1 will use GETNEXT, 2 and 3 use GETBULK.
    max_repetitions: 25  # How many objects to request with GET/GETBULK, defaults to 25.
                         # May need to be reduced for buggy devices.
    retries: 3   # How many times to retry a failed request, defaults to 3.
    timeout: 5s  # Timeout for each individual SNMP request, defaults to 5s.

    auth:
      # Community string is used with SNMP v1 and v2. Defaults to "public".
      community: public

      # v3 has different and more complex settings.
      # Which are required depends on the security_level.
      # The equivalent options on NetSNMP commands like snmpbulkwalk
      # and snmpget are also listed. See snmpcmd(1).
      username: user  # Required, no default. -u option to NetSNMP.
      security_level: noAuthNoPriv  # Defaults to noAuthNoPriv. -l option to NetSNMP.
                                    # Can be noAuthNoPriv, authNoPriv or authPriv.
      password: pass  # Has no default. Also known as authKey, -A option to NetSNMP.
                      # Required if security_level is authNoPriv or authPriv.
      auth_protocol: MD5  # MD5 or SHA, defaults to MD5. -a option to NetSNMP.
                          # Used if security_level is authNoPriv or authPriv.
      priv_protocol: DES  # DES or AES, defaults to DES. -x option to NetSNMP.
                          # Used if security_level is authPriv.
      priv_password: otherPass # Has no default. Also known as privKey, -X option to NetSNMP.
                               # Required if security_level is authPriv.
      context_name: context # Has no default. -n option to NetSNMP.
                            # Required if context is configured on the device.

    lookups:  # Optional list of lookups to perform.
              # The default for `keep_source_indexes` is false. Indexes must be unique for this option to be used.

      # If the index of a table is bsnDot11EssIndex, usually that'd be the label
      # on the resulting metrics from that table. Instead, use the index to
      # lookup the bsnDot11EssSsid table entry and create a bsnDot11EssSsid label
      # with that value.
      - source_indexes: [bsnDot11EssIndex]
        lookup: bsnDot11EssSsid
        drop_source_indexes: false  # If true, delete source index labels for this lookup.
                                    # This avoids label clutter when the new index is unique.

     overrides: # Allows for per-module overrides of bits of MIBs
       metricName:
         ignore: true # Drops the metric from the output.
         regex_extracts:
           Temp: # A new metric will be created appending this to the metricName to become metricNameTemp.
             - regex: '(.*)' # Regex to extract a value from the returned SNMP walks's value.
               value: '$1' # The result will be parsed as a float64, defaults to $1.
           Status:
             - regex: '.*Example'
               value: '1' # The first entry whose regex matches and whose value parses wins.
             - regex: '.*'
               value: '0'
         type: DisplayString # Override the metric type, possible types are:
                             #   gauge:   An integer with type gauge.
                             #   counter: An integer with type counter.
                             #   OctetString: A bit string, rendered as 0xff34.
                             #   DateAndTime: An RFC 2579 DateAndTime byte sequence. If the device has no time zone data, UTC is used.
                             #   DisplayString: An ASCII or UTF-8 string.
                             #   PhysAddress48: A 48 bit MAC address, rendered as 00:01:02:03:04:ff.
                             #   Float: A 32 bit floating-point value with type gauge.
                             #   Double: A 64 bit floating-point value with type gauge.
                             #   InetAddressIPv4: An IPv4 address, rendered as 1.2.3.4.
                             #   InetAddressIPv6: An IPv6 address, rendered as 0102:0304:0506:0708:090A:0B0C:0D0E:0F10.
                             #   InetAddress: An InetAddress per RFC 4001. Must be preceded by an InetAddressType.
                             #   InetAddressMissingSize: An InetAddress that violates section 4.1 of RFC 4001 by
                             #       not having the size in the index. Must be preceded by an InetAddressType.
                             #   EnumAsInfo: An enum for which a single timeseries is created. Good for constant values.
                             #   EnumAsStateSet: An enum with a time series per state. Good for variable low-cardinality enums.
                             #   Bits: An RFC 2578 BITS construct, which produces a StateSet with a time series per bit.


Here is a list of MIBS:

.. seealso:: https://github.com/librenms/librenms/tree/master/mibs

You can get more info here:

.. seealso:: https://github.com/prometheus/snmp_exporter/tree/master/generator

And here:

.. seealso:: https://programmer.group/prometheus-prometheus-monitoring-switch-snmp.html

Once you are done tuning the file, simply do:

.. code-block:: text

  $ export MIBDIRS=mibs
  $ ./generator generate

>hat you will get is a snmp.yml file. Simply copy the new file:

.. code-block:: text

  $ cp snmp.yml /etc/snmp_exporter/

Setup targets
-------------

To setup the targets, simply add:

.. code-block:: yaml

  monitoring:

  exporters:
    snmp_exporter:
      port: 9116
      with_generator: false

to the /etc/ansible/inventory/group_vars/equipment_profile you desire.

Switch setup
------------

To setup the community on the switch to communicate with the exporter:
Go to the switch via ssh or telnet, and enter the following commands:

.. code-block:: text

  $ Enable
  $ configure terminal
  $ snmp-server community cluster RO
  $ exit
  $ write memory

You can change cluster to any community name you want, that is written in the
 snmp.yml file

Start service
-------------

To start the service, simply run:

.. code-block:: text

  systemctl start snmp_exporter

.. note:: all exporter services are under the /etc/systemd/system directory, and most binaries are under the /usr/local/bin directory

Dashboard
---------

The dashboard gives the following:

* Interface thoughput( in and out)
* Interface in,out,total in, total out, Bandwidth
* Alerts
* Percentage of casts (uni,multi,etc) In and Out
* Max in, Max out, number of interfaces, Total in,Uptime, Total out
* Etc...
