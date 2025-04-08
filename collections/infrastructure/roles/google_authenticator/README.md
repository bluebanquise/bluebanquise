# google_authenticator ( 2fa )

## Description

This role simply install google-authenticator tool and configure the basics to enable 2fa over ssh.

## Instructions

For now the Role has two possible configuration modes:

1 - public key + google authenticator ( recommended )

```yaml
google_authenticator_mfa_mode: publickey
```

2- password + google authenticator

```yaml
google_authenticator_mfa_mode: password
```

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.0.1: Port to bb 2.0. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Lucas Santos <lucassouzasantos@gmail.com>
