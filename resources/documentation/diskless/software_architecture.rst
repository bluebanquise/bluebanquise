Software Architecture
======================

The tool is class and object oriented and fully modular. 

It can be used by mutiple ways:

* Use class methods to manage diskless images.
* Connect a custom API in order to use the class methods.
* Use the cli integrated system.

Classes architecture
---------------------

The tool is based on a simple design patern:

.. figure::  ./images/class_architecture.SVG
   :align:   center

   Class architecture

There are three main classes:

* KernelManager: The class to manage kernels
* ImageManager: The class to manage images
* Image: The mother class of all images

The Image class can be inherited to create custom image classes. The first implementation of the diskless tool includes three image classes:

* NfsImage: The class to create nfs images. With this type of image a node can had a remote operating system on an nfs server.

* LivenetImage: The class to create livenet images. With this type of image a node can load it's operation system in RAM.

* DemoImage: A demo image class that is an exemple of how to create custom classes.

Modules architecture
---------------------

The images classes are contained in modules:

.. figure::  ./images/modules_architecture.SVG
   :align:   center

   The modules and their classes

Each module is independent and can be added or removed from the module directory depending on the needs.

File system architecture
------------------------

Bellow the gobal hierarchy of the diskless tool files (absolute paths) :

* Diskless basic files:

.. code-block:: text

    /diskless
    └── /images
        └── /nfsimages 
            ├── /golden
            └── /staging 

* Python modules

.. code-block:: text

    /lib/python3.6/site-packages/diskless/
    ├── utils.py
    ├── image_manager.py
    ├── kernel_manager.py
    └── /modules 
        ├── base_module.py 
        ├── livenet_module.py 
        ├── demo_module.py 
        └── nfs_module.py 

* Ongoing installations file 

.. code-block:: text

    /var/lib/diskless
    └── installations.yml 

* Temporary directory to work with images

.. code-block:: text

    /var/tmp/diskless/workdir/

* CLI diskless script:

.. code-block:: text

    /usr/bin  
    └── disklessset (disklesset.py)  

* Files on http server:

.. code-block:: text

    /var/www/html/preboot_execution_environment/diskless  
    ├── images  
    └── kernels  


