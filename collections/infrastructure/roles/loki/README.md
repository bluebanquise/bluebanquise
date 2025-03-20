# Loki

## Description

This role configures Loki and Promtail on a BlueBanquise management node.

A rsyslog forwarder configuration file is created to forward all rsyslog traffic to Promtail. From here Promtail uses Loki to store the data.

The following labels are added to the syslog data:

- app
- host
- job
- level

Further details about Loki and Promtail can be found at: https://grafana.com/docs/loki/latest

Loki can be set as a data source in Grafana by setting the data source URL to http://localhost:3100.

## Requirements

loki and promtail RPMs are required.

## Role Variables

All variables which can be overridden are stored in [defaults/main.yml](defaults/main.yml) file as well as in table below.

| Name | Default Value | Description |
| ---- | ------------- | ----------- |
| loki_groups                 | See `defaults/main.yml`    | Dictionary of groups to create                                            |
| loki_users                  | See `defaults/main.yml`    | Dictionary of users to create                                             |
| loki_conf_dir               | /etc/loki                  | Loki config directory                                                     |
| loki_data_dir               | /var/lib/loki              | Loki data directory                                                       |
| loki_index_dir              | {{ loki_data_dir }}/index  | Loki index directory                                                      |
| loki_chunks_dir             | {{ loki_data_dir }}/chunks | Loki chunks directory                                                     |
| loki_ip                     | 127.0.0.1                  | Loki HTTP IP address                                                      |
| loki_port                   | 3100                       | Loki HTTP port                                                            |
| loki_grpc_port              | 9095                       | Loki gRPC port                                                            |
| loki_promtail_conf_dir      | /etc/promtail              | Promtail config dir                                                       |
| loki_promtail_enable_server | false                      | Enable Promtail HTTP/gRPC server (not needed for processing central logs) |
| loki_promtail_ip            | 127.0.0.1                  | Promtail HTTP/gRPC address                                                |
| loki_promtail_port          | 9080                       | Promtail HTTP port                                                        |
| loki_promtail_grpc_port     | 0                          | Set to zero to randomise gRPC port                                        |
| loki_promtail_grpc_ip       | 127.0.0.1                  | Promtail gRPC address                                                     |
| loki_promtail_syslog_port   | 1514                       | Syslog listener port                                                      |
| loki_promtail_syslog_ip      | 127.0.0.1                  | Syslog address                                                            |

## Change log

* 1.0.0: Role creation. Neil Munday <neil@mundayweb.com>
