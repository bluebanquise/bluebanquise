Diskless Technical Documentation
================================

This documentation is about the diskless tool. It is a technical documentation for the developers. It allow to understand the tool internal architecture and functioning.

Software Architecture
----------------------

The tool is class and object oriented and fully modular. 

It can be used by mutiple ways:

* Use class methods to manage diskless images.
* Connect a custom API in order to use the class methods.
* Use the cli integrated system.

Classes architecture
^^^^^^^^^^^^^^^^^^^^

The tool is based on a simple design patern:

.. figure::  /diskless/images/class_architecture.SVG
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
^^^^^^^^^^^^^^^^^^^^

The images classes are contained in modules:

.. figure::  /diskless/images/modules_architecture.SVG
   :align:   center

   The modules and their classes

Each module is independent and can be added or removed from the module directory depending on the needs.

File system architecture
^^^^^^^^^^^^^^^^^^^^^^^^

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

The image system
---------------------

Overview about images
^^^^^^^^^^^^^^^^^^^^^

In the diskless tool images are objects instantiated from Image class inherited classes. An Image object is a representation of a concrete diskless image. An image cannot be directly instantiated from Image class because it is an abstract class. Image classes inherited from Image class are specific images. Each inherited image class has it's own features and image creation process. For example the process of creation of an NFS image by the NfsImage class is different from the process of creation of a Livenet image by the LivenetImage class.

Each image object has at least its own base directory in directory:

.. code-block:: text

    /var/www/html/preboot_execution_environment/diskless/images

This directory take the name of the image, for exemple:

.. code-block:: text

        /var/www/html/preboot_execution_environment/diskless/images/myimage

An image object has two mandatory base files in it's base directory that are:

* image_data.yml: The file where all images attributs are stored when the diskless program is not running.
* boot.ipxe: The booting file of the image that give instructions about the booting process.


Save an image
^^^^^^^^^^^^^

A diskless image has several attributs, for exemple it's name or it's kernel. When the diskless program is not running we need to have all images attributs saved. This save is done by the register_image() instance method of the Image class. Calling this method with an image object just save all the image attributs in it's image_data.yml file.

When modifying image attributs you need to re-register image in order to save new image attributs values.

Load an image
^^^^^^^^^^^^^

To load an image as an object, just call the ImageManager.get_created_image(image_name) static method with the created image name to load.

Module creation
---------------

Module implementation
^^^^^^^^^^^^^^^^^^^^^

With the diskless tool other modules and image classes can be easily and quickly created by developers.

The creation of a new module need to follow some conventions:

* The name of the module must finish by '_module.py'.
* In order to use the module it must be stored in the /lib/python3.6/site-packages/diskless/modules directory.

If the module is compliant it will be automatically detected by the diskless tool.

To use the module with cli interface, the module need to has a cli_menu() function. The aim of these function is to provide actions inside the module. You can take exemple from the demo_module.

Images class's implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inside a module, developers can implement images classes depending of their needs. These image classes must be inherited from Image class (in base_module).

Inherited classes have to follow several convention:

First, they have to redefine all Image abstract methods:

* create_new_image()       -> Define your own image creation process
* remove_files()           -> Specify what files to remove when the image was properly created
* clean()                  -> Specify what files to remove when the image was not properly created (All possible files)
* get_boot_file_template() -> Get the image boot file template

The module has also to be compliant with the constructor and create_new_image() method implementation. It has to define it's constructor and and create_new_image() as following:

.. code-block:: python

    def __init__(self, name, arg1 = None, arg2 = None, argX = None...):
        super().__init__(name, arg1, arg2, argX...)                     
                                                               
    def create_new_image(self, arg1, arg32, argX...):                   
        ...(your code)      
        
The constructor don't have to be modified, all instruction for image creation must be defined in and from create_new_image() body. Look at the demo_image for an exemple of implementation.

Cleaning process
----------------

The cleaning process is an important process to keep diskless tool file system clean. This process aim to clean all files of an image when the installation process of the image has crashed.

Image creation process
^^^^^^^^^^^^^^^^^^^^^^

The mechanism of cleaning images use a file called installation.yml file. We add informations about images installation inside this file during the image installation.

Bellow, a properly image creation process:

.. figure::  /diskless/images/proper_installation.png
   :align:   center

   A proper installation process

We can see that at the start of the installation the image is registered inside the installations.yml file, and at the end of the installation the image is unregistered from this file.

Bellow, a bad image installation process:

.. figure::  /diskless/images/bad_installation.png
   :align:   center

   An image installation that crash 
   
We can see that the image is nether unregistered from the installation.yml file because the process has crashed.

Image status
^^^^^^^^^^^^

An image can has three status:

+----------------------------------------+------------+------------+-----------+
| Image status                           | CREATED    | IN_CREATION| CORRUPTED |
+========================================+============+============+===========+
| Inside installations.yml file          |            |     x      |     x     |
+----------------------------------------+------------+------------+-----------+
| Installation process is running        |            |     x      |           |
+----------------------------------------+------------+------------+-----------+

As you can see the image status depend on two elements. If the image is registered or not inside the installation.yml file, and if the process that install the image is currently running.

The content of the installatins.yml file is the following:

.. figure::  /diskless/images/installation_file.png
   :align:   center

   Content of installations.yml file during two simultaneous images installations.

We can see that the name and the class of the image are registered. The pid of the installation process is also registered.

Cleaning process
^^^^^^^^^^^^^^^^

The cleaning process is called once after the user has selected an action in the main menu in gui.

Bellow the cleaning process:

.. figure::  /diskless/images/clean_installations.SVG
   :align:   center
   
   Image cleaning process
   
We can see that an image is cleaning when it's status is CORRUPTED. Bellow the process to get image status:

.. figure::  /diskless/images/get_image_status.SVG
   :align:   center
   
   Getting image status process
   
This process returns the image status in compliance with the previous image status table.





