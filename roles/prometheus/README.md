# Prometheus

## Description

This role deploy Prometheus (server/client) with related additional software.

## Instructions

### Server or/and client

To install server part, set `prometheus_server` to `true` at role invocation
vars.

To install client part, set `prometheus_client` to `true` at role invocation
vars.

### Default ports

* Prometheus is available at http://localhost:9090
* Alertmanager is available at http://localhost:9093
* Node_exporter is available at http://localhost:9100
* Karma is available at http://localhost:8080

### General server side configuration

By default, role will inherit from values set in its defaults folder.
You may wish to update these values to your needs, as these values set the
different timings used by Prometheus.

To do so, create file inventory/group_vars/all/prometheus.yml with the
following content (tuned to your needs):

```yaml
  prometheus:
    scrape_interval: 1m
    evaluation_interval: 2m
    alertmanager:
      group_wait: 1m
      group_interval: 10m
      repeat_interval: 3h
```

See also:

* https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config
* https://www.robustperception.io/whats-the-difference-between-group_interval-group_wait-and-repeat_interval

**Alerting**:

By default, the role will only add a simple alerts file into the
/etc/prometheus/alerts folder. This file contains a basic alert that fire when
an exporter is down.

You will probably wish to add more alerts. You can add more files in this same
directory, and these will be loaded by Prometheus at startup.

### General client side configuration

Each role has its own http port. For example, Node_exporter is available at
http://localhost:9100 .

In order for this role to install and start exporters on the host, a
configuration is required in the Ansible inventory.

A file is needed for each **equipment_profile** group that should be monitored.

For example, to have equipment_typeC nodes installing and starting the
node_exporter, you will need to create file
*inventory/group_vars/equipment_typeC/monitoring.yml* with the following content:

```yaml
  monitoring:
    exporters:
      node_exporter:
        package: node_exporter
        service: node_exporter
        port: 9100
```

And for example, on your management nodes, you may wish to have more exporters
setup to monitor much more things. This would be here, assuming managements
nodes are from equipment group equipment_typeM, a file
*inventory/group_vars/equipment_typeM/monitoring.yml* with the following content:

```yaml
  monitoring:
    exporters:
      node_exporter:
        package: node_exporter
        service: node_exporter
        port: 9100
      ha_cluster_exporter:
        package: ha_cluster_exporter
        service: ha_cluster_exporter
        port: 9664
      slurm_exporter:
        package: slurm_exporter
        service: slurm_exporter
        scrape_interval: 5m
        scrape_timeout: 5m
        port: 9817
```

Note that ha_cluster_exporter and slurm_exporter are documented in the stack,
but no packages are provided by the BlueBanquise project. Refer to the
monitoring main documentation to get additional details about these exporters.

You can see here that it is possible to customize the scrape_interval and
scrape_timeout.

### IPMI and SNMP

ipmi_exporter and snmp_exporter behave differently: they act as translation
gateways between Prometheus and the target. Which means, if you wish for example
to query IPMI data of a node, you do not install the exporter on the node itself.

By default, the server task will install both exporters, and configure them. And
the client task will simply ignore them if present in the exporters list to be
installed on the client.
The role will then check each equipment_profile and if ipmi_exporter or/and
snmp_exporter exporters are defined under *monitoring.exporters*, then all nodes
of the equipment_profile will be added to the list of target to be scraped
through these exporters.

Example: User wish to gather IPMI data of all nodes of equipment_typeC. To do so,
create file *inventory/group_vars/equipment_typeC/monitoring.yml* with the
following content:

```yaml
  monitoring:
    exporters:
      ipmi_exporter:
        scrape_interval: 5m
        scrape_timeout: 5m
```

## To be done

* Global role reorganization
* Allow groups alerts selection.

## Changelog

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>, johnnykeats <johnny.keats@outlook.com>
