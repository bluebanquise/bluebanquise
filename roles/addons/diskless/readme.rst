Diskless
--------

Description
^^^^^^^^^^^

This role provides needed tools to deploy a basic diskless cluster.

Instructions
^^^^^^^^^^^^

Once the role is deployed, it is possible to use the disklessset tool to interactivley create new diskless images.

Two type of images are available:

* Livenet images are full ram images, without persistance but need less infrastructure.
* NFS images are full nfs rw images, with psersistance, very simple to use, but need more infrastructure.

It is important to understand that this role is independant of the pxe_stack core role, and so each tools do not communicate.

To be done
^^^^^^^^^^

Clean code, add more error detection, and more verbosity.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
 
