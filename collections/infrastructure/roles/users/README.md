# Users

## Description

This role provides a very basic users management, for simple clusters.
The role generates a dedicated group for each users, then users themselves, and can add ssh keys to their authorized_keys file.

## Instructions

Define `users` list as following example:

```
users:
  - name: johnnykeats
    uid: 1078
    gid: 1078
    home: /home/johnnykeats
    shell: /bin/bash
    comment: dream all the day # optional
    password: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0
  - name: oxedions
    uid: 1079
    gid: 1079
    home: /home/oxedions
    shell: /bin/bash
    password: !
  - name: bluebanquise
    home: /home/bluebanquise
    shell: /bin/bash
    comment: BlueBanquise account
    password: '*'
    ssh_authorized_keys:
      - <ssh key 1>
      - <ssh key 2>
      - <ssh key 3>
```

Available arguments for each user are:

* name
* uid
* gid
* password
* state
* groups (optional)
* create_home (optional)
* update_password (optional)
* shell (optional)
* home (optional)
* generate_ssh_key (optional)
* ssh_key_bits (optional)
* ssh_key_file (optional)
* remove (optional)
* comment (optional)

To ensure a user is not on a system, set state to "absent". To also remove its
home, set remove to "yes".

It is also possible to add ssh public keys for users. The following parameters
are available for each user:

* ssh_authorized_keys: a list of ssh public keys to be added to user's authorized_keys file
* ssh_authorized_keys_exclusive: if the provided list must be exclusive (will erase other existing keys in authorized_keys file)

To generate an sha512 password, use the following command (python >3.3):

```
python -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'
```

Or (python 2):

```
python -c "import crypt,random,string; print crypt.crypt(raw_input('clear-text password: '), '\$6\$' + ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)]))"
```

## Changelog

**Please now update CHANGELOG file at repository root instead of adding logs in this file.
These logs bellow are only kept for archive.**

* 1.1.1: Role enhancement and bug fixing. Hamid MERZOUKI <hamid@sesterce.com>
* 1.1.0: Role enhancement. New inventory structure. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Documentation and resources. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
