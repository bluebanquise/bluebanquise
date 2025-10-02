===========
Inventories
===========

Create first inventory
======================

You can now create your first cluster inventory, which acts as a text/folders based database of your cluster description.

To do so, you can either create it manually from scratch using the remaining documentation, or initialize it with the ``bluebanquise-manager`` tool.

.. code-block:: text

  bluebanquise-manager create-inventory

.. note::

  This tool was made to cover basic clusters. In order to create a complex inventory, please refer to the documentation.
  It is possible to use both the tool and custom files. The tool will always prefix its files with ``bbm_`` prefix. Edit these files with care.
  Other files will be ignored by the tool, but not during Ansible execution.

