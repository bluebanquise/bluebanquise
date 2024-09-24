============
Introduction
============

**BlueBanquise** is a generic stack, based on Ansible, whose purpose is to
deploy and manage clusters of hosts.
These clusters can be from few workstations in enterprise to very large HPC or
servers farm clusters.

.. image:: images/clusters/3_size_single_row.png

**BlueBanquise** is the result of a need. A need for a very simple stack, not
based on multi languages scripts difficult to maintain. A stack that can keep
simplicity while managing very complex architecture.

The **BlueBanquise** project also aims to train new system administrators to the
deployment of bare metal servers.

The project relies on **Ansible**.
Ansible was chosen for its simplicity and its security.
The Ansible inventory groups/variables mechanism can cover from very simple to
very sophisticated configurations. Ansible is not the fastest tool, nor the
simplest to debug. However, it is easy to learn, and widely used today with an
active community.

The **BlueBanquise** stack is made of multiple Ansible collections.
The *infrastructure* collection is the largest one, and should be generic.
Other collections allows to specialize the cluster of hosts.


This documentation is structured as the following:

* Few basic vocabulary
* Procedure to install BlueBanquise
    * Bootstrap and configure BlueBanquise on first management host
    * Deploy cluster
* Procedures to specialize the cluster

If you encounter any bugs/issues or have any comments, please let me know.

Note also that since BlueBanquise is a multi-distribution based stack, parts of the
documentation may be dedicated to a specific Linux distribution (always
explicitly mentioned).

I hope you will enjoy this stack as much as I do developing it.

If you need help, do not hesitate to use `the discussions tab <https://github.com/bluebanquise/bluebanquise/discussions>`_
of the project's github.

Next step is to grab few basic :ref:`Vocabulary`.
