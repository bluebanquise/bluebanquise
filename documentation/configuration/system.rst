======
System
======

System roles take care of the hosts themselves: their network interfaces, their packages and
repositories, their users, their security settings, and all the small things that make a freshly
installed operating system become a real member of your cluster.

Most of these roles are applied on every host, management hosts included. Their settings can be
set at group level (``group_vars/``) or at host level (``host_vars/``) in the inventory, with one
exception worth keeping in mind: ``hw_`` and ``os_`` prefixed variables belong to hardware and
OS groups only (see :doc:`groups`).

.. note::

  A good starting point for a new host is the trio ``nic``, ``repositories`` and
  ``local_configuration``: once its network, its package sources and its base system settings are
  in place, every other role can follow.

------------

Here is the detailed configuration available for each system related role of the stack.

.. toctree::
   :maxdepth: 1
   :caption: System:

   system/local_configuration
   system/nic
   system/repositories
   system/hosts_file
   system/dns_client
   system/firewall
   system/sshd
   system/ssh_client
   system/ssh_remote_keys
   system/users
   system/auditd
   system/cloudinit
   system/custom_packages
   system/logrotate
   system/update_reboot
   system/xfs_quota
   system/gpu
   system/lmod
   system/nhc
   system/rasdaemon
   system/clustershell
   system/bluebanquise_power
   system/powerman
