# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# base_module:
#    This module contains the Image class that is the mother class
#    for all images classes. You need to be in compliance with this
#    class when creating new diskless images classes.
#
# 1.3.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>, Benoit Leveugle <benoit.leveugle@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import base modules
import os
import shutil
from datetime import datetime
import logging
from abc import ABC, abstractmethod
import subprocess

# Import diskless modules
from diskless.utils import inform
from diskless.image_manager import ImageManager
from diskless.utils import ask_module, load_file


class Image(ABC):

    """ Abstract class representing an image
    This class is the mother class for all types of images.

    You must redefine the following methods when inherit:

        * create_new_image()     -> Define your own image creation process
        * remove_files()         -> Specify what files to remove when image was properly created
        * clean()                -> Specify what files to remove when image was not properly created (All possible files)

    You can redefine the following methods when inherit:

        * generate_files()       -> Contains methods to execute to create image
        * create_image_folders() -> Create your image folders
        * generate_file_system() -> Generate your image file system

    Normaly you don't have to redefine other methods in sub classes but also you can for a specific need.
    Please check all Image class methods that can be redefined before creating a new method in subclass
    """

    # All type of image has a boot_file_template
    boot_file_template = ''

    # Each image has it's own base directory in IMAGES_DIRECTORY directory
    IMAGES_DIRECTORY = '/var/www/html/preboot_execution_environment/diskless/images/'

    def __init__(self, name, *args):
        """Class consructor.
        The constructor take in argument the name of the image, and the creation arguments (in *args).
        To get an already existing image that you have previously created, you must call this constructor whith only image 'name' to load it.
        To create a new image, you must call this constructor with image 'name' and all other requiered class constructor arguments.
        When you redefine Image class constructor you must define your constructor and create_new_image method as following:

            def __init__(self, name, arg1 = None, arg2 = None, argX = None...): <- You must strictly follow this syntax with your custom args (arg1, arg2, argX ...)
                super().__init__(name, arg1, arg2, argX...)                     <-
                                                                                <-
            def create_new_image(self, arg1, arg32, argX...):                   <-
                ...(your code)                                                  <- From here you can custom

        For an exemple look at DemoClass class in demo_module.

        :param name: The name of the image
        :type name: str
        :param *args: The list of arguments for image creation
        :type *args: list of arguments
        """

        # Check name format
        if ((not isinstance(name, str)) or (len(name.split()) > 1)):
            raise ValueError('Invalid name format.')

        self.name = name
        self.IMAGE_DIRECTORY = Image.IMAGES_DIRECTORY + self.name + '/'

        # If image already exist, and not all other arguments excepts name are None:
        # Bad usage of constructor
        if os.path.isdir(self.IMAGE_DIRECTORY) and not all(arg is None for arg in args):
            raise ValueError('Bad constructor image: All arguments must be None except name when image already exist')

        # If the image already exist, and all other arguments excepts name are None:
        # Load existing image
        elif os.path.isdir(self.IMAGE_DIRECTORY):
            self.get_existing_image()

        # If image don't already exist, create it
        else:
            # Register image in ongoing installations file
            ImageManager.register_installation(self.name, self.__class__.__name__)

            # Create the image object with all constructor arguments except the name because it is already an image attribute
            self.create_new_image(*args)

            # Register all image attributs at the end of its creation for saving it
            self.register_image()

            # After image creation, unregister it from ongoing installations file
            ImageManager.unregister_installation(self.name)
            logging.info('Image \'' + self.name + '\' creation complete !')

    @abstractmethod
    def create_new_image(self):
        """Create a new image. This method must be redefined in all subclasses."""
        logging.info('Starting image \'' + self.name + '\' creation')

    @abstractmethod
    def remove_files(self):
        """Remove all files of a created image when the image was properly created.
        This method must be redefined in all subclasses."""
        logging.info('Removing image \'' + self.name + '\' files')

        # Remove image base directory
        if os.path.isdir(self.IMAGE_DIRECTORY):
            logging.debug('Delating directory ' + self.IMAGE_DIRECTORY)
            logging.debug('Executing \'rm -rf ' + self.IMAGE_DIRECTORY + '\'')
            shutil.rmtree(self.IMAGE_DIRECTORY)

    @abstractmethod
    def clone(self, clone_name):
        """Clone the image into another image.
        :param clone_name: The name of the clone who will be cloned
        :type clone_name: str
        """
        logging.info('Clonning image \'' + self.name + '\' into \'' + clone_name + '\'')

    @staticmethod
    @abstractmethod
    def get_boot_file_template():
        """Get the class boot file template.
        This method must be redefined in all Image subclasses."""
        return ''

    @staticmethod
    @abstractmethod
    def clean(image_name):
        """ Clean all files of an image without the need of an image object.
        It is usefull to clean all files when an image has crashed during it's creation.
        This method must be redefined in all Image subclasses.
        The redefinition must clean all possible remaining image files.
        :param image_name: The name of the image to clean
        :type image_name: str
        """
        logging.info('Cleaning image \'' + image_name + '\' files')

    def generate_files(self):
        """Generate image files."""
        logging.info('Start generating image \'' + self.name + '\' stuff...')

    def create_image_folders(self):
        """Create image folders."""
        logging.info('Start generating image \'' + self.name + '\' folders...')

        # Create the base mandatory directory for the image
        logging.debug('Executing \'mkdir ' + self.IMAGE_DIRECTORY + '\'')
        os.mkdir(self.IMAGE_DIRECTORY)

    def generate_file_system(self):
        """Generate image file system."""
        logging.info('Start generating image \'' + self.name + '\' file system...')

    def register_image(self):
        """Register the image data into it's 'image_data' file.
        This file is a save of the image.
        To load an existing image this file is mandatory because it contains all image attributs."""
        logging.info('Registering image \'' + self.name + '\'')

        # Add creation date to image attributes, it is the date of image registering (current date)
        self.image_class = self.__class__.__name__
        self.creation_date = datetime.today().strftime('%Y-%m-%d')

        file_content = 'image_data:\n    '

        # For all image attributes
        for attribute, value in self.__dict__.items():
            # Register attribute
            file_content = file_content + '\n    ' + attribute + ': ' + str(value)

        # Creating or edit the image_data file that contains image attributes in yaml
        logging.debug('Writing image attributs inside ' + self.IMAGE_DIRECTORY + 'image_data.yml')
        with open(self.IMAGE_DIRECTORY + '/image_data.yml', "w") as ff:
            ff.write(file_content)

    def get_image_data(self):
        """Getting image data that has been writen inside the image image_data.yml during register_image() call."""

        # Reading image_data file
        data = load_file(self.IMAGE_DIRECTORY + '/image_data.yml')

        # Getting image_data
        return data['image_data']

    def get_existing_image(self):
        """Load an existing image. The loading consist of getting all image attributes from it's image_data.yml file."""

        # Get image data
        image_data = self.get_image_data()

        # Set all image attributes with image data
        for attribute_key, attribute_value in image_data.items():
            setattr(self, attribute_key, attribute_value)

        # Convert name into a string value, this is necessary because name can be a number
        self.name = str(self.name)

    # Change image kernel
    def set_kernel(self, kernel):
        """Change the kernel of the image.

        :param kernel: The kernel to set to the image
        :type kernel: str
        """
        logging.info('Set up image \'' + self.name + '\' kernel')

        # Change image kernel attibute
        self.kernel = kernel
        # Regenerate ipxe boot file
        self.generate_ipxe_boot_file(self.get_ipxe_boot_file())
        # Register image with new kernel
        self.register_image()

    def generate_ipxe_boot_file(self):
        """Generate an ipxe boot file for the image."""
        logging.info('Creating image \'' + self.name + '\' IPXE boot file')

        # Format image ipxe boot file template with image attributes
        file_content = self.__class__.get_boot_file_template().format(image_name=self.name,
                                                                      image_initramfs=self.image,
                                                                      image_kernel=self.kernel)

        # Create ipxe boot file
        logging.debug('Creating boot content inside file ' + self.IMAGE_DIRECTORY + 'boot.ipxe')
        with open(self.IMAGE_DIRECTORY + 'boot.ipxe', "w") as ff:
            ff.write(file_content)

    @classmethod
    def get_images(cls):
        """Get all images that are of this class type."""
        # Get all images
        images = ImageManager.get_created_images()

        # Instantiate None class_image array
        class_images = None
        # If there is images
        if images:
            # Get all class images
            class_images = [image for image in images if image.image_class == cls.__name__]

        # Return all class images
        return class_images

    @classmethod
    def create_image_from_parameters(cls):
        """Getting all the image building arguments from a dictionary

        :param image_dict: The dictionary of parameters
        :type image_dict: str
        """
        logging.info('Parsing input parameters...')

    #####################
    # CLI reserved part #
    #####################

    def cli_display_info(self):
        """Display informations about an image"""

        # Print image name
        print(' • Image name: ' + self.name)

        # Get all attributs in a dictionary
        attributes_dictionary = dict(self.__dict__)

        # Delete name because it was already printed
        del attributes_dictionary['name']

        # For each element of the dictionary except the last
        for i in range(0, len(attributes_dictionary.items()) - 1):
            print('     ├── ' + str(list(attributes_dictionary.keys())[i]) + ': ' + str(list(attributes_dictionary.values())[i]))

        # For the last tuple element of the list
        print('     └── ' + str(list(attributes_dictionary.keys())[-1]) + ': ' + str(list(attributes_dictionary.values())[-1]))

    @staticmethod
    def cli_add_packages():
        """Ask user for a list of packages"""
        ask_module('Give a list of packages separated by spaces.', 'Exemple: \'package1 package2 package3 ...\' ')

        while True:

            # Get packages
            package_list = input('-->: ').split()

            logging.debug('Checking that requested packages exists...')
            # For each package
            for package_name in package_list:
                try:
                    # Check packages availability
                    logging.debug('Executing \'subprocess.check_output(\'dnf list \'' + package_name + ' | grep ' + package_name + ', shell=True)\'')
                    subprocess.check_output('dnf list ' + package_name + ' | grep ' + package_name, shell=True)
                    # Return the list of packages
                    return package_list

                # If there is not running process for image creator instance pid
                except subprocess.CalledProcessError:
                    inform("Package \'" + package_name + '\' not available, try again.')
