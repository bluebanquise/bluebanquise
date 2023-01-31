# google_authenticator ( 2fa )

## Description

This role simply install google-authenticator tool and configure the basics to enable 2fa over ssh.

## Instructions

For now the Role has two possible configuration modes:

1 - public key + google authenticator ( recomended )

```yaml
mfa_mode: password
```

2- password + google authenticator

```yaml
mfa_mode: publickey
```

## Changelog

* 1.0.0: Role creation. Lucas Santos <lucassouzasantos@gmail.com>
