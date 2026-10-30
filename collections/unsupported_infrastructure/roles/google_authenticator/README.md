# google_authenticator (2FA)

## Description

This role installs google-authenticator, and configures SSH two-factor authentication: users log in with a first factor (SSH key or password), then a verification code (TOTP) from an authenticator application.

## Instructions

### Modes

The role has two modes, set with `google_authenticator_mfa_mode`:

* `publickey` (default, recommended): SSH key, then verification code. Password authentication is disabled for SSH.
* `password`: password, then verification code.

### Users setup

Each user must configure google-authenticator once, by running `google-authenticator` on the host, and scanning the displayed QR code with an authenticator application. This creates the `~/.google_authenticator` file of the user.

**Warning:** by default (`google_authenticator_nullok: false`), users who did not configure google-authenticator yet can no longer log in with SSH, administrators included. To deploy two-factor authentication progressively, set `google_authenticator_nullok: true`: users without configuration then log in as before (SSH key only, or password only), until they configure google-authenticator.

### Files

* `/etc/ssh/sshd_config.d/10-bluebanquise-google-authenticator.conf`: SSH server settings. A drop-in file is used, as the SSH server keeps the first value of each setting, and distributions set conflicting values (for example `KbdInteractiveAuthentication no` in Ubuntu `sshd_config`, `ChallengeResponseAuthentication no` in RHEL `50-redhat.conf`). The file is checked with `sshd -t` before being installed, and the SSH server is restarted on change.
* `/etc/pam.d/sshd`: adds the google-authenticator module, and disables (publickey mode) or enables (password mode) the distribution password authentication line.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `google_authenticator_mfa_mode` | `publickey` | `publickey` (SSH key + code) or `password` (password + code). |
| `google_authenticator_nullok` | `false` | Allow users without google-authenticator configuration to log in without verification code. |
| `google_authenticator_start_services` | `bb_start_services`, else `true` | Restart the SSH server on configuration change. |
