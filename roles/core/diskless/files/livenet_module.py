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
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>, Benoit Leveugle <benoit.leveugle@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import base modules
import os
import shutil
import crypt
import logging
from datetime import datetime
from enum import Enum, auto
from subprocess import check_call

# Import diskless modules
from diskless.modules.base_module import Image
from diskless.kernel_manager import KernelManager
from diskless.image_manager import ImageManager
from diskless.utils import Color, printc, select_from_list


# Class representing a livenet image
class LivenetImage(Image):

    # Enumeration of livenet types
    class Type(Enum):
        # Values are auto because we don't care about
        STANDARD = auto()
        SMALL = auto()
        CORE = auto()

    # Image working directory, specific for livenet images
    WORKING_DIRECTORY = '/var/tmp/diskless/workdir/'

    # Define the allowed sizes range
    MAX_LIVENET_SIZE = 50000  # 50 Gigas
    MIN_LIVENET_SIZE = 100  # 100 Megabytes

    # Class constructor
    def __init__(self, name, password=None, kernel=None, livenet_type=None, livenet_size=None, additional_packages=None, ssh_pub_key=None, selinux=None, release_version=None, optimize=None):
        super().__init__(name, password, kernel, livenet_type, livenet_size, additional_packages, ssh_pub_key, selinux, release_version, optimize)

    def create_new_image(self, password, kernel, livenet_type, livenet_size, additional_packages, ssh_pub_key, selinux, release_version, optimize):
        super().create_new_image()

        # Checking all parameters
        # Check name format
        if not isinstance(password, str) or len(password.split()) > 1:
            raise ValueError('Unexpected password format.')

        # Check kernel attribute
        if kernel not in KernelManager.get_available_kernels():
            raise ValueError('Invalid kernel.')

        # Check livenet type
        if livenet_type is not LivenetImage.Type.STANDARD and livenet_type is not LivenetImage.Type.SMALL and livenet_type is not LivenetImage.Type.CORE:
            raise ValueError('Invalid livenet type.')

        # Check livenet size
        if not isinstance(livenet_size, str) or int(livenet_size) < LivenetImage.MIN_LIVENET_SIZE or int(livenet_size) > LivenetImage.MAX_LIVENET_SIZE:
            raise ValueError('Invalid livenet size')

        # Set image attributes before creation
        self.kernel = kernel
        self.image = 'initramfs-kernel-' + self.kernel.replace('vmlinuz-', '')
        self.password = password

        self.livenet_type = livenet_type
        self.livenet_size = livenet_size

        self.selinux = selinux

        self.optimize = optimize

        if ssh_pub_key is not None:
            self.ssh_pub_key = ssh_pub_key

        if additional_packages is not None:
            self.additional_packages = additional_packages

        if release_version is not None:
            self.release_version = release_version

        # A livenet can be mounted on it's personnal mount directory
        # in order to perform actions on it.
        self.is_mounted = False

        # Set up working and mount image directories
        self.WORKING_DIRECTORY = self.WORKING_DIRECTORY + self.name + '/'
        self.MOUNT_DIRECTORY = self.WORKING_DIRECTORY + 'mnt/'

        # Generate image files
        self.generate_files()

    def generate_files(self):
        super().generate_files()
        super().create_image_folders()
        self.generate_file_system()
        self.generate_ipxe_boot_file()

    def generate_file_system(self):
        super().generate_file_system()

        # Generate operating system of the image
        self.generate_operating_system()

        # Setup image password
        self.set_image_password(self.WORKING_DIRECTORY + 'generated_os')

        # Ensure root password is allowed
        self.set_image_ssh_permitrootlogin(self.WORKING_DIRECTORY + 'generated_os')

        # Setup ssh key
        if hasattr(self, 'ssh_pub_key'):
            self.set_image_ssh_pub_key()

        # Setup SELinux
        if self.selinux:
            self.set_image_selinux()

        # Set /etc/os-release meta data
        self.set_image_release_meta_data()

        # Generate image squashfs.img
        self.generate_squashfs()

    # Use dnf command in order to create the image operating system
    def generate_operating_system(self):
        logging.info('Generating image \'' + self.name + '\' operating system')

        # Create os generation directory
        logging.debug('Executing \'mkdir -p ' + self.WORKING_DIRECTORY + 'generated_os\'')
        os.makedirs(self.WORKING_DIRECTORY + 'generated_os')

        # Set up release version
        if hasattr(self, 'release_version'):
            release = ' --releasever=' + self.release_version
        else:
            release = ''

        # Create empty string of packages
        dnf_packages = ''

        # Get appropriate packages for desired image file system
        if self.livenet_type == LivenetImage.Type.STANDARD:
            logging.debug('Standard image requested. Adding "@core" to packages list')
            dnf_packages = '@core'

        elif self.livenet_type == LivenetImage.Type.SMALL:
            logging.debug('Small image requested. Adding "dnf yum iproute procps-ng openssh-server NetworkManager" to packages list')
            dnf_packages = 'dnf yum iproute procps-ng openssh-server NetworkManager'

        elif self.livenet_type == LivenetImage.Type.CORE:
            logging.debug('Core image requested. Adding "iproute procps-ng openssh-server" to packages list')
            dnf_packages = 'iproute procps-ng openssh-server'

        # If there are additional packages to install
        if hasattr(self, 'additional_packages'):
            logging.debug('Additional packages requested. Adding "' + str(self.additional_packages) + '" to dnf packages to install')
            dnf_packages += ' ' + ' '.join(self.additional_packages)

        # If SELinux is activated (or enabled)
        if self.selinux:
            # Add needed SELinux packages to the dnf packages list
            logging.debug('SElinux requested. Adding "install policycoreutils" to packages list')
            dnf_packages += ' selinux-policy-targeted selinux-policy-devel policycoreutils'

        # Execute dnf
        logging.debug('Executing packages install with the following command:')
        if self.optimize:
            if self.selinux:
                logging.debug('dnf install ' + dnf_packages + release + ' -y --installroot=' + self.WORKING_DIRECTORY + 'generated_os/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
                os.system('dnf install ' + dnf_packages + release + ' -y --installroot=' + self.WORKING_DIRECTORY + 'generated_os/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
            else:
                logging.debug('dnf install ' + dnf_packages + release + ' -y --installroot=' + self.WORKING_DIRECTORY + 'generated_os/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
                os.system('dnf install ' + dnf_packages + release + ' -y --installroot=' + self.WORKING_DIRECTORY + 'generated_os/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
        else:
            logging.debug('dnf install ' + dnf_packages + release + ' -y --installroot=' + self.WORKING_DIRECTORY + 'generated_os/ --setopt=module_platform_id=platform:el8')
            os.system('dnf install ' + dnf_packages + release + ' -y --installroot=' + self.WORKING_DIRECTORY + 'generated_os/ --setopt=module_platform_id=platform:el8')

    # Generate the image squashfs image after creating the image rootfs image
    # The operating system need to be previoulsy created by the
    # generate_operating_system method.
    def generate_squashfs(self):
        logging.info('Generating image \'' + self.name + '\' squashfs')

        # Create the directory that will contain the rootfs image
        logging.debug('Executing \'mkdir -p ' + self.IMAGE_DIRECTORY + 'tosquash/LiveOS\'')
        os.makedirs(self.IMAGE_DIRECTORY + 'tosquash/LiveOS')

        # Create the rootfs image with the image size in Mb
        logging.debug('Executing \'dd if=/dev/zero of=' + self.IMAGE_DIRECTORY + 'tosquash/LiveOS/rootfs.img bs=1M count=' + self.livenet_size + '\'')
        os.system('dd if=/dev/zero of=' + self.IMAGE_DIRECTORY + 'tosquash/LiveOS/rootfs.img bs=1M count=' + self.livenet_size)

        # Format the rootfs.img in mkfs format
        logging.debug('Executing \'mkfs.xfs ' + self.IMAGE_DIRECTORY + 'tosquash/LiveOS/rootfs.img\'')
        os.system('mkfs.xfs ' + self.IMAGE_DIRECTORY + 'tosquash/LiveOS/rootfs.img')

        # Create a mounting directory for rootfs.img
        logging.debug('Executing \'mkdir -p ' + self.MOUNT_DIRECTORY + '\'')
        os.makedirs(self.MOUNT_DIRECTORY)

        # Mount rootfs.img in order to put inside the operating system
        logging.debug('Executing \'mount -o loop ' + self.IMAGE_DIRECTORY + 'tosquash/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY + '\'')
        os.system('mount -o loop ' + self.IMAGE_DIRECTORY + 'tosquash/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY)

        # Put the operating system inside rootfs.img
        logging.debug('Executing \'cp -a ' + self.WORKING_DIRECTORY + 'generated_os/* ' + self.MOUNT_DIRECTORY + '\'')
        os.system('cp -a ' + self.WORKING_DIRECTORY + 'generated_os/* ' + self.MOUNT_DIRECTORY)

        # Unmount rootfs.img file
        logging.debug('Executing \'umount ' + self.MOUNT_DIRECTORY + '\'')
        os.system('umount ' + self.MOUNT_DIRECTORY)

        # Remove mountage directory for rootfs.img
        logging.debug('Executing \'rm -rf ' + self.MOUNT_DIRECTORY + '\'')
        shutil.rmtree(self.MOUNT_DIRECTORY)

        # Removing useless working directory because we don't need it anymore
        logging.debug('Executing \'rm -rf ' + self.WORKING_DIRECTORY + '\'')
        shutil.rmtree(self.WORKING_DIRECTORY)

        # Create the squashfs.img that will contains LiveOS/rootfs.img
        logging.debug('Executing \'mksquashfs ' + self.IMAGE_DIRECTORY + 'tosquash ' + self.IMAGE_DIRECTORY + 'squashfs.img\'')
        os.system('mksquashfs ' + self.IMAGE_DIRECTORY + 'tosquash ' + self.IMAGE_DIRECTORY + 'squashfs.img')

        # Removing not squashed LiveOS/rootfs.img, because we don't need it anymore
        # (In fact the rootfs.img is now inside the squashfs.img)
        logging.debug('Executing \'rm -rf ' + self.IMAGE_DIRECTORY + 'tosquash\'')
        shutil.rmtree(self.IMAGE_DIRECTORY + 'tosquash')

    # Set a password for the image
    # Staging images need a password
    def set_image_password(self, mountage_directory):
        logging.info('Setting up image \'' + self.name + '\' password')

        # Create hash with clear password
        self.password = crypt.crypt(self.password, crypt.METHOD_SHA512)

        # Create new password file content
        with open(mountage_directory + '/etc/shadow', 'r') as ff:
            newText = ff.read().replace('root:*', 'root:' + self.password)
            # Write new passord file content
        with open(mountage_directory + '/etc/shadow', "w") as ff:
            ff.write(newText)

    # Ensure root login is allowed via ssh
    def set_image_ssh_permitrootlogin(self, mountage_directory):
        logging.info('Setting up image \'' + self.name + '\' sshd PermitRootLogin')

        # Create new file content
        with open(mountage_directory + '/etc/ssh/sshd_config', 'r') as ff:
            filebuffer = ff.readlines()
        for i in range(len(filebuffer)):
            if 'PermitRootLogin' in filebuffer[i]:
                filebuffer[i] = 'PermitRootLogin yes'

        # Write new file content
        with open(mountage_directory + '/etc/ssh/sshd_config', "w") as ff:
            ff.writelines(filebuffer)

    # Write meta data inside image os-release file
    def set_image_release_meta_data(self):
        logging.info('Setting image \'' + self.name + '\' meta data')

        with open(self.WORKING_DIRECTORY + 'generated_os/etc/os-release', 'a') as ff:
            ff.writelines(['BLUEBANQUISE_IMAGE_NAME="{0}"\n'.format(self.name),
                           'BLUEBANQUISE_IMAGE_KERNEL="{0}"\n'.format(self.kernel),
                           'BLUEBANQUISE_IMAGE_DATE="{0}"\n'.format(datetime.today().strftime('%Y-%m-%d'))])

    # Inject ssh pub key
    def set_image_ssh_pub_key(self):
        logging.info('Injecting image \'' + self.name + '\' SSH public key')

        # Create ssh dir and copy pub key to authorized_keys
        logging.debug('Executing \'mkdir ' + self.WORKING_DIRECTORY + 'generated_os/root/.ssh\'')
        os.mkdir(self.WORKING_DIRECTORY + 'generated_os/root/.ssh')

        logging.debug('Executing \'cp ' + self.ssh_pub_key + ' ' + self.WORKING_DIRECTORY + 'generated_os/root/.ssh/authorized_keys\'')
        shutil.copyfile(self.ssh_pub_key, self.WORKING_DIRECTORY + 'generated_os/root/.ssh/authorized_keys')

    # Enable SELinux in the image
    def set_image_selinux(self):
        logging.info('Setting up SELinux for image \'' + self.name + '\'')

        # Mouot required directories on the image
        logging.debug('Executing \'mount --bind /proc ' + self.WORKING_DIRECTORY + 'generated_os/proc\'')
        check_call('mount --bind /proc ' + self.WORKING_DIRECTORY + 'generated_os/proc', shell=True)

        logging.debug('Executing \'mount --bind /sys ' + self.WORKING_DIRECTORY + 'generated_os/sys\'')
        check_call('mount --bind /sys ' + self.WORKING_DIRECTORY + 'generated_os/sys', shell=True)

        logging.debug('Executing \'mount --bind /sys/fs/selinux ' + self.WORKING_DIRECTORY + 'generated_os/sys/fs/selinux\'')
        check_call('mount --bind /sys/fs/selinux ' + self.WORKING_DIRECTORY + 'generated_os/sys/fs/selinux', shell=True)

        logging.debug('Executing \'mount --bind /sys/kernel/tracing ' + self.WORKING_DIRECTORY + 'generated_os/sys/kernel/tracing\'')
        check_call('mount --bind /sys/kernel/tracing ' + self.WORKING_DIRECTORY + 'generated_os/sys/kernel/tracing', shell=True)

        # Chroot onto image
        real_root = os.open("/", os.O_RDONLY)
        logging.debug('Executing \'chroot ' + self.WORKING_DIRECTORY + 'generated_os/\'')
        os.chroot(self.WORKING_DIRECTORY + 'generated_os/')
        os.chdir("/")

        # Restore SELinux values on all file system
        logging.debug('Executing \'restorecon -Rv /\'')
        check_call('restorecon -Rv /', shell=True)

        # Quit chroot
        logging.debug('Executing \'exit\'')
        os.fchdir(real_root)
        os.chroot(".")
        os.close(real_root)

        # Unmount all selinux mountages
        logging.debug('Executing \'umount ' + self.WORKING_DIRECTORY + 'generated_os/{sys/fs/selinux,sys,proc}\'')
        check_call('umount ' + self.WORKING_DIRECTORY + 'generated_os/{sys/fs/selinux,sys/kernel/tracing,sys,proc}', shell=True)

    # Remove files associated with the NFS image
    def remove_files(self):

        # If the livenet image is currently mounted
        if self.is_mounted is True:
            # Unmount before removing files
            self.unmount()

        super().remove_files()

    # Mount the image to edit it
    def mount(self):
        """Mounting livenet image"""
        logging.info('Mounting livenet image \'' + self.name + '\'')

        # Create image working directory
        logging.debug('Executing \'mkdir ' + self.WORKING_DIRECTORY + '\'')
        os.mkdir(self.WORKING_DIRECTORY)

        # Unsquash current image inside working directory
        logging.debug('Executing \'unsquashfs -d ' + self.WORKING_DIRECTORY + 'squashfs-root ' + self.IMAGE_DIRECTORY + 'squashfs.img\'')
        os.system('unsquashfs -d ' + self.WORKING_DIRECTORY + 'squashfs-root ' + self.IMAGE_DIRECTORY + 'squashfs.img')

        # Create image mounting directory
        logging.debug('Executing \'mkdir -p ' + self.MOUNT_DIRECTORY + '\'')
        os.makedirs(self.MOUNT_DIRECTORY)

        logging.debug('Executing \'mount ' + self.WORKING_DIRECTORY + 'squashfs-root/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY + '\'')
        os.system('mount ' + self.WORKING_DIRECTORY + 'squashfs-root/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY)

        # Mount diskless server proc on livenet image proc
        logging.debug('Executing \'mount --bind /proc ' + self.MOUNT_DIRECTORY + 'proc\'')
        os.system('mount --bind /proc ' + self.MOUNT_DIRECTORY + 'proc')

        # Mount diskless server sys on livenet image sys
        logging.debug('Executing \'mount --bind /sys ' + self.MOUNT_DIRECTORY + 'sys\'')
        os.system('mount --bind /sys ' + self.MOUNT_DIRECTORY + 'sys')

        self.get_existing_image()
        if (self.selinux):
            logging.debug('Executing \'mount --bind /sys/fs/selinux ' + self.MOUNT_DIRECTORY + 'sys/fs/selinux\'')
            check_call('mount --bind /sys/fs/selinux ' + self.MOUNT_DIRECTORY + 'sys/fs/selinux', shell=True)

            logging.debug('Executing \'mount --bind /sys/kernel/tracing ' + self.MOUNT_DIRECTORY + 'sys/kernel/tracing\'')
            check_call('mount --bind /sys/kernel/tracing ' + self.MOUNT_DIRECTORY + 'sys/kernel/tracing', shell=True)

        # Create an inventory directory
        logging.debug('Executing \'mkdir ' + self.WORKING_DIRECTORY + 'inventory\'')
        os.mkdir(self.WORKING_DIRECTORY + 'inventory')

        # Create the ansible connection
        # Use of [:-1] to remove last '/' from the MOUNT_DIRECTORY path
        logging.debug('Executing \'echo \'' + self.MOUNT_DIRECTORY[:-1] + ' ansible_connection=chroot\' > ' + self.WORKING_DIRECTORY + 'inventory/host\'')
        os.system('echo \'' + self.MOUNT_DIRECTORY[:-1] + ' ansible_connection=chroot\' > ' + self.WORKING_DIRECTORY + 'inventory/host')

        # Change image mountage status
        self.is_mounted = True
        self.register_image()

    # Unmount the image when the editing is finished
    def unmount(self):
        """Unmounting livenet image"""
        logging.info('Unmounting livenet image \'' + self.name + '\'')

        self.get_existing_image()
        if (self.selinux):
            logging.debug('Executing \'umount ' + self.MOUNT_DIRECTORY + 'sys/{fs/selinux,kernel/tracing}\'')
            check_call('umount ' + self.MOUNT_DIRECTORY + 'sys/{fs/selinux,kernel/tracing}', shell=True)

        # Unmount all mountages and delete mountage directory
        logging.debug('Executing \'umount ' + self.MOUNT_DIRECTORY + '{proc,sys}\'')
        os.system('umount ' + self.MOUNT_DIRECTORY + '{proc,sys}')

        logging.debug('Executing \'umount ' + self.MOUNT_DIRECTORY + '\'')
        os.system('umount ' + self.MOUNT_DIRECTORY)

        logging.debug('Executing \'rm -rf ' + self.MOUNT_DIRECTORY + '\'')
        shutil.rmtree(self.MOUNT_DIRECTORY)

        # Create a squashfs backup (prevent failure)
        logging.debug('Executing \'mv ' + self.IMAGE_DIRECTORY + 'squashfs.img ' + self.IMAGE_DIRECTORY + 'squashfs.img.bkp\'')
        os.system('mv ' + self.IMAGE_DIRECTORY + 'squashfs.img ' + self.IMAGE_DIRECTORY + 'squashfs.img.bkp')

        # Create a new squashfs
        logging.debug('Executing \'mksquashfs ' + self.WORKING_DIRECTORY + 'squashfs-root/ ' + self.IMAGE_DIRECTORY + 'squashfs.img\'')
        os.system('mksquashfs ' + self.WORKING_DIRECTORY + 'squashfs-root/ ' + self.IMAGE_DIRECTORY + 'squashfs.img')

        # Remove backup squashfs because we have the new squashfs
        logging.debug('Executing \'rm -f ' + self.IMAGE_DIRECTORY + 'squashfs.img.bkp\'')
        os.remove(self.IMAGE_DIRECTORY + 'squashfs.img.bkp')

        # Remove working directory because we don't need it anymore
        logging.debug('Executing \'rm -rf ' + self.WORKING_DIRECTORY + '\'')
        shutil.rmtree(self.WORKING_DIRECTORY)

        # Changing image mountage status
        self.is_mounted = False
        self.register_image()

    # Resize the livenet image image size
    def resize(self, new_size):
        logging.info('Start resizing image \'' + self.name + '\'')

        # Image must be unmounted to resize it
        if self.is_mounted:
            raise ValueError('Cannot resize a mounted livenet image')

        # Check livenet size
        if not isinstance(new_size, str) or int(new_size) < LivenetImage.MIN_LIVENET_SIZE or int(new_size) > LivenetImage.MAX_LIVENET_SIZE:
            raise ValueError('Invalid livenet size')

        # Create usefull directories for resizement
        logging.debug('Executing \'mkdir -p ' + self.MOUNT_DIRECTORY + 'mnt_copy\'')
        os.makedirs(self.MOUNT_DIRECTORY + 'mnt_copy')

        logging.debug('Executing \'mkdir -p ' + self.MOUNT_DIRECTORY + 'mnt\'')
        os.makedirs(self.MOUNT_DIRECTORY + 'mnt')

        logging.debug('Executing \'mkdir -p ' + self.WORKING_DIRECTORY + 'current\'')
        os.makedirs(self.WORKING_DIRECTORY + 'current')

        logging.debug('Executing \'mkdir -p ' + self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/\'')
        os.makedirs(self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/')

        # Create a new rootfs image with the new size
        logging.debug('Executing \'dd if=/dev/zero of=' + self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/rootfs.img bs=1M count=' + new_size + '\'')
        os.system('dd if=/dev/zero of=' + self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/rootfs.img bs=1M count=' + new_size)

        # Format the fresh rootfs.img into an xfs system
        logging.debug('Executing \'mkfs.xfs ' + self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/rootfs.img\'')
        os.system('mkfs.xfs ' + self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/rootfs.img')

        # Mount the new rootfs.img on it's mount directory
        logging.debug('Executing \'mount ' + self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY + 'mnt_copy/\'')
        os.system('mount ' + self.WORKING_DIRECTORY + 'copy/squashfs-root/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY + 'mnt_copy/')

        # Unsquash current image
        logging.debug('Executing \'unsquashfs -d ' + self.WORKING_DIRECTORY + 'current/squashfs-root ' + self.IMAGE_DIRECTORY + 'squashfs.img\'')
        os.system('unsquashfs -d ' + self.WORKING_DIRECTORY + 'current/squashfs-root ' + self.IMAGE_DIRECTORY + 'squashfs.img')

        # Mount current rootfs.img on it's mount directory
        logging.debug('Executing \'mount ' + self.WORKING_DIRECTORY + 'current/squashfs-root/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY + 'mnt\'')
        os.system('mount ' + self.WORKING_DIRECTORY + 'current/squashfs-root/LiveOS/rootfs.img ' + self.MOUNT_DIRECTORY + 'mnt')

        # Create image.xfsdump from current image
        logging.debug('Executing \'xfsdump -l 0 -L ' + self.name + ' -M media -f ' + self.WORKING_DIRECTORY + '/current/image.xfsdump ' + self.MOUNT_DIRECTORY + 'mnt\'')
        os.system('xfsdump -l 0 -L ' + self.name + ' -M media -f ' + self.WORKING_DIRECTORY + '/current/image.xfsdump ' + self.MOUNT_DIRECTORY + 'mnt')

        # Restore with new sized rootfs.img mountage
        logging.debug('Executing \'xfsrestore -f ' + self.WORKING_DIRECTORY + 'current/image.xfsdump ' + self.MOUNT_DIRECTORY + 'mnt_copy\'')
        os.system('xfsrestore -f ' + self.WORKING_DIRECTORY + 'current/image.xfsdump ' + self.MOUNT_DIRECTORY + 'mnt_copy')
        os.sync()

        # Umount mnt and mnt_copy
        logging.debug('Executing \'umount ' + self.MOUNT_DIRECTORY + '*\'')
        os.system('umount ' + self.MOUNT_DIRECTORY + '*')

        logging.debug('Executing \'rm -rf ' + self.MOUNT_DIRECTORY + '\'')
        shutil.rmtree(self.MOUNT_DIRECTORY)

        # Remove old squashfs
        logging.debug('Executing \'rm -f ' + self.IMAGE_DIRECTORY + 'squashfs.img\'')
        os.remove(self.IMAGE_DIRECTORY + 'squashfs.img')

        # Generate the new squashfs
        logging.debug('Executing \'mksquashfs ' + self.WORKING_DIRECTORY + 'copy/squashfs-root/ ' + self.IMAGE_DIRECTORY + 'squashfs.img\'')
        os.system('mksquashfs ' + self.WORKING_DIRECTORY + 'copy/squashfs-root/ ' + self.IMAGE_DIRECTORY + 'squashfs.img')

        logging.debug('Executing \'rm -rf ' + self.WORKING_DIRECTORY + '\'')
        shutil.rmtree(self.WORKING_DIRECTORY)

        # Update image size attribute value
        self.livenet_size = new_size
        self.register_image()

        logging.info('Image has been resized to ' + new_size + 'Mb')

    # We must redefine the method because we cannot register attributs as boolean
    def get_existing_image(self):
        super().get_existing_image()

        # Convert string is_mounted state into boolean equivalent
        if self.is_mounted == 'True':
            self.is_mounted = True
        elif self.is_mounted == 'False':
            self.is_mounted = False

        # Convert SELinux string status into boolean
        if hasattr(self, 'selinux'):
            if self.selinux == 'True':
                self.selinux = True
            elif self.selinux == 'False':
                self.selinux = False

    # Clean all image files without image object when an image is corrupted
    @staticmethod
    def clean(image_name):
        Image.clean(image_name)

        IMAGES_DIRECTORY = LivenetImage.IMAGES_DIRECTORY + image_name + '/'
        WORKING_DIRECTORY = LivenetImage.WORKING_DIRECTORY + image_name + '/'
        MOUNT_DIRECTORY = WORKING_DIRECTORY + 'mnt/'

        # Cleanings for mount directories
        if os.path.isdir(MOUNT_DIRECTORY):
            logging.debug(MOUNT_DIRECTORY + ' is a directory')
            logging.debug('Executing \'umount ' + MOUNT_DIRECTORY + '*\'')
            os.system('umount ' + MOUNT_DIRECTORY + '*')

            if os.path.ismount(MOUNT_DIRECTORY):
                logging.debug(MOUNT_DIRECTORY + ' is a mount point')
                logging.debug('Executing \'umount ' + MOUNT_DIRECTORY + '\'')
                os.system('umount ' + MOUNT_DIRECTORY)

            logging.debug('Executing \'rm -rf ' + MOUNT_DIRECTORY + '\'')
            shutil.rmtree(MOUNT_DIRECTORY)

        # Try logging.debuging image working directory
        if os.path.isdir(WORKING_DIRECTORY):
            logging.debug(WORKING_DIRECTORY + ' is a directory')
            logging.debug('Executing \'rm -rf ' + WORKING_DIRECTORY + '\'')
            shutil.rmtree(WORKING_DIRECTORY)

        # Try logging.debuging image base directory
        if os.path.isdir(IMAGES_DIRECTORY):
            logging.debug(IMAGES_DIRECTORY + ' is a directory')
            logging.debug('Executing \'rm -rf ' + IMAGES_DIRECTORY + '\'')
            shutil.rmtree(IMAGES_DIRECTORY)

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
kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} root=live:http://${{next-server}}/preboot_execution_environment/diskless/images/{image_name}/squashfs.img rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4 selinux={image_selinux}
echo | Loading initial ramdisk ...
initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}
echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+
sleep 4
boot
'''

    def cli_display_info(self):
        """Display informations about an image"""

        # Print image name
        print(' • Image name: ' + self.name)

        # Get all attributs in a dictionary
        attributes_dictionary = dict(self.__dict__)

        # Delete name because it was already printed
        del attributes_dictionary['name']
        del attributes_dictionary['MOUNT_DIRECTORY']
        del attributes_dictionary['WORKING_DIRECTORY']

        if self.livenet_size < 1000:
            attributes_dictionary['livenet_size'] = str(self.livenet_size) + 'M'
        # Division can produce a long size string, we get only the 5 firsts
        else:
            attributes_dictionary['livenet_size'] = str(self.livenet_size/1024)[:5] + "G"

        if self.is_mounted is True:
            attributes_dictionary['is_mounted'] = 'True, on ' + self.MOUNT_DIRECTORY

        # For each element of the dictionary except the last
        for i in range(0, len(attributes_dictionary.items()) - 1):
            print('     ├── ' + str(list(attributes_dictionary.keys())[i]) + ': ' + str(list(attributes_dictionary.values())[i]))

        # For the last tuple element of the list
        print('     └── ' + str(list(attributes_dictionary.keys())[-1]) + ': ' + str(list(attributes_dictionary.values())[-1]))

    # Override method because of selinux
    def generate_ipxe_boot_file(self):
        """Generate an ipxe boot file for the image."""
        logging.info('Creating image \'' + self.name + '\' IPXE boot file')

        # Format image ipxe boot file template with image attributes
        file_content = self.__class__.get_boot_file_template().format(image_name=self.name,
                                                                      image_initramfs=self.image,
                                                                      image_kernel=self.kernel,
                                                                      image_selinux=int(self.selinux))

        # Create ipxe boot file
        with open(self.IMAGE_DIRECTORY + '/boot.ipxe', "w") as ff:
            ff.write(file_content)


#####################
# CLI reserved part #
#####################

def cli_menu():
    # Display main livenet menu
    printc('\n == Livenet image module == \n', Color.GREEN)

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

# Get a size from the user and check the compliance


def cli_get_size(size):

    # Check if there is the size unit
    unit = size[-1]

    if unit != 'G' and unit != 'M':
        raise UserWarning('\nNot a valid size unit format!')

    # Delete unit from size
    size = size[:-1]

    # If the user has entered a Giga value
    if unit == 'G':
        # If the giga value has a dot separator
        if '.' in size:
            size_array = size.split(".")
            if len(size_array) != 2 or not size_array[0].isdigit() or not size_array[1].isdigit() or len(size_array[1]) > 3:
                raise UserWarning('\nNot a valid size format!')

            size = str(int(float(size)*1024))

        # If the giga value has no dot separator
        else:
            if not size.isdigit():
                raise UserWarning('\nNot a valid size format!')
            size = str(int(size) * 1024)

    elif unit == 'M':
        # Check if the size is only numerical
        if not size.isdigit():
            raise UserWarning('\nNot a valid size format!')

    return size


def cli_create_livenet_image():

    # Get available kernels
    kernel_list = KernelManager.get_available_kernels()

    # If there are no kernels aise an exception
    if not kernel_list:
        raise UserWarning('No kernel available')

    # Condition to test if image name is compliant
    while True:

        printc('[+] Give a name for your image', Color.GREEN)
        # Get new image name
        selected_image_name = input('-->: ').replace(" ", "")

        if selected_image_name == '':
            raise UserWarning('Image name cannot be empty !')

        if not ImageManager.is_image(selected_image_name):
            break

        # Else
        print('Image ' + selected_image_name + ' already exist, use another image name.')

    # Select the kernel to use
    printc('\n[+] Select your kernel:', Color.GREEN)
    selected_kernel = select_from_list(kernel_list)

    # Manage password
    printc('\n[+] Give a password for your image', Color.GREEN)
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
    printc('\nPlease choose image size:\n(supported units: M=1024*1024, G=1024*1024*1024)\n(Examples: 5120M or 5G)', Color.GREEN)
    selected_size = input('-->: ')

    # Check and convert the size
    image_size = cli_get_size(selected_size)

    # Check size compliance with livenet image expected size limits
    if int(image_size) < (LivenetImage.MIN_LIVENET_SIZE) or int(image_size) > (LivenetImage.MAX_LIVENET_SIZE):
        raise UserWarning('\nSize out of limits !')

    # Inject ssh key or not
    printc('\nEnter path to SSH public key (left empty to disable key injection)', Color.GREEN)
    selected_ssh_pub_key = input('-->: ')
    if selected_ssh_pub_key != '' and not os.path.exists(selected_ssh_pub_key):
        raise UserWarning('\nSSH public key not found ' + selected_ssh_pub_key)
    if selected_ssh_pub_key == '':
        selected_ssh_pub_key = None

    # Activate SELinux or not
    printc('\nActivate SELinux inside the image (yes/no) ?', Color.GREEN)
    answer_selinux = input('-->: ')
    if answer_selinux == 'yes':
        selinux = True
    elif answer_selinux == 'no':
        selinux = False
    else:
        raise UserWarning('\nInvalid input !')

    # Propose to user to install additional packages
    printc('\nDo you want to customize your image with additional packages (yes/no) ? ', Color.GREEN)
    choice = input('-->: ')
    # Install additional packages
    if choice == 'yes':
        # Get package list from user
        additional_packages = Image.cli_add_packages()
    # Don't install additional packages
    elif choice == 'no':
        additional_packages = None
    else:
        raise UserWarning('\nInvalid entry !')

    # Propose to user to specify a release version
    printc('\nSpecify a release version for installation (left empty to not use the --relasever option)', Color.GREEN)
    release_version = input('-->: ')
    if release_version == '':
        release_version = None

    # Propose to optimize image packages
    printc('\nDo you wish tool try to optimize image by using aggressive packages dependencies parameters ? ', Color.GREEN)
    printc('Note that this may collide with additional packages if asked for. (yes/no) ? ', Color.GREEN)
    answer_optimize = input('-->: ')
    if answer_optimize == 'yes':
        optimize = True
    elif answer_optimize == 'no':
        optimize = False
    else:
        raise UserWarning('\nInvalid input !')

    # Confirm image creation
    printc('\n[+] Would you like to create a new livenet image with the following attributes: (yes/no)', Color.GREEN)
    print('  ├── Image name: \t\t' + selected_image_name)
    print('  ├── Image password: \t\t' + selected_password)
    print('  ├── Image kernel: \t\t' + selected_kernel)
    print('  ├── Image type: \t\t' + get_type)
    print('  ├── Image size: \t\t' + selected_size)
    print('  ├── Optimize packages: \t' + str(optimize))

    # Print ssh pub key packages if there is one
    if selected_ssh_pub_key is not None:
        print('  ├── SSH pubkey: \t\t' + selected_ssh_pub_key)

    # Print additional packages if there is
    if additional_packages is not None:
        print('  ├── Additional packages: \t' + str(additional_packages))

    # Print release version if there is one
    if release_version is not None:
        print('  ├── Release version: \t\t' + release_version)

    print('  └── Enable SELinux: \t\t' + str(selinux))

    confirmation = input('-->: ').replace(" ", "")

    if confirmation == 'yes':
        # Create the image object
        LivenetImage(selected_image_name, selected_password, selected_kernel, selected_type, image_size, additional_packages, selected_ssh_pub_key, selinux, release_version, optimize)
        printc('\n[OK] Done.', Color.GREEN)

    elif confirmation == 'no':
        printc('\n[+] Image creation cancelled, return to main menu.', Color.YELLOW)
        return

    else:
        raise UserWarning('\nInvalid confirmation !')


def cli_mount_livenet_image():
    livenet_images = LivenetImage.get_images()

    # Check if there are staging images
    if not livenet_images:
        raise UserWarning('No livenet images.')

    # Get staging images names
    unmounted_images_names = [livenet_image.name for livenet_image in livenet_images if livenet_image.is_mounted is False]

    # Check if there unmounted images
    if not unmounted_images_names:
        raise UserWarning('No unmounted livenet images.')

    # Select a staging image for golden image creation
    printc('[+] Select the livenet image to mount:', Color.GREEN)
    unmounted_image_name = select_from_list(unmounted_images_names)
    unmounted_image = ImageManager.get_created_image(unmounted_image_name)

    unmounted_image.mount()


def cli_unmount_livenet_image():
    livenet_images = LivenetImage.get_images()

    # Check if there are staging images
    if not livenet_images:
        raise UserWarning('No livenet images.')

    # Get staging images names
    mounted_images_names = [livenet_image.name for livenet_image in livenet_images if livenet_image.is_mounted is True]

    # Check if there unmounted images
    if not mounted_images_names:
        raise UserWarning('No mounted livenet images.')

    # Select a staging image for golden image creation
    printc('[+] Select the livenet image to unmount:', Color.GREEN)
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
    unmounted_images_names = [livenet_image.name for livenet_image in livenet_images if livenet_image.is_mounted is False]

    # Check if there are unmounted images
    # An image must be unmounted to be resized
    if not unmounted_images_names:
        raise UserWarning('No unmounted livenet images.')

    # Select a livenet to mount
    printc('[+] Select the livenet image to mount:', Color.GREEN)
    unmounted_image_name = select_from_list(unmounted_images_names)
    unmounted_image = ImageManager.get_created_image(unmounted_image_name)

    # Enter new size
    printc('Please enter your new image size:\n(supported units: M=1024*1024, G=1024*1024*1024)\n(Examples: 5120M or 5G)', Color.GREEN)
    selected_size = input('-->: ')

    # Check and convert the size
    image_size = cli_get_size(selected_size)

    # Check size compliance with livenet image expected size limits
    if int(image_size) < (LivenetImage.MIN_LIVENET_SIZE) or int(image_size) > (LivenetImage.MAX_LIVENET_SIZE):
        raise UserWarning('\nSize out of limits !')

    # Confirm image resizing
    printc('\n[+] Are you sure you want to resize image \'' + unmounted_image.name + '\' with the following size: (yes/no)', Color.GREEN)
    print('  └── Image size: ' + selected_size)

    confirmation = input('-->: ').replace(" ", "")

    if confirmation == 'yes':
        # Create the image object
        unmounted_image.resize(image_size)
        printc('\n[OK] Done.', Color.GREEN)

    elif confirmation == 'no':
        printc('\n[+] Image resizing cancelled, return to main menu.', Color.YELLOW)
        return
