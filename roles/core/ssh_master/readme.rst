SSH master
----------

Description
^^^^^^^^^^^

This role configure the ssh access of know hosts to make this access through nodes main network.

Instructions
^^^^^^^^^^^^

This role will generate a configuration file in */root/.ssh/config*.

This file will contains all hosts of the Ansible inventory (or all hosts of the
current iceberg if using icebergs mode), with the following parameters:

.. code-block:: text

  Host freya
      Hostname %h-ice1-1

Note that for this example host, **freya**, the target hostname for ssh is
%h-ice1-1, which translates to **freya-ice1-1**. This can be seen when invoking
ssh with verbosity:

.. code-block:: text

  [root@odin ]# ssh freya -vvv
  OpenSSH_7.8p1, OpenSSL 1.1.1 FIPS  11 Sep 2018
  debug1: Reading configuration data /root/.ssh/config
  debug1: /root/.ssh/config line 10: Applying options for freya
  debug1: Reading configuration data /etc/ssh/ssh_config
  debug3: /etc/ssh/ssh_config line 52: Including file /etc/ssh/ssh_config.d/05-redhat.conf depth 0
  debug1: Reading configuration data /etc/ssh/ssh_config.d/05-redhat.conf
  debug3: /etc/ssh/ssh_config.d/05-redhat.conf line 2: Including file /etc/crypto-policies/back-ends/openssh.config depth 1
  debug1: Reading configuration data /etc/crypto-policies/back-ends/openssh.config
  debug3: gss kex names ok: [gss-gex-sha1-,gss-group14-sha1-]
  debug3: kex names ok: [curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1]
  debug1: /etc/ssh/ssh_config.d/05-redhat.conf line 8: Applying options for *
  debug2: resolving "freya-ice1-1" port 22
  debug2: ssh_connect_direct
  debug1: Connecting to freya-ice1-1 [10.11.2.1] port 22.

You can see here ssh is not trying to reach **freya** but is using
**freya-ice-1-1**. This has been made to ensure whatever the direct resolution
is in /etc/hosts or DNS, ssh and so Ansible will always use the management
network of the target host.

Also, keep in mind that when redeploying a host its SSH key changes, which
requires to remove the former host key from the known_hosts file, then add the
new key. It is possible to achieve this with the commands below:

.. code-block:: bash

  # for host in $(nodeset -e $NODES); do \
      sed -i -e "/^${host}/d" /root/.ssh/known_hosts; \
  done
  # clush -o '-o StrictHostKeyChecking=no' -w $NODES dmidecode -s system-uuid

It is possible to disable the strict host key checking in the inventory with the
configuration below:

.. code-block:: yaml

   ---
   security:
     ssh:
       hostkey_checking: false

This was the default behaviour prior BlueBanquise 1.3. The ssh configuration
file will include the following parameters:

.. code-block:: text

  Host freya
      StrictHostKeyChecking no
      UserKnownHostsFile=/dev/null
      Hostname %h-ice1-1

This ensure no issues when redeploying an host, at the cost of security.

Note that this file generation is kind of "sensible", and will surely be the
first one to break in case of uncoherent inventory. If this happens, check your
inventory, fix it, and remove manually /root/.ssh/config and relaunch its
generation.

To be done
^^^^^^^^^^

Add ProxyJump for icebergs


Changelog
^^^^^^^^^

* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
