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
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license

# Import base modules
from ClusterShell.NodeSet import NodeSet
import os
import shutil
import yaml
import crypt
import logging
from datetime import datetime

# Import diskless modules
from base_module import Image
from kernel_manager import KernelManager
from image_manager import ImageManager
from utils import *


# Class representing an nfs staging image
class NfsStagingImage(Image):

    # Class constructor
    def __init__(self, name, password = None, kernel = None):
        super().__init__(name, password, kernel)

    # Create new staging image
    def create_new_image(self, password, kernel):

        # Checking all parameters
        # Check name format
        if len(password.split()) > 1 or not isinstance(password, str):
            raise ValueError('Unexpected password format.')

        # Check kernel attribute
        if not kernel in KernelManager.get_available_kernels():
            raise ValueError('Invalid kernel.')

        # Set image attributes before creation
        self.kernel = kernel
        self.image = 'initramfs-kernel-'+ self.kernel.replace('vmlinuz-', '')
        self.password = password
       
        # Generate image files 
        self.generate_files()
        
    # Generate staging image files
    def generate_files(self):
        logging.info('Generating image files')
        self.create_image_folders()
        self.generate_ipxe_boot_file()
        self.generate_file_system()
        # Add password set up 
        self.set_image_password()

    # Remove files associated with the NFS image
    def remove_files(self):
        super().remove_files()
        # Remove specific nfs staging image directory
        if os.path.isdir('/diskless/nfsimages/' + self.name):
            shutil.rmtree('/diskless/nfsimages/' + self.name)

    # Create image base folders
    def create_image_folders(self):
        super().create_image_folders()
        # Create the specific nfs image directory
        os.makedirs('/diskless/nfsimages/' + self.name + '/staging')

    # Generate image file system
    def generate_file_system(self):
        super().generate_file_system()
        # create file system with dnf
        os.system('dnf groupinstall -y "core" --releasever=8 --setopt=module_platform_id=platform:el8 --installroot=/diskless/nfsimages/'+ self.name+ '/staging')

    # Set a password for the image
    # Staging images need a password
    def set_image_password(self):
        logging.info('Setting up a password for the image')
        
        # Create hash with clear password
        self.password = crypt.crypt(self.password, crypt.METHOD_SHA512)
        
        # Create new password file content
        with open('/diskless/nfsimages/' + self.name + '/staging/etc/shadow', 'r') as ff:
            newText = ff.read().replace('root:*', 'root:' + self.password)
            # Write new passord file content
        with open('/diskless/nfsimages/' + self.name + '/staging/etc/shadow', "w") as ff:
            ff.write(newText)

    # Clean all image files without image object when an image is corrupted
    @staticmethod
    def clean(image_name):

        if os.path.isdir(Image.IMAGES_DIRECTORY + image_name):
            shutil.rmtree(Image.IMAGES_DIRECTORY + image_name)

        if os.path.isdir('/diskless/nfsimages/' + image_name):
            shutil.rmtree('/diskless/nfsimages/' + image_name)

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
kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux=0 text=1 root=nfs:${{next-server}}:/diskless/nfsimages/{image_name}/staging/,vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4 
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

    image_type = 'nfs'

    # Class constructor
    def __init__(self, name, staging_image = None):
        super().__init__(name, staging_image)

    # Create new golden image
    def create_new_image(self, staging_image):

        # Set image attributes before creation
        self.kernel = staging_image.kernel
        self.image = 'initramfs-kernel-'+ self.kernel.replace('vmlinuz-', '')
        self.nodes = NodeSet()

        # Generate image files
        self.generate_files(staging_image)

    def get_existing_image(self):
        super().get_existing_image()
        # Convert string node set into NodeSet object
        self.nodes = NodeSet(self.nodes)

    # Generate golden image files
    def generate_files(self, staging_image):
        self.create_image_folders()
        super().generate_ipxe_boot_file()
        self.generate_file_system(staging_image)

    def create_image_folders(self):
        os.makedirs('/diskless/nfsimages/' + self.name + '/nodes')

    def generate_file_system(self, staging_image):
        logging.info('Cloning staging image to golden')
        os.system('cp -a /diskless/nfsimages/' + staging_image.name + '/staging /diskless/nfsimages/' + self.name +'/golden')

    # List nodes associated with nfs golden image
    def get_nodes(self):
        return self.nodes

    # Add nodes to the image
    def add_nodes(self, nodes_range):

        self.nodes.add(nodes_range)

        logging.info('Cloning, this may take some time...')
        # For each specified node
        for node in NodeSet(nodes_range):
            logging.info("Working on node: " + str(node))
            # Copy golden base image for the specified nodes
            os.system('cp -a /diskless/nfsimages/' + self.name + '/golden '
                       + '/diskless/nfsimages/' + self.name + '/nodes/' + node)
        
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
                shutil.rmtree('/diskless/nfsimages/' + self.name + '/nodes/' + node)

            # Register image with new values
            self.register_image()
        
        except KeyError as err:
            raise KeyError("NodeSet to remove is not in image NodeSet !")

    # Remove files associated with the NFS image
    def remove_files(self):
        super().remove_files()
        # Remove specific nfs golden image directory
        if os.path.isdir('/diskless/nfsimages/' + self.name):
            shutil.rmtree('/diskless/nfsimages/' + self.name)

    # Clean all image files without image object when an image is corrupted
    @staticmethod
    def clean(image_name):

        if os.path.isdir(Image.IMAGES_DIRECTORY + image_name):
            shutil.rmtree(Image.IMAGES_DIRECTORY + image_name)

        if os.path.isdir('/diskless/nfsimages/' + image_name):
            shutil.rmtree('/diskless/nfsimages/' + image_name)

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
kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux=0 text=1 root=nfs:${{next-server}}:/diskless/nfsimages/{image_name}/nodes/${{hostname}},vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4
echo | Loading initial ramdisk ...
initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}
echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+
sleep 4
boot
'''
   

######################
## CLI reserved part##
######################

def cli_menu():
    # Display main menu
    printc('\n == NFS image module == \n', CGREEN)

    print(' 1 - Generate a new nfs staging image')
    print(' 2 - Generate a new nfs golden image from a staging image')
    print(' 3 - Manage nodes of a golden image')

    # Answer and get the action to execute
    print('\n Select an action')
    main_action = input('-->: ')
    print('')

    if main_action == '1':
        cli_create_staging_image()

    elif main_action == '2': 
        cli_create_golden_image()
    
    elif main_action == '3':
        cli_manage_nodes()

    # Bad entry
    else:
        raise UserWarning('\'' + main_action + '\' is not a valid entry. Please enter another value.')


def cli_create_staging_image():

    # Get available kernels
    kernel_list = KernelManager.get_available_kernels()
    
    # If there are no kernels aise an exception
    if not kernel_list:
        raise UserWarning('No kernel available')
   
    # Condition to test if image name is compliant
    while True:

        printc('[+] Give a name for your image', CGREEN)
        # Get new image name
        selected_image_name = input('-->: ').replace(" ", "")
        
        if not ImageManager.is_image(selected_image_name):
            break

        # Else
        print('Image ' + selected_image_name + ' already exist, use another image name.')

    # Select the kernel to use
    printc('\n[+] Select your kernel:', CGREEN)
    selected_kernel = select_from_list(kernel_list)
    
    # Manage password
    printc('\n[+] Give a password for your image', CGREEN)
    selected_password = input('Please enter clear root password of the new image: ').replace(" ", "")

    # Confirm image creation
    printc('\n[+] Would you like to create a new nfs staging image with the following attributes: (yes/no)', CGREEN)
    print('  ├── Image name: ' + selected_image_name)
    print('  ├── Image password : ' + selected_password)
    print('  └── Image kernel: ' + selected_kernel)

    confirmation = input('-->: ').replace(" ", "")

    if confirmation == 'yes':
       # Create the image object
        NfsStagingImage(selected_image_name, selected_password, selected_kernel)
        printc('\n[OK] Done.', CGREEN)

    elif confirmation == 'no':
        printc('\n[+] Image creation cancelled, return to main menu.', CYELLOW)
        return

    else:
        raise UserWarning('\nInvalid confirmation !')


# Create a golden image from a staging image
def cli_create_golden_image():
    # Get all staging images
    staging_images = NfsStagingImage.get_images()

    # Check if there are staging images
    if not staging_images:
        raise UserWarning('No nfs staging images. Golden image creation require an nfs staging image.')

    # Get staging images names
    staging_images_names = [staging_image.name for staging_image in staging_images]

    # Select a staging image for golden image creation
    printc('[+] Select the nfs image to use for golden image creation:', CGREEN)
    staging_image_name = select_from_list(staging_images_names)
    staging_image = ImageManager.get_created_image(staging_image_name)

    # Condition to test if image name is compliant
    while True:

        printc('\n[+] Give a name for your image', CGREEN)
        # Get new image name
        selected_image_name = input('-->: ').replace(" ", "")
        
        if not ImageManager.is_image(selected_image_name):
            break

        # Else
        print('Image ' + selected_image_name + ' already exist, use another image name.')

    # Confirm image creation
    printc('\n[+] Would you like to create a new nfs golden image with the following attributes: (yes/no)', CGREEN)
    print('  ├── Image name: ' + selected_image_name)
    print('  └── Staging image from: ' + staging_image.name)

    confirmation = input('-->: ').replace(" ", "")

    if confirmation == 'yes':
        # Create the image object
        NfsGoldenImage(selected_image_name, staging_image)
        printc('\n[OK] Done.', CGREEN)

    elif confirmation == 'no':
        printc('\nImage creation cancelled, return to main menu.', CYELLOW)
        return

    else:
        raise UserWarning('\nInvalid confirmation !')


# Manage a golden image nodes
def cli_manage_nodes():
    # Get all golden images
    golden_images = NfsGoldenImage.get_images()

    if not golden_images:
        raise UserWarning('No nfs golden image to manage.')

    # Get golden images names
    golden_images_names = [golden_image.name for golden_image in golden_images]

    # Select the golden image to manage from list
    printc('\n[+] Select the golden image to manage:', CGREEN)
    golden_image_name = select_from_list(golden_images_names)
    golden_image = ImageManager.get_created_image(golden_image_name)

    # Choose an action for nodes management
    printc('\n[+] Manages nodes of image ' + golden_image_name, CGREEN)
    print(' 1 - List nodes with the image')
    print(' 2 - Add nodes with the image')
    print(' 3 - Remove nodes with the image')

    action = input('-->: ')

    # Print golden image nodes
    if action == '1':
        nodeset = golden_image.get_nodes()
        print(nodeset)
        printc('\n[OK] Done.', CGREEN)

    # Add some nodes to the image
    elif action == '2':
        printc('\n[+] Actual image NodeSet is:' + str(golden_image.nodes), CGREEN)
        printc('[+] Please enter nodes range to add:', CGREEN)

        nodes_range = input('-->: ').replace(" ", "")
        # Test if nodes_range is a valid range
        try:
            golden_image.add_nodes(nodes_range)
            printc('\n[OK] Done.', CGREEN)

        except KeyError as err:
            raise UserWarning('The Node you have entered is not compliant.')
    
    # Delete nodes from image
    elif action == '3':
        printc('\n[+] Please enter nodes range to remove:', CGREEN)
        
        nodes_range = input('-->: ').replace(" ", "")
        # Test if nodes_range is a valid range
        try:
            golden_image.remove_nodes(nodes_range)
            printc('\n[OK] Done.', CGREEN)

        except KeyError as err:
            raise UserWarning('The Node you have entered is not compliant.')

    else:
        raise UserWarning('Not a valid entry')

    




