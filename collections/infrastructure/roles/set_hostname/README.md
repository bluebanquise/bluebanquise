# Set Hostname

## Description

These settings simply sets a host static (hardcoded) hostname.

## Instructions

By default, an FQDN hostname is set. If users wish to set a basic hostname,
variable `set_hostname_fqdn` must be set to **false**.

FQDN is based on content of variable `set_hostname_domain_name` or `bb_domain_name` (default is `cluster.local`).
Note that `set_hostname_domain_name` is precedencing the global variable `bb_domain_name` if set.

Note also that using these settings identify the host.
This should not be used when creating a diskless golden image.
