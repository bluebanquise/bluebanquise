# Changelog

## 1.5.1

### Updated roles

  - high_availability:
    - Allows order constraint between resource groups (#58)

## 1.5.0

### New roles

  - loki. Owner: @neilmunday
  - automate. Owner: @oxedions

### Updated roles

  - slurm: missing string filter in templates
  - prometheus: update ubuntu support

## 1.0.1

### Updated roles

  - automate:
    - improve yaml loader. (#49)

  - high_availability:
    - configure firewall before pcs commands. (#41)
    - enable/disable STONITH when configuration is available/unavailable (#43)
    - fix use of unencrypted password of hacluster user (#45)

  - podman:
    - correct logical operator to run local registry. (#33)
    - quotes in lists of registries. (#34)

## 1.0.0

### New roles

  - clone. Owner: @oxedions
  - display_tuning. Owner: @oxedions
  - drbd. Owner: @oxedions
  - generic_psf. Owner: @johnnykeats
  - grafana. Owner: @oxedions
  - haproxy. Owner: @oxedions
  - high_availability. Owner: @oxedions
  - lmod. Owner: @oxedions
  - nhc. Owner: @oxedions
  - nvidia. Owner: @oxedions
  - ofed. Owner: @oxedions
  - openldap. Owner: @oxedions
  - prometheus. Owner: @oxedions
  - rasdaemon. Owner: @oxedions
  - report. Owner: @oxedions
  - singularity. Owner: @strus38
  - slurm. Owner: @oxedions
  - update_reboot: Owner: @oxedions
  - users_basic. Owner: @oxedions


### Updated roles

  - advanced_dhcp_server: prevent filename for none server type hosts. (#6)
  - slurm: major role upgrade. (#11)
  - users_basic: add ssh public keys support. (#12)
  - prometheus: correct default value of prometheus_exporters_groups_to_scrape. (#30)

### New tools

### Updated tools
