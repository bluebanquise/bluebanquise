# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# livenet_module module:
#    This module contains a class used for creating livenet
#    images. This type of image allow to load operating system
#    in ram.
#
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import base modules
import os
import shutil
import yaml
import crypt
import logging
from datetime import datetime
from enum import Enum, auto

# Import diskless modules
from base_module import Image
from kernel_manager import KernelManager
from image_manager import ImageManager
from utils import *


# Class representing a livenet image
class LivenetImage(Image):

    # Enumeration of livenet types
    class Type(Enum):
        # Values are auto because we don't care about
        STANDARD = auto()
        SMALL = auto()
        CORE = auto()

    # Image working directory, specific for livenet images
    WORKING_DIRECTORY = '/diskless/workdir/'
    MOUNT_DIRECTORY = '/diskless/mntdir/'

    # Define the allowed sizes range
    MAX_LIVENET_SIZE = 50000 # 50 Gigas
    MIN_LIVENET_SIZE = 100 # 100 Megabytes

    # Class constructor
    def __init__(self, name, password = None, kernel = None, livenet_type = None, livenet_size = None):
        super().__init__(name, password, kernel, livenet_type, livenet_size)

    def create_new_image(self, password, kernel, livenet_type, livenet_size):

        # Checking all parameters
        # Check name format
        if len(password.split()) > 1 or not isinstance(password, str):
            raise ValueError('Unexpected password format.')
 
        # Check kernel attribute
        if not kernel in KernelManager.get_available_kernels():
            raise ValueError('Invalid kernel.')

        # Check livenet type
        if livenet_type is not LivenetImage.Type.STANDARD and livenet_type is not LivenetImage.Type.SMALL and livenet_type is not LivenetImage.Type.CORE:
            raise ValueError('Invalid livenet type.')

        # Check livenet size
        if not isinstance(livenet_size, str) or int(livenet_size) < LivenetImage.MIN_LIVENET_SIZE or int(livenet_size) > LivenetImage.MAX_LIVENET_SIZE:
            raise ValueError('Invalid livenet size.')

        # Set image attributes before creation
        self.kernel = kernel
        self.image = 'initramfs-kernel-'+ self.kernel.replace('vmlinuz-', '')
        self.password = password

        self.livenet_type = livenet_type
        self.livenet_size = livenet_size

        # A livenet can be mounted on it's personnal mount directory
        # in order to perform actions on it.
        self.is_mounted = False

        # Generate image files 
        self.generate_files()

    def generate_files(self):
        logging.info('Starting generating image files...')
    
        self.generate_file_system()
        self.generate_ipxe_boot_file()
    
    def generate_file_system(self):
        super().generate_file_system()
        # Generaéte operating system of the image
        self.generate_operating_system()
        # Set up image password before after generating operating system
        self.set_image_password(LivenetImage.WORKING_DIRECTORY + self.name)
        # Generate image squashfs.img
        self.generate_squashfs()

    # Use dnf command in order to create the image operating system
    def generate_operating_system(self):
        logging.info('Generating operating system')
        # create image personnal working directory
        os.mkdir(LivenetImage.WORKING_DIRECTORY + self.name)

        # Generate desired image file system
        if self.livenet_type == LivenetImage.Type.STANDARD:
            os.system('dnf groupinstall -y "core"  --releasever=8 --setopt=module_platform_id=platform:el8 --installroot=' + LivenetImage.WORKING_DIRECTORY + self.name + ' --exclude selinux-policy-targeted --exclude selinux-policy-mls')
        elif self.livenet_type == LivenetImage.Type.SMALL:
            os.system('dnf install -y dnf yum iproute procps-ng openssh-server NetworkManager --installroot=' + LivenetImage.WORKING_DIRECTORY + self.name + ' --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --exclude selinux-policy-targeted --exclude selinux-policy-mls --setopt=module_platform_id=platform:el8 --nobest')
        elif self.livenet_type == LivenetImage.Type.CORE:
            os.system('dnf install -y iproute procps-ng openssh-server --installroot=' + LivenetImage.WORKING_DIRECTORY + self.name +' --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --exclude selinux-policy-targeted --exclude selinux-policy-mls --setopt=module_platform_id=platform:el8 --nobest')

    # Generate the image squashfs image after creating the image rootfs image
    # The operating system need to be previoulsy created by the 
    # generate_operating_system method.
    def generate_squashfs(self):
        logging.info('Generating squashfs image')
        # Create the directory that will contain the rootfs image
        os.makedirs(self.IMAGE_DIRECTORY + '/tosquash/LiveOS')

        # Create the rootfs image with the image size in Mb
        os.system('dd if=/dev/zero of=' + self.IMAGE_DIRECTORY + '/tosquash/LiveOS/rootfs.img bs=1M count=' + self.livenet_size)
        
        # Format the rootfs.img in mkfs format
        os.system('mkfs.xfs ' + self.IMAGE_DIRECTORY + '/tosquash/LiveOS/rootfs.img')

        # Create a mounting directory for rootfs.img
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name)

        # Mount rootfs.img in order to put inside the operating system
        os.system('mount -o loop ' + self.IMAGE_DIRECTORY + '/tosquash/LiveOS/rootfs.img ' + LivenetImage.MOUNT_DIRECTORY + self.name)

        # Put the operating system inside rootfs.img
        os.system('cp -r ' +  LivenetImage.WORKING_DIRECTORY + self.name + '/* ' + LivenetImage.MOUNT_DIRECTORY + self.name)
        
        # Removing useless working directory because we don't need it anymore
        shutil.rmtree(LivenetImage.WORKING_DIRECTORY + self.name)

        # Unmount rootfs.img file
        os.system('umount ' + LivenetImage.MOUNT_DIRECTORY + self.name)

        # Remove mountage directory for rootfs.img
        shutil.rmtree(LivenetImage.MOUNT_DIRECTORY + self.name)

        # Create the squashfs.img that will contains LiveOS/rootfs.img
        os.system('mksquashfs ' + self.IMAGE_DIRECTORY + '/tosquash ' + self.IMAGE_DIRECTORY + '/squashfs.img')
        
        # Removing not squashed LiveOS/rootfs.img, because we don't need it anymore
        # (In fact the rootfs.img is now inside the squashfs.img)
        shutil.rmtree(self.IMAGE_DIRECTORY + '/tosquash')

    # Set a password for the image
    # Staging images need a password
    def set_image_password(self, mountage_directory):
        logging.info('Setting up a password for the image')

        # Create hash with clear password
        self.password = crypt.crypt(self.password, crypt.METHOD_SHA512)
        
        # Create new password file content
        with open(mountage_directory + '/etc/shadow', 'r') as ff:
            newText = ff.read().replace('root:*', 'root:' + self.password)
            # Write new passord file content
        with open(mountage_directory + '/etc/shadow', "w") as ff:
            ff.write(newText)

    # Remove files associated with the NFS image
    def remove_files(self):

        # If the livenet image is currently mounted
        if self.is_mounted == True:
            # Unmount before removing files
            self.unmount()

        super().remove_files()

    # Mount the image to edit it
    def mount(self):
        """Mounting livenet image"""
        logging.info('Mounting livenet image ' + self.name)

        # Create image mounting directory
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name)

        # Create mountage point for squashfs
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name + '/squashfs')

        # Create mountage point for rootfs.img image
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name + '/mnt')

        # Create mountage point for system sys
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name + '/inventory')

        # Mounting squashfs on the squashfs mountage point
        os.system('mount ' + self.IMAGE_DIRECTORY +'/squashfs.img ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/squashfs')

        # Mounting rootfs.img on /mnt mountage point
        os.system('mount ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/squashfs/LiveOS/rootfs.img ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/mnt')

        # Mount diskless server proc on livenet image proc
        os.system('mount --bind /proc ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/mnt/proc')
        # Mount diskless server sys on livenet image sys
        os.system('mount --bind /sys ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/mnt/sys')

        # Create the ansible connection
        os.system('echo ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/mnt ansible_connection=chroot > ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/inventory/host')

        # Changing image mountage status
        self.is_mounted = True
        self.register_image()

    # Unmount the image when the editing is finished
    def unmount(self):
        """Unmounting livenet image"""
        logging.info('Unmounting livenet image ' + self.name)

        if self.is_mounted:
            # Unmounting image mounted proc and sys
            os.system('umount ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/mnt/{proc,sys}')

            # Unmounting image mounted mnt and squashfs
            os.system('umount ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/{mnt,squashfs}')

            # Removing image mount directory
            shutil.rmtree(LivenetImage.MOUNT_DIRECTORY + self.name)

        # Changing image mountage status
        self.is_mounted = False
        self.register_image()

    # Resize the livenet image image size
    def resize(self, new_size):
        logging.info('Start image resizing')

        # Image must be unmounted to resize it
        if self.is_mounted:
            raise ValueError('Cannot resize a mounted livenet image')

        # Check livenet size
        if not isinstance(new_size, str) or int(new_size) < LivenetImage.MIN_LIVENET_SIZE or int(new_size) > LivenetImage.MAX_LIVENET_SIZE:
            raise ValueError('Invalid livenet size')


        # Creating directories for mountages

        # Create mounting directory for the image
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name)

        # Create mounting directory for the existing squashfs image
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name + '/squashfs')

        # Create mounting directory for the existing rootfs image
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name + '/old_rootfs')

        # Create mounting directory for the new image
        os.mkdir(LivenetImage.MOUNT_DIRECTORY + self.name + '/rootfs')


        # Mount old rootfs on it's mountage point

        # First, mount squashfs inside the image squashfs mount directory
        os.system('mount ' + self.IMAGE_DIRECTORY +'/squashfs.img ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/squashfs')

        # Then, mount rootfs inside the image rootfs directory
        os.system('mount ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/squashfs/LiveOS/rootfs.img ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/old_rootfs')


        # Create the new rootfs image

        # Create working directory for the image
        os.makedirs(LivenetImage.WORKING_DIRECTORY + self.name + '/tosquash/LiveOS')

        # Create a new rootfs image
        os.system('dd if=/dev/zero of=/' + LivenetImage.WORKING_DIRECTORY + self.name + '/tosquash/LiveOS/rootfs.img bs=1M count=' + new_size)

        # Create a new livenet xfs file system
        os.system('mkfs.xfs ' + LivenetImage.WORKING_DIRECTORY + self.name + '/tosquash/LiveOS/rootfs.img')
        
        # Mount the new rootfs image on rootfs mounting directory
        os.system('mount ' + LivenetImage.WORKING_DIRECTORY + self.name + '/tosquash/LiveOS/rootfs.img ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/rootfs')

        # Copy old rootfs content into the new rootfs directory
        os.system('cp -r ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/old_rootfs/* ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/rootfs')

        # Unmounting new image mount directory
        os.system('umount ' + LivenetImage.MOUNT_DIRECTORY + self.name + '/*' )

        # Create new squashfs image
        
        # Remove old squashfs image
        os.remove(self.IMAGE_DIRECTORY + '/squashfs.img')

        # Create fresh squashfs.img file system with new rootfs.img
        os.system('mksquashfs ' + LivenetImage.WORKING_DIRECTORY + self.name + '/tosquash ' + self.IMAGE_DIRECTORY +'/squashfs.img')

        # Removing image mount directory
        shutil.rmtree(LivenetImage.MOUNT_DIRECTORY + self.name)

        # Removing image working directory
        shutil.rmtree(LivenetImage.WORKING_DIRECTORY + self.name)

        # Update image size attribute value
        self.livenet_size = new_size
        self.register_image()

        logging.info('Image was resized to ' + new_size + 'Mb')

    # We must redefine the method because we cannot register attributs as boolean
    def get_existing_image(self):
        super().get_existing_image()

        # Convert string is_mounted state into boolean equivalent
        if self.is_mounted == 'True':
            self.is_mounted = True
        elif self.is_mounted == 'False':
            self.is_mounted = False
                
    # Clean all image files without image object when an image is corrupted
    @staticmethod
    def clean(image_name):

        # Try cleaning image base directory
        if os.path.isdir(LivenetImage.IMAGES_DIRECTORY + image_name):
            shutil.rmtree(LivenetImage.IMAGES_DIRECTORY + image_name)

        # Try cleaning image working directory
        if os.path.isdir(LivenetImage.WORKING_DIRECTORY + image_name):
            shutil.rmtree(LivenetImage.WORKING_DIRECTORY + image_name)

        # Cleanings for mount directories
        if os.path.isdir(LivenetImage.MOUNT_DIRECTORY + image_name):
            os.system('umount ' + LivenetImage.MOUNT_DIRECTORY + image_name + '/mnt/*')
            os.system('umount ' + LivenetImage.MOUNT_DIRECTORY + image_name + '/*')
            shutil.rmtree(LivenetImage.MOUNT_DIRECTORY + image_name)
            
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
echo | Now starting livenet diskless sessions.
echo |
echo | Parameters used:
echo | > Image target: {image_name}
echo | > Console: ${{eq-console}}
echo | > Additional kernel parameters: ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}
echo |
echo | Loading linux ...
kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} root=live:http://${{next-server}}/preboot_execution_environment/diskless/images/{image_name}/squashfs.img rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4
echo | Loading initial ramdisk ...
initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}
echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+
sleep 4
boot
'''


#######################
## CLI reserved part ##
#######################

def cli_menu():
    # Display main livenet menu
    printc('\n == Livenet image module == \n', CGREEN)

    print(' 1 - Generate a new livenet image')
    print(' 2 - Mount an existing livenet image')
    print(' 3 - Unount an existing livenet image')
    print(' 4 - Resize livenet image')

    # Answer and get the action to execute
    print('\n Select an action')
    main_action = input('-->: ')
    print('')
    
    # List available kernels
    if main_action == '1':
        cli_create_livenet_image()
    elif main_action == '2':
        cli_mount_livenet_image()
    elif main_action == '3':
        cli_unmount_livenet_image()
    elif main_action == '4':
        cli_resize_livenet_image()

    # Bad entry
    else:
        raise UserWarning('\'' + main_action + '\' is not a valid entry. Please enter another value.')

def cli_create_livenet_image():

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
    selected_password = input('Enter clear root password of the new image: ').replace(" ", "")

    # Select livenet type
    types_list = ['Standard: core (~1.3Gb)', 'Small: openssh, dnf and NetworkManager (~300Mb)', 'Minimal: openssh only (~270Mb)']
    get_type = select_from_list(types_list)
    
    if get_type == 'Standard: core (~1.3Gb)':
        selected_type = LivenetImage.Type.STANDARD
    elif get_type == 'Small: openssh, dnf and NetworkManager (~300Mb)':
        selected_type = LivenetImage.Type.SMALL
    elif get_type == 'Minimal: openssh only (~270Mb)':
        selected_type = LivenetImage.Type.CORE
    else:
        raise UserWarning('Not a valid choice !')
    
     # Select livenet size
    printc('Please choose image size (in megabytes):', CGREEN)
    selected_size = input('-->: ')

    if int(selected_size) < (LivenetImage.MIN_LIVENET_SIZE) or int(selected_size) > (LivenetImage.MAX_LIVENET_SIZE):
        raise UserWarning('\nInvalid input size !')

    # Confirm image creation
    printc('\n[+] Would you like to create a new livenet image with the following attributes: (yes/no)', CGREEN)
    print('  ├── Image name: ' + selected_image_name)
    print('  ├── Image password : ' + selected_password)
    print('  ├── Image kernel: ' + selected_kernel)
    print('  ├── Image type: ' + get_type)
    print('  └── Image size: ' + selected_size + ' Mb')

    confirmation = input('-->: ').replace(" ", "")

    if confirmation == 'yes':
        # Create the image object
        LivenetImage(selected_image_name, selected_password, selected_kernel, selected_type, selected_size)
        printc('\n[OK] Done.', CGREEN)
   
    elif confirmation == 'no':
        printc('\n[+] Image creation cancelled, return to main menu.', CYELLOW)
        return

    else:
        raise UserWarning('\nInvalid confirmation !')


def cli_mount_livenet_image():
    livenet_images = LivenetImage.get_images()

    # Check if there are staging images
    if not livenet_images:
        raise UserWarning('No livenet images.')

    # Get staging images names
    unmounted_images_names = [livenet_image.name for livenet_image in livenet_images if livenet_image.is_mounted == False]

    # Check if there unmounted images
    if not unmounted_images_names:
        raise UserWarning('No unmounted livenet images.')

    # Select a staging image for golden image creation
    printc('[+] Select the livenet image to mount:', CGREEN)
    unmounted_image_name = select_from_list(unmounted_images_names)
    unmounted_image = ImageManager.get_created_image(unmounted_image_name)

    unmounted_image.mount()


def cli_unmount_livenet_image():
    livenet_images = LivenetImage.get_images()

    # Check if there are staging images
    if not livenet_images:
        raise UserWarning('No livenet images.')

    # Get staging images names
    mounted_images_names = [livenet_image.name for livenet_image in livenet_images if livenet_image.is_mounted == True]

    # Check if there unmounted images
    if not mounted_images_names:
        raise UserWarning('No mounted livenet images.')

    # Select a staging image for golden image creation
    printc('[+] Select the livenet image to unmount:', CGREEN)
    mounted_image_name = select_from_list(mounted_images_names)
    mounted_image = ImageManager.get_created_image(mounted_image_name)

    mounted_image.unmount()

def cli_resize_livenet_image():
    # Get list of livenet images
    livenet_images = LivenetImage.get_images()

    # Check if there are livenet images
    if not livenet_images:
        raise UserWarning('No livenet images.')

    # Get livenet images names
    unmounted_images_names = [livenet_image.name for livenet_image in livenet_images if livenet_image.is_mounted == False]

    # Check if there are unmounted images
    # An image must be unmounted to be resized
    if not unmounted_images_names:
        raise UserWarning('No unmounted livenet images.')

    # Select a livenet to mount
    printc('[+] Select the livenet image to mount:', CGREEN)
    unmounted_image_name = select_from_list(unmounted_images_names)
    unmounted_image = ImageManager.get_created_image(unmounted_image_name)

    # Enter new size
    printc('Please choose your new livenet image size (in megabytes):', CGREEN)
    selected_size = input('-->: ')

    # Check size compliance
    if int(selected_size) < (LivenetImage.MIN_LIVENET_SIZE) or int(selected_size) > (LivenetImage.MAX_LIVENET_SIZE):
        raise UserWarning('Invalid input size !')

    # Confirm image resizing
    printc('\n[+] Are you sure you want to resize image \'' + unmounted_image.name + '\' with the following size: (yes/no)', CGREEN)
    print('  └── Image size: ' + selected_size + ' Mb')

    confirmation = input('-->: ').replace(" ", "")

    if confirmation == 'yes':
        # Create the image object
        unmounted_image.resize(selected_size)
        printc('\n[OK] Done.', CGREEN)
   
    elif confirmation == 'no':
        printc('\n[+] Image resizing cancelled, return to main menu.', CYELLOW)
        return

    

