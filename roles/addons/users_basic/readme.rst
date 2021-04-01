Users basic
-----------

Description
^^^^^^^^^^^

This role provides a very basic users management, for simple clusters.

Instructions
^^^^^^^^^^^^

Create file inventory/group_vars/all/addons/users_basic.yml with the following content:

.. code-block:: yaml

  users_basic:

    users:
      - name: johnnykeats
        uid: 1078
        gid: 1078
        home: /home
        shell: /bin/bash
        comment: dream all the day # optional
        password: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0

Then edit this file according to your needs, and play this role on all hosts with users, including slurmctld server if using slurm.

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

To generate an sha512 password, use the following command (python >3.3):

.. code-block:: bash

  python -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'

Or (python 2):

.. code-block:: bash

  python -c "import crypt,random,string; print crypt.crypt(raw_input('clear-text password: '), '\$6\$' + ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)]))"

Changelog
^^^^^^^^^

* 1.1.0: Role enhancement. New inventory structure. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.1: Documentation and resources. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
