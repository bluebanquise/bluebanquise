# Rasdaemon

## Description

These settings install and start the Rasdaemon tool, to track hardware errors (memory, PCIe, CPU...).

Supported distributions: RHEL 9/10, Ubuntu 24.04/26.04, Debian 13, OpenSuse Leap 16.

## External documentation

[Project sources on Github](https://github.com/mchehab/rasdaemon)

[Small tutorial on manual usage](https://www.setphaserstostun.org/posts/monitoring-ecc-memory-on-linux-with-rasdaemon/)

## Instructions

Simply apply these settings, then check regularly (using a script or a monitoring
probe) that no errors are found, using command:

```
ras-mc-ctl --error-count
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `rasdaemon_enable_services` | `bb_enable_services`, else `true` | Enable rasdaemon service. |
| `rasdaemon_start_services` | `bb_start_services`, else `true` | Start rasdaemon service. |
