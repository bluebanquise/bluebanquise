============
Installation
============

Install BlueBanquise
====================

Make sure the system possesses curl command, then bootstrap bluebanquise using the provided online installer:

.. code-block:: text

  sudo source <(curl -s https://raw.githubusercontent.com/bluebanquise/bluebanquise/refs/heads/master/bootstrap/online_bootstrap.sh)

Once this installer has been used, you should have a new user called ``bluebanquise``, with home folder set at ``/var/lib/bluebanquise``.

Load working environment
========================

Login as the bluebanquise user:

.. code-block:: text

  sudo su - bluebanquise

This user can be considered as the "cluster admin user". Deployed nodes for example will automatically have
the bluebanquise user configured and ssh keys set so that you can ssh on them.

Test you can now use the ``ansible-playbook`` command:

.. code-block:: text
  
  $ ansible-playbook --version
  ansible-playbook [core 2.19.2]
  config file = None
  ...

BlueBanquise tool is now installed on the current system (but not deployed yet!).

Next step is to create your first inventory to define and configure your cluster.

You can also, if needed, have a quick look to the vocabulary page (this is not mandatory).
