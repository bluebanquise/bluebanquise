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

Now you can load the BlueBanquise environment (Python, Ansible and tools), using the ``bluebanquise-environment`` command:

.. code-block:: text

  /var/lib/bluebanquise/bluebanquise/stack/bin/bluebanquise-environment load

.. note::
  You can unload this environment at anytime using ``unload`` instead of ``load`` at the end of this command.

This command will have loaded a Python virtual environment located at ``/var/lib/bluebanquise/ansible_venv/`` and added ``/var/lib/bluebanquise/bluebanquise/stack/bin``.

Test you can now use the ``bluebanquise-ansible-playbook`` command:

.. code-block:: text
  
  $ bluebanquise-ansible-playbook --version
  ansible-playbook [core 2.19.2]
  config file = None
  ...


Configure inventory
===================

You can now create your first cluster inventory, which acts as a text/folders based database of your cluster description.

To do so, you can either create it manually from scratch using the remaining docuentation, or initialize it with the ``bluebanquise-inventory`` tool.

.. code-block:: text

  bluebanquise-inventory create