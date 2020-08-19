Root password
-------------

Description
^^^^^^^^^^^

This role updates the root password on the target hosts.

Instructions
^^^^^^^^^^^^

The root password must be defined in the inventory:

.. code-block:: yaml

  authentication_root_password_sha512: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0

To generate an sha512 password, use the following command (python >3.3):

.. code-block:: bash

  python -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'

Input
^^^^^

Mandatory inventory vars:

**hostvars[inventory_hostname]**

* authentication_root_password_sha512

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Bruno Travouillon <devel@travouillon.fr>
