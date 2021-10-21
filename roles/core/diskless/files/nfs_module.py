# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# nfs_module module:
#    This module allow contain a class used for creating nfs
#    images with the diskless images
#    management script.
#
# 1.3.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>, Benoit Leveugle <benoit.leveugle@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license

# Import base modules
from ClusterShell.NodeSet import NodeSet
import os
import shutil
import crypt
import logging
from subprocess import check_output, CalledProcessError


# Import diskless modules
from diskless.modules.base_module import Image
from diskless.kernel_manager import KernelManager
from diskless.image_manager import ImageManager
from diskless.utils import Color, printc, select_from_list, inform, warn, ask_module, ok


# Class representing an nfs staging image
class NfsStagingImage(Image):

    NFS_DIRECTORY = '/diskless/images/nfsimages/staging/'

    # Class constructor
    def __init__(self, name, password=None, kernel=None, additional_packages=None, release_version=None):
        super().__init__(name, password, kernel, additional_packages, release_version)

    # Create new staging image
    def create_new_image(self, password, kernel, additional_packages, release_version):
        super().create_new_image()

        if not isinstance(password, str) or len(password.split()) > 1:
            raise ValueError('Invalid password format parameter value')
        self.password = password

        if kernel not in KernelManager.get_available_kernels():
            raise ValueError('Invalid kernel parameter value')
        self.kernel = kernel
        self.image = 'initramfs-kernel-' + self.kernel.replace('vmlinuz-', '')

        if additional_packages is not None:
            for package_name in additional_packages:
                try:
                    # Check packages availability
                    logging.debug('Executing \'subprocess.check_output(\'dnf list \'' + package_name + ' | grep ' + package_name + ', shell=True)\'')
                    check_output('dnf list ' + package_name + ' | grep ' + package_name, shell=True)

                # If there is not running process for image creator instance pid
                except CalledProcessError:
                    raise ValueError('Invalid additional_packages parameter value')

            self.additional_packages = additional_packages

        if release_version is not None:
            self.release_version = release_version

        self.NFS_DIRECTORY = NfsStagingImage.NFS_DIRECTORY + self.name + '/'

        # Generate image files
        self.generate_files()

    # Generate staging image files
    def generate_files(self):
        super().generate_files()
        self.create_image_folders()
        self.generate_file_system()
        # Add password set up
        self.set_image_password()
        self.generate_ipxe_boot_file()

    # Remove files associated with the NFS image
    def remove_files(self):
        super().remove_files()

        logging.debug('Executing \'rm -rf ' + self.NFS_DIRECTORY + '\'')
        shutil.rmtree(self.NFS_DIRECTORY)

    # Clone the image into another image
    def clone(self, clone_name):

        super().clone(clone_name)

        # Clone directories path
        CLONE_IMAGE_DIRECTORY = Image.IMAGES_DIRECTORY + clone_name + '/'
        CLONE_NFS_DIRECTORY = NfsStagingImage.NFS_DIRECTORY + clone_name + '/'

        # Copying image directory for the clone
        logging.debug('Copying directory ' + self.IMAGE_DIRECTORY + ' into ' + CLONE_IMAGE_DIRECTORY)
        logging.debug('Executing \'cp -r ' + self.IMAGE_DIRECTORY + ' ' + CLONE_IMAGE_DIRECTORY + '\'')
        shutil.copytree(self.IMAGE_DIRECTORY, CLONE_IMAGE_DIRECTORY)

        # Copying nfs directory for the clone
        logging.debug('Copying directory ' + self.NFS_DIRECTORY + ' into ' + CLONE_NFS_DIRECTORY)
        logging.debug('Executing \'cp -r ' + self.NFS_DIRECTORY + ' ' + CLONE_NFS_DIRECTORY + '\'')

        # Don't crash copying symlinks because they can point to non existing ressources
        # (it is not a booted file system)
        shutil.copytree(self.NFS_DIRECTORY, CLONE_NFS_DIRECTORY, symlinks=True)

        # Create a clone object
        clone = NfsStagingImage(clone_name)

        # Change the clone attribute values
        clone.name = clone_name
        clone.IMAGE_DIRECTORY = CLONE_IMAGE_DIRECTORY
        clone.NFS_DIRECTORY = CLONE_NFS_DIRECTORY

        # Register the clone to update it's image_data file values
        clone.register_image()

        # Update the boot.ipxe file content
        clone.generate_ipxe_boot_file()

    # Create image base folders
    def create_image_folders(self):
        super().create_image_folders()
        # Create the specific nfs image directory
        logging.debug('Executing \'mkdir ' + self.NFS_DIRECTORY + '\'')
        os.mkdir(self.NFS_DIRECTORY)

    # Generate image file system
    def generate_file_system(self):
        super().generate_file_system()

        if hasattr(self, 'release_version'):
            release = '--releasever=' + self.release_version
        else:
            release = ''

        # Create file system with dnf
        logging.debug('Executing \'dnf groupinstall ' + release + ' -y "core" --releasever=8 --setopt=module_platform_id=platform:el8 --installroot=' + self.NFS_DIRECTORY + '\'')
        os.system('dnf groupinstall ' + release + ' -y "core" --releasever=8 --setopt=module_platform_id=platform:el8 --installroot=' + self.NFS_DIRECTORY)

        # If there are additional packages to install
        if hasattr(self, 'additional_packages'):
            # Install additional packages in installroot directory

            packages = ''
            for package in self.additional_packages:
                packages = packages + ' ' + package

            logging.debug('Executing \'dnf install ' + release + ' -y --installroot=' + self.NFS_DIRECTORY + ' ' + packages + '\'')
            os.system('dnf install ' + release + ' -y --installroot=' + self.NFS_DIRECTORY + ' ' + packages)

    # Set a password for the image
    # Staging images need a password
    def set_image_password(self):
        logging.info('Setting up image \'' + self.name + '\' password')

        # Create hash with clear password
        self.password = crypt.crypt(self.password, crypt.METHOD_SHA512)

        # Create new password file content
        with open(self.NFS_DIRECTORY + 'etc/shadow', 'r') as ff:
            newText = ff.read().replace('root:*', 'root:' + self.password)
            # Write new passord file content
        with open(self.NFS_DIRECTORY + 'etc/shadow', "w") as ff:
            ff.write(newText)

    # Clean all image files without image object when an image is corrupted
    @staticmethod
    def clean(image_name):
        Image.clean(image_name)

        if os.path.isdir(Image.IMAGES_DIRECTORY + image_name):
            logging.debug(Image.IMAGES_DIRECTORY + image_name + ' is a directory')
            logging.debug('Executing \'rm -rf ' + Image.IMAGES_DIRECTORY + image_name + '\'')
            shutil.rmtree(Image.IMAGES_DIRECTORY + image_name)

        if os.path.isdir(NfsStagingImage.NFS_DIRECTORY + image_name):
            logging.debug(NfsStagingImage.NFS_DIRECTORY + image_name + ' is a directory')
            logging.debug('Executing \'rm -rf ' + NfsStagingImage.NFS_DIRECTORY + image_name + '\'')
            shutil.rmtree(NfsStagingImage.NFS_DIRECTORY + image_name)

    # Get the parameters from a dictionary
    @classmethod
    def create_image_from_parameters(cls, image_dict):
        super().create_image_from_parameters()

        # Check that there are all mandatory the parameters
        if not all(key in image_dict for key in ['name', 'password', 'kernel']):
            raise ValueError('Invalid set of parameters')

        # Getting attributes from the dictionary
        name = str(image_dict['name'])
        password = str(image_dict['password'])
        kernel = image_dict['kernel']

        if 'additional_packages' in image_dict:
            additional_packages = image_dict['additional_packages']
        else:
            additional_packages = None

        if 'release_version' in image_dict:
            release_version = str(image_dict['release_version'])
        else:
            release_version = None

        # Create the new image with the parameters
        cli_construct_nfsstaging_image(name, password, kernel, additional_packages, release_version)

    @staticmethod
    def get_boot_file_template():
        """Get the class boot file template.
        This method must be redefined in all Image subclasses."""
        return '''#!ipxe
echo |
echo | Entering diskless/images/{image_name}/boot.ipxe
echo |
set image-kernel {image_kernel}
set image-initramfs {image_initramfs}
echo | Now starting staging nfs image boot.
echo |
echo | Parameters used:
echo | > Image target: {image_name}
echo | > Console: ${{eq-console}}
echo | > Additional kernel parameters: ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}
echo |
echo | Loading linux ...
kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux=0 text=1 root=nfs:${{next-server}}:/diskless/images/nfsimages/staging/{image_name},vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4
echo | Loading initial ramdisk ...
initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}
echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+
sleep 4
boot
'''


# Class representing an nfs golden image
class NfsGoldenImage(Image):

    NFS_DIRECTORY = '/diskless/images/nfsimages/golden/'

    # Class constructor
    def __init__(self, name, staging_image=None):
        super().__init__(name, staging_image)

    # Create new golden image
    def create_new_image(self, staging_image):
        super().create_new_image()

        # Checking all parameters compliance
        if not ImageManager.is_image(staging_image.name):
            raise ValueError('Invalid staging_image parameter value')

        # Set image attributes before creation
        self.kernel = staging_image.kernel
        self.image = 'initramfs-kernel-' + self.kernel.replace('vmlinuz-', '')
        self.password = staging_image.password

        if hasattr(staging_image, 'additional_packages'):
            self.additional_packages = staging_image.additional_packages

        if hasattr(staging_image, 'release_version'):
            self.release_version = staging_image.release_version

        self.nodes = NodeSet()
        self.NFS_DIRECTORY = NfsGoldenImage.NFS_DIRECTORY + self.name + '/'

        # Generate image files
        self.generate_files(staging_image)

    def get_existing_image(self):
        super().get_existing_image()
        # Convert string node set into NodeSet object
        self.nodes = NodeSet(self.nodes)

    # Generate golden image files
    def generate_files(self, staging_image):
        super().generate_files()
        self.create_image_folders()
        self.generate_file_system(staging_image)
        super().generate_ipxe_boot_file()

    def create_image_folders(self):
        super().create_image_folders()
        logging.debug('Executing \'mkdir -p ' + self.NFS_DIRECTORY + 'nodes\'')
        os.makedirs(self.NFS_DIRECTORY + 'nodes')

    def generate_file_system(self, staging_image):
        super().generate_file_system()
        logging.info('Cloning staging image to golden')
        logging.debug('Executing \'cp -a ' + staging_image.NFS_DIRECTORY + ' ' + self.NFS_DIRECTORY + 'image/\'')
        os.system('cp -a ' + staging_image.NFS_DIRECTORY + ' ' + self.NFS_DIRECTORY + 'image/')

    # List nodes associated with nfs golden image
    def get_nodes(self):
        return self.nodes

    # Add nodes to the image
    def add_nodes(self, nodes_range):
        logging.info('Cloning nodes, this may take some time...')

        # For each specified node
        for node in NodeSet(nodes_range):
            # If the node is not already in the nodeset
            if str(node) not in self.nodes:

                logging.info("Working on node: " + str(node))

                # Copy golden base image for the specified nodes
                logging.debug('Executing \'cp -a ' + self.NFS_DIRECTORY + 'image/ ' + self.NFS_DIRECTORY + 'nodes/' + node + '\'')
                os.system('cp -a ' + self.NFS_DIRECTORY + 'image/ ' + self.NFS_DIRECTORY + 'nodes/' + node)

        # Updatde node list
        self.nodes.add(nodes_range)

        # Register image with new values
        self.register_image()

    # Remove nodes from the golden image
    def remove_nodes(self, nodes_range):
        try:
            self.nodes.remove(nodes_range)

            logging.info('Deleting nodes, this may take some time...')
            # For each node
            for node in NodeSet(nodes_range):
                logging.info('Working on node: ' + str(node))
                # Remove node directory
                logging.debug('Executing \'rm -rf ' + self.NFS_DIRECTORY + '/nodes/' + node + '\'')
                shutil.rmtree(self.NFS_DIRECTORY + '/nodes/' + node)

            # Register image with new values
            self.register_image()

        except KeyError:
            raise KeyError("NodeSet to remove is not in image NodeSet !")

    # Remove files associated with the NFS image
    def remove_files(self):
        super().remove_files()

        logging.debug('Executing \'rm -rf ' + self.NFS_DIRECTORY + '\'')
        shutil.rmtree(self.NFS_DIRECTORY)

    # Clone the image into another image
    def clone(self, clone_name):

        super().clone(clone_name)

        # Clone directories path
        CLONE_IMAGE_DIRECTORY = Image.IMAGES_DIRECTORY + clone_name + '/'
        CLONE_NFS_DIRECTORY = NfsGoldenImage.NFS_DIRECTORY + clone_name + '/'

        # Copying image directory for the clone
        logging.debug('Copying directory ' + self.IMAGE_DIRECTORY + ' into ' + CLONE_IMAGE_DIRECTORY)
        logging.debug('Executing \'cp -r ' + self.IMAGE_DIRECTORY + ' ' + CLONE_IMAGE_DIRECTORY + '\'')
        shutil.copytree(self.IMAGE_DIRECTORY, CLONE_IMAGE_DIRECTORY)

        # Copying nfs directory for the clone
        logging.debug('Copying directory ' + self.NFS_DIRECTORY + ' into ' + CLONE_NFS_DIRECTORY)
        logging.debug('Executing \'cp -r ' + self.NFS_DIRECTORY + ' ' + CLONE_NFS_DIRECTORY + '\'')

        # Don't crash copying symlinks because they can point to non existing ressources
        # (it is not a booted file system)
        shutil.copytree(self.NFS_DIRECTORY, CLONE_NFS_DIRECTORY, symlinks=True)

        # Create a clone object
        clone = NfsGoldenImage(clone_name)

        # Change the clone attribute values
        clone.name = clone_name
        clone.IMAGE_DIRECTORY = CLONE_IMAGE_DIRECTORY
        clone.NFS_DIRECTORY = CLONE_NFS_DIRECTORY

        # Register the clone to update it's image_data file values
        clone.register_image()

        # Update the boot.ipxe file content
        clone.generate_ipxe_boot_file()

    # Clean all image files without image object when an image is corrupted
    @staticmethod
    def clean(image_name):
        Image.clean(image_name)

        if os.path.isdir(Image.IMAGES_DIRECTORY + image_name):
            logging.debug(Image.IMAGES_DIRECTORY + image_name + ' is a directory')
            logging.debug('Executing \'rm -rf ' + Image.IMAGES_DIRECTORY + image_name + '\'')
            shutil.rmtree(Image.IMAGES_DIRECTORY + image_name)

        if os.path.isdir(NfsGoldenImage.NFS_DIRECTORY + image_name):
            logging.debug(NfsGoldenImage.NFS_DIRECTORY + image_name + ' is a directory')
            logging.debug('Executing \'rm -rf ' + NfsGoldenImage.NFS_DIRECTORY + image_name + '\'')
            shutil.rmtree(NfsGoldenImage.NFS_DIRECTORY + image_name)

    @staticmethod
    def get_boot_file_template():
        """Get the class boot file template.
        This method must be redefined in all Image subclasses."""
        return '''#!ipxe
echo |
echo | Entering diskless/images/{image_name}/boot.ipxe
echo |
set image-kernel {image_kernel}
set image-initramfs {image_initramfs}
echo | Now starting golden nfs image boot.
echo |
echo | Parameters used:
echo | > Image target: {image_name}
echo | > Image type: nfs in golden shared mode
echo | > Console: ${{eq-console}}
echo | > Additional kernel parameters: ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}
echo |
echo | Loading linux ...
kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux=0 text=1 root=nfs:${{next-server}}:/diskless/images/nfsimages/golden/{image_name}/nodes/${{hostname}},vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4
echo | Loading initial ramdisk ...
initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}
echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+
sleep 4
boot
'''


#####################
# CLI reserved part #
#####################

def cli_menu():

    # Display main menu
    printc('\n == NFS image module == ', Color.GREEN)

    ask_module('Select an action:')
    action_list = ['Generate a new nfs staging image', 'Generate a new nfs golden image from a staging image', 'Manage nodes of a golden image']

    while True:
        action = select_from_list(action_list)

        try:
            if action == 'Generate a new nfs staging image':
                cli_create_nfsstaging_image_questions()
            elif action == 'Generate a new nfs golden image from a staging image':
                cli_create_nfsgolden_image_questions()
            else:
                cli_manage_nodes()
            break

        # Catch the error in order to stay in this menu if an error appends
        except UserWarning as e:
            inform(str(e))


def cli_create_nfsstaging_image_questions():
    """Getting all the image building arguments from the user shell."""

    # Get available kernels
    kernel_list = KernelManager.get_available_kernels()

    # If there are no kernels raise an exception
    if not kernel_list:
        raise UserWarning('No kernel available')

    # Condition to test if image name is compliant
    ask_module('Give a name for your image')
    while True:

        # Get new image name
        selected_image_name = input('-->: ').replace(" ", "")

        if selected_image_name == '':
            inform('Image name cannot be empty !')

        if not ImageManager.is_image(selected_image_name):
            break

        # Else
        inform('Image ' + selected_image_name + ' already exist, use another image name.')

    # Select the kernel to use
    ask_module('Select your kernel:')
    selected_kernel = select_from_list(kernel_list)

    # Manage password
    ask_module('Give a password for your image')
    selected_password = input('Please enter clear root password of the new image: ').replace(" ", "")

    # Propose to user to install additional packages
    ask_module('Do you want to customize your image with additional packages? (yes/no)')
    while 'additional_packages' not in locals():
        choice = input('-->: ')
        # Install addictional packages
        if choice in {'yes', 'y'}:
            # Get package list from user
            additional_packages = Image.cli_add_packages()
        # Don't install additional packages
        elif choice in {'no', 'n'}:
            additional_packages = None
        else:
            inform('Invalid entry !')

    # Propose to user to specify a release version
    ask_module('Specify a release version for installation (left empty to not use the --relasever option)')
    release_version = input('-->: ')
    if release_version == '':
        release_version = None

    cli_construct_nfsstaging_image(selected_image_name, selected_password, selected_kernel, additional_packages, release_version)


def cli_construct_nfsstaging_image(name, password, kernel, additional_packages, release_version):
    """Create the new nfs staging image"""

    # Confirm image creation
    ask_module('Would you like to create a new nfs staging image with the following attributes: (yes/no)')
    print('  ├── Image name: \t\t' + name)
    print('  ├── Image password : \t\t' + password)

    # Print additional packages if there is
    if additional_packages is not None:
        print('  ├── Additional packages: \t' + str(additional_packages))

    # Print release version if there is one
    if release_version is not None:
        print('  ├── Release version: \t\t' + release_version)

    print('  └── Image kernel: \t\t' + kernel)

    while True:
        confirmation = input('-->: ').replace(" ", "")

        # Image creation confirmed
        if confirmation in {'yes', 'y'}:

            try:
                # Create the image object
                NfsStagingImage(name, password, kernel, additional_packages, release_version)
                ok()
                return

            # If an exception occurs during the image creation process
            except Exception as e:
                # First, clean previous uncompleted installation
                ImageManager.clean_installation(name)
                warn('An exception occurred durring the installation process !',
                     'The exception was: ' + str(e))

            inform('Would you like to retry the installation with the same parameters (yes/no)?',
                   '(If you exit now you will lost all the image creation parameters you entered.)')

        elif confirmation in {'no', 'n'}:
            inform('Image creation cancelled, return to main menu.')
            return

        else:
            inform('Invalid confirmation !')


# Create a golden image from a staging image
def cli_create_nfsgolden_image_questions():
    """Getting all the image building arguments from the user shell."""

    # Get all staging images
    staging_images = NfsStagingImage.get_images()

    # Check if there are staging images
    if not staging_images:
        raise UserWarning('No nfs staging images. Golden image creation require an nfs staging image.')

    # Get staging images names
    staging_images_names = [staging_image.name for staging_image in staging_images]

    # Select a staging image for golden image creation
    ask_module('Select the nfs image to use for golden image creation:')
    staging_image_name = select_from_list(staging_images_names)
    staging_image = ImageManager.get_created_image(staging_image_name)

    # Condition to test if image name is compliant
    ask_module(' Give a name for your image')
    while True:

        # Get new image name
        selected_image_name = input('-->: ').replace(" ", "")

        if selected_image_name == '':
            inform('Image name cannot be empty !')

        elif ImageManager.is_image(selected_image_name):
            inform('Image ' + selected_image_name + ' already exist, use another image name.')

        else:
            break

    cli_construct_nfsgolden_image(selected_image_name, staging_image)


def cli_construct_nfsgolden_image(name, staging_image):
    """Create the new nfs golden image."""

    # Confirm image creation
    ask_module(' Would you like to create a new nfs golden image with the following attributes: (yes/no)')
    print('  ├── Image name: \t\t' + name)
    print('  └── Staging image from: \t' + staging_image.name)

    while True:
        confirmation = input('-->: ').replace(" ", "")

        # Image creation confirmed
        if confirmation in {'yes', 'y'}:

            try:
                # Create the image object
                NfsGoldenImage(name, staging_image)
                ok()
                return

            # If an error occurs during the image creation
            except Exception as e:
                # First, clean previous uncompleted installation
                ImageManager.clean_installation(name)
                warn('An exception occurs durring the installation process !',
                     'The exception was: ' + str(e))

            inform('Would you like to retry the installation with the same parameters (yes/no)?',
                   '(If you exit now you will lost all the image creation parameters you entered.)')

        elif confirmation in {'no', 'n'}:
            inform('Image creation cancelled, return to main menu.')
            return

        else:
            inform('Invalid confirmation !')


# Manage a golden image nodes
def cli_manage_nodes():
    # Get all golden images
    golden_images = NfsGoldenImage.get_images()

    if not golden_images:
        raise UserWarning('No nfs golden image to manage.')

    # Get golden images names
    golden_images_names = [golden_image.name for golden_image in golden_images]

    # Select the golden image to manage from list
    ask_module('Select the golden image to manage:')
    golden_image_name = select_from_list(golden_images_names)
    golden_image = ImageManager.get_created_image(golden_image_name)

    # Choose an action for nodes management
    ask_module('Manages nodes of image ' + golden_image_name)
    action_list = ['List nodes with the image', 'Add nodes with the image', 'Remove nodes with the image']
    action = select_from_list(action_list)

    # Print golden image nodes
    if action == 'List nodes with the image':
        nodeset = golden_image.get_nodes()
        print(nodeset)
        ok()

    # Add some nodes to the image
    elif action == 'Add nodes with the image':
        if golden_image.nodes.__len__() == 0:
            ask_module('Actualy there are no nodes for this image', 'Please enter nodes range to add:')
        else:
            ask_module('Actual image NodeSet is: ' + str(golden_image.nodes), 'Please enter nodes range to add:')

        while True:
            nodes_range = input('-->: ').replace(" ", "")
            # Test if nodes_range is a valid range
            try:
                golden_image.add_nodes(nodes_range)
                ok('Nodes added !')
                break

            except KeyError:
                inform("Invalid input value, please enter another range value.")

    # Delete nodes from image
    elif action == 'Remove nodes with the image':
        ask_module('Please enter nodes range to remove:')
        while True:
            nodes_range = input('-->: ').replace(" ", "")
            # Test if nodes_range is a valid range
            try:
                golden_image.remove_nodes(nodes_range)
                ok('Nodes removed !')
                break

            except KeyError:
                inform("Invalid input value, please enter another range value.")
