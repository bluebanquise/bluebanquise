Module creation
======================

Module implementation
---------------------

With the diskless tool other modules and image classes can be easily and quickly created by developers.

The creation of a new module need to follow some conventions:

* The name of the module must finish by '_module.py'.
* In order to use the module it must be stored in the /diskless/modules directory.

If the module is compliant it will be automatically detected by the diskless tool.

To use the module with cli interface, the module need to has a cli_menu() function. The aim of these function is to provide actions inside the module. You can take exemple from the demo_module.


Images class's implementation
-----------------------------

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
    
    
    
    
    
