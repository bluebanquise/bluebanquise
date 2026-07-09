# Root password

## Description

These settings update the root password on the target hosts.
## Instructions

The root password must be defined in the inventory per equipment profiles using:

```yaml
os_admin_password_sha512: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
```

Or globally using:

```yaml
root_password_os_admin_password_sha512: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
```

To generate an sha512 password, use the following command (python >3.3):

```
python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'
```

Note that for security reasons, no default value is provided.
