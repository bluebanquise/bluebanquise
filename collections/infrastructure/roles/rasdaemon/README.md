# Rasdaemon

## Description

These settings install and starts Rasdaemon tool to track hardware issues.

## External documentation

[Project sources on Github](https://github.com/mchehab/rasdaemon)

[Small tutorial on manual usage](https://www.setphaserstostun.org/posts/monitoring-ecc-memory-on-linux-with-rasdaemon/)

## Instructions

Simply apply these settings, then check regularly (using a script or a monitoring
probe) that no errors are found, using command:

```
ras-mc-ctl --error-count
```
