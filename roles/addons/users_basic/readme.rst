Users basic
-----------

Description
^^^^^^^^^^^

This role provides a very basic users management, for simple clusters.

Instructions
^^^^^^^^^^^^

Copy addon/users_basic.yml into /etc/bluebanquise/inventory/group_vars/all/addons folder.

Then edit this file according to your needs, and play this role on all hosts with users.

To generate an sha512 password, use the following command (python >3.3):

.. code-block:: bash

  python -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'

Or (python 2):

.. code-block:: bash

  python -c "import crypt,random,string; print crypt.crypt(raw_input('clear-text password: '), '\$6\$' + ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(16)]))"

Changelog
^^^^^^^^^

* 1.0.1: Documentation and ressources. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
