The image system
=================

Overview about images
---------------------

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
----------------

A diskless image has several attributs, for exemple it's name or it's kernel. When the diskless program is not running we need to have all images attributs saved. This save is done by the register_image() instance method of the Image class. Calling this method with an image object just save all the image attributs in it's image_data.yml file.

When modifying image attributs you need to re-register image in order to save new image attributs values.

Load an image
----------------

To load an image as an object, just call the ImageManager.get_created_image(image_name) static method with the created image name to load.
