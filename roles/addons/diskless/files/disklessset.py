#!/usr/bin/env python3

# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# disklessset tool, to generate and manage diskless images in bluebanquise
# 2019 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/oxedions/bluebanquise - MIT license

# Import dependances
from ClusterShell.NodeSet import NodeSet
from argparse import ArgumentParser
from shutil import copy2
import yaml
import os
import pwd
import grp
import re
import hashlib
import crypt
from base64 import urlsafe_b64encode as encode
from base64 import urlsafe_b64decode as decode
from getpass import getpass
from datetime import datetime

# Colors, from https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Get arguments passed to bootset
parser = ArgumentParser()
#parser.add_argument("-n", "--nodes", dest="nodes",
#                    help="Target node(s). Use nodeset format for ranges.", metavar="NODE")
#parser.add_argument("-b", "--boot", dest="boot",
#                    help="Next pxe boot: can be osdeploy or disk.")
#parser.add_argument("-f", "--force", dest="force", default=" ",
#                    help="Force. 'update' = files update, 'network' = static ip. Combine using comma separator.")

passed_arguments = parser.parse_args()

dnf_cache_directory = '/dev/shm/'
image_working_directory = '/root/diskless/workdir'

print('BlueBanquise Diskless manager')
print(' 1 - List available kernels')
print(' 2 - Generate a new initramfs')
print(' 3 - Generate a new diskless image')
print(' 4 - Manage/list existing diskless images')
print(' 5 - Remove a diskless image')

main_action = str(input('-->: ').lower().strip())

if main_action == '1':

    file_list = os.listdir('/var/www/html/preboot_execution_environment/diskless/kernels/')
    nb_kernels = 0
    kernel_list = [None]
    for i in file_list:
        if 'linu' in i:
            kernel_list[nb_kernels] = i
            nb_kernels = nb_kernels + 1

    print('')
    print('Available kernels:')
    print("    │")
    if kernel_list[0] != None:
        for i in kernel_list:
            if os.path.exists('/var/www/html/preboot_execution_environment/diskless/kernels/initramfs-kernel-'+(i.strip('vmlinuz-'))):
                initramfs_status = bcolors.OKGREEN+'initramfs present'+bcolors.ENDC
            else:
                initramfs_status = bcolors.WARNING+'missing initramfs-kernel-'+i.strip('vmlinuz-')+bcolors.ENDC
            if i == kernel_list[-1]:
                print("    └── "+str(i)+' - '+initramfs_status)
            else:
                print("    ├── "+str(i)+' - '+initramfs_status)
        print('')

elif main_action == '2':

    file_list = os.listdir('/var/www/html/preboot_execution_environment/diskless/kernels/')
    nb_kernels = 0
    kernel_list = [None]
    for i in file_list:
        if 'linu' in i:
            kernel_list[nb_kernels] = i
            nb_kernels = nb_kernels + 1

    print('')
    print('Select kernel:')
    if kernel_list[0] != None:
        for index, i in enumerate(kernel_list):
            print(' '+str(index+1)+' - '+i)
    selected_kernel = str(int(input('-->: ').lower().strip())-1)

    print ('Now generating initramfs...')
    os.system('dracut --xz -v -m "network base nfs" --add "livenet" --add-drivers xfs --no-hostonly --nolvmconf /var/www/html/preboot_execution_environment/diskless/kernels/initramfs-kernel-'+(kernel_list[int(selected_kernel)].strip('vmlinuz-'))+' --force')
    os.chmod('/var/www/html/preboot_execution_environment/diskless/kernels/initramfs-kernel-'+(kernel_list[int(selected_kernel)].strip('vmlinuz-')),0o644)
    print ('Done.')

elif main_action == '3':

    print('New image creation tool.')
    image_types = ["nfs", "livenet"]
    print('Image type ?')
    for index, i in enumerate(image_types):
        print(' '+str(index+1)+' - '+i)
    selected_image_type = str(int(input('-->: ').lower().strip())-1)

    print('Kernel ?')
    file_list = os.listdir('/var/www/html/preboot_execution_environment/diskless/kernels/')
    nb_kernels = 0
    kernel_list = [None]
    for i in file_list:
        if 'linu' in i:
            kernel_list[nb_kernels] = i
            nb_kernels = nb_kernels + 1
    print('')
    print('Select kernel:')
    if kernel_list[0] != None:
        for index, i in enumerate(kernel_list):
            print(' '+str(index+1)+' - '+i)
    selected_kernel = str(int(input('-->: ').lower().strip())-1)

    print('Image name ?')
    selected_image_name = str(input('-->: ').lower().strip())

    password_raw = str(input('Please enter the root password of the new image : '))
    password_hash = crypt.crypt(password_raw, crypt.METHOD_SHA512)

    if selected_image_type == '0': # BASIC NFS

        print('Entering nfs dedicated parameters.')

        print('Do you want to create a new image with the following parameters:')
        print('  Image name: \t\t'+selected_image_name)
        print('  Image type: \t\t'+image_types[int(selected_image_type)])
        print('  Kernel version: \t'+kernel_list[int(selected_kernel)])
        print('  Root password: \t'+password_raw)

        answer = str(input("Confirm ? Enter yes or no: ").lower().strip())

        if answer == "yes":

            print('Cleaning and creating image folders...')
            os.system('rm -Rf /diskless/images/'+selected_image_name)
            os.system('mkdir /diskless/images/'+selected_image_name)
            os.system('mkdir /diskless/images/'+selected_image_name+'/staging')
#            os.system('mkdir /diskless/images/'+selected_image_name+'/golden')
#            os.system('mkdir /diskless/images/'+selected_image_name+'/nodes')
            os.system('rm -Rf /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
            os.system('mkdir /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
            print('Done.')
            print('Generating new ipxe boot file...')
            boot_file_content = '''#!ipxe

echo |
echo | Entering diskless/images/{image_name}/boot.ipxe
echo |

set image-kernel {image_kernel}
set image-initramfs {image_initramfs}

echo | Now starting staging nfs image boot.
echo |
echo | Parameters used:
echo | > Image target: {image_name}
echo | > Image type: nfs in staging single mode
echo | > Console: ${{eq-console}}
echo | > Additional kernel parameters: ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}
echo |
echo | Loading linux ...

kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux=0 text=1 root=nfs:${{next-server}}:/diskless/images/{image_name}/staging/,vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}

echo | Loading initial ramdisk ...

initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}

echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
'''.format(image_name=selected_image_name,image_kernel=kernel_list[int(selected_kernel)],image_initramfs='initramfs-kernel-'+kernel_list[int(selected_kernel)].strip('vmlinuz-'))
            with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/boot.ipxe', "w") as ff:
                ff.write(boot_file_content)
            print('Done.')
            print('Installing new system image...')
            os.system('dnf groupinstall -y "core" --releasever=8 --setopt=module_platform_id=platform:el8 --installroot=/diskless/images/'+selected_image_name+'/staging')
            print('Done.')
            print('Setting password into image...')
            with open('/diskless/images/'+selected_image_name+'/staging/etc/shadow') as ff:
                newText=ff.read().replace('root:*', 'root:'+password_hash)
            with open('/diskless/images/'+selected_image_name+'/staging/etc/shadow', "w") as ff:
                ff.write(newText)
            print('Done.')
            print('Registering new image...')
            file_content = '''image_data:
  image_name: {image_name}
  image_kernel: {image_kernel}
  image_creation_date: {image_date}
  image_type: nfs
  image_status: staging
'''.format(image_name=selected_image_name,image_kernel=kernel_list[int(selected_kernel)],image_date=datetime.today().strftime('%Y-%m-%d'))
            with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml', "w") as ff:
                ff.write(file_content)
            print('Done.')
            print('Done creating image.')

    if selected_image_type == '1': # LIVENET

        print('Entering livenet dedicated parameters.')

        print('Please select livenet image generation profile:')
        print(' 1 - Standard : core (~1.2Gb)')
        print(' 2 - Small NM/DNF : openssh and dnf and NetworkManager (~248Mb)')
        print(' 3 - Small DNF : openssh and dnf (~227Mb)')
        print(' 4 - Small NM : openssh and NetworkManager (~166Mb)')
        print(' 5 - Minimal : openssh only (~129Mb)')
        selected_livenet_type = str(int(input('-->: ').lower().strip()))

        print('Please choose image size, considering /1000: 2M for 2Gb, 600K for 600Mb, etc:')
        selected_livenet_size = str(input('-->: ').strip())

        print('Do you want to create a new image with the following parameters:')
        print('  Image name: \t\t'+selected_image_name)
        print('  Image type: \t\t'+image_types[int(selected_image_type)])
        print('  Kernel version: \t'+kernel_list[int(selected_kernel)])
        print('  Root password: \t'+password_raw)
        print('  Image size /1000: \t'+selected_livenet_size)
        print('  Image profile: \t'+selected_livenet_type)

        answer = str(input("Confirm ? Enter yes or no: ").lower().strip())

        if answer == "yes":

            print('Cleaning and creating image folders...')
            os.system('rm -Rf /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
            os.system('mkdir /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
            print('Done.')
            print('Generating new ipxe boot file...')
            boot_file_content = '''#!ipxe

echo |
echo | Entering diskless/images/{image_name}/boot.ipxe
echo |

echo | Now starting livenet diskless sessions.
echo |
echo | Parameters used:
echo | > Image target: {image_name}
echo | > Image type: livenet
echo | > Console: ${{eq-console}}
echo | > Additional kernel parameters: ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}
echo |
echo | Loading linux ...

set image-kernel {image_kernel}
set image-initramfs {image_initramfs}

kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} root=live:http://${{next-server}}/preboot_execution_environment/diskless/images/{image_name}/squashfs.img rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}

echo | Loading initial ramdisk ...

initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}

echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
'''.format(image_name=selected_image_name,image_kernel=kernel_list[int(selected_kernel)],image_initramfs='initramfs-kernel-'+kernel_list[int(selected_kernel)].strip('vmlinuz-'))
            with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/boot.ipxe', "w") as ff:
                ff.write(boot_file_content)
            print('Done.')
            print('Creating empty image file, format and mount it...')
            os.system('rm -Rf '+image_working_directory+'/LiveOS')
            os.system('mkdir -p '+image_working_directory+'/LiveOS')
            os.system('dd if=/dev/zero of='+image_working_directory+'/LiveOS/rootfs.img bs=1k count='+selected_livenet_size)
            os.system('mkfs.xfs '+image_working_directory+'/LiveOS/rootfs.img')
            os.system('mount -o loop '+image_working_directory+'/LiveOS/rootfs.img /mnt')
            print('Done.')
            print('Generating cache link for dnf...')
            os.system('mkdir /mnt/var/cache/ -p')
            os.system('rm -Rf '+dnf_cache_directory+'/dnfcache')
            os.system('mkdir '+dnf_cache_directory+'/dnfcache')
            os.system('ln -s '+dnf_cache_directory+'/dnfcache/ /mnt/var/cache/dnf')
            print('Done.')
            print('Installing system into image...')
            if selected_livenet_type == '5':
                os.system('dnf install -y iproute procps-ng openssh-server --releasever=8 --installroot=/mnt/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
            elif selected_livenet_type == '4':
                os.system('dnf install -y iproute procps-ng openssh-server NetworkManager --releasever=8 --installroot=/mnt/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
            elif selected_livenet_type == '3':
                os.system('dnf install -y iproute procps-ng openssh-server dnf --releasever=8 --installroot=/mnt/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
            elif selected_livenet_type == '2':
                os.system('dnf install -y iproute procps-ng openssh-server NetworkManager dnf --releasever=8 --installroot=/mnt/ --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest')
            elif selected_livenet_type == '1':
                os.system('dnf groupinstall -y "core" --releasever=8 --setopt=module_platform_id=platform:el8 --installroot=/mnt')
            print('Done.')
            print('Setting password into image...')
            with open('/mnt/etc/shadow') as ff:
                newText=ff.read().replace('root:*', 'root:'+password_hash)
            with open('/mnt/etc/shadow', "w") as ff:
                ff.write(newText)
            print('Done.')
            print('Packaging and moving files. May take some time...')
            os.system('umount /mnt')
#            os.system('rm -Rf /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
#            os.system('mkdir /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
            os.system('mksquashfs '+image_working_directory+' /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/squashfs.img')
            os.system('cp -a '+image_working_directory+'  /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/')
            print('Done.')
            print('Registering new image...')
            file_content = '''image_data:
  image_name: {image_name}
  image_kernel: {image_kernel}
  image_creation_date: {image_date}
  image_type: livenet
'''.format(image_name=selected_image_name,image_kernel=kernel_list[int(selected_kernel)],image_date=datetime.today().strftime('%Y-%m-%d'))
            with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml', "w") as ff:
                ff.write(file_content)
            print('Done.')
            print('Done creating image.')

elif main_action == '4':

    print('Manage images.')
    print(' 1 - List available images')
    print(' 2 - Manage kernel of an image')
    print(' 3 - Create a golden from a staging NFS image')
    print(' 4 - Manage hosts of an NFS image')

    sub_main_action = str(input('-->: ').lower().strip())

    if sub_main_action == '1':
        for i in os.listdir('/var/www/html/preboot_execution_environment/diskless/images/'):
            print('')
            print('  Image name: '+str(i))
            with open('/var/www/html/preboot_execution_environment/diskless/images/'+str(i)+'/image_data.yml', 'r') as f:
                image_dict = yaml.load(f)
            print('    ├── Kernel linked: '+str(image_dict['image_data']['image_kernel']))
            print('    ├── Image type: '+str(image_dict['image_data']['image_type']))
            if str(image_dict['image_data']['image_type']) == 'nfs':
                print('    ├── image status: '+str(image_dict['image_data']['image_status']))
            print('    └── Image creation date: '+str(image_dict['image_data']['image_creation_date']))

    elif sub_main_action == '2':
        print('Manage kernels of an image.')
        print('Please select image to work with')
        images_list = os.listdir('/var/www/html/preboot_execution_environment/diskless/images/')
        for i in range(0,len(images_list)):
            print(' '+str(i+1)+' - '+str(images_list[i]))
        selected_image = images_list[int(input('-->: ').lower().strip())-1]
        with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image+'/image_data.yml', 'r') as f:
            image_dict = yaml.load(f)
        print('Current kernel is: '+str(image_dict['image_data']['image_kernel']))
        print('Please select a new kernel to use in the available kernels list:')
        file_list = os.listdir('/var/www/html/preboot_execution_environment/diskless/kernels/')
        nb_kernels = 0
        kernel_list = [None]
        for i in file_list:
            if 'linu' in i:
                kernel_list[nb_kernels] = i
                nb_kernels = nb_kernels + 1
        if kernel_list[0] != None:
            for index, i in enumerate(kernel_list):
                print(' '+str(index+1)+' - '+i)
        selected_kernel = kernel_list[int(input('-->: ').lower().strip())-1]
        print('Updating image files...')
        file = open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image+'/boot.ipxe','r')
        filebuffer = file.readlines()
        for i in range(len(filebuffer)):
            if 'image-kernel' in filebuffer[i]:
                filebuffer[i] = 'set image-kernel '+selected_kernel+'\n'
            if 'image-initramfs' in filebuffer[i]:
                filebuffer[i] = 'set image-initramfs '+'initramfs-kernel-'+kernel_list[int(selected_kernel)].strip('vmlinuz-')+'\n'
        file.close
        file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node)+'.ipxe','w')
        file.writelines(filebuffer)
        file.close
        file = open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml','r')
        filebuffer = file.readlines()
        for i in range(len(filebuffer)):
            if 'image_kernel' in filebuffer[i]:
                filebuffer[i] = 'image_kernel: '+selected_kernel+'\n'
        file.close
        file = open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml','w')
        file.writelines(filebuffer)
        file.close
        print('Done.')
        print('You will need to restart your running nodes for changes to take effect.')

    elif sub_main_action == '3':
        print('Please select image to work with')
        images_list = os.listdir('/var/www/html/preboot_execution_environment/diskless/images/')
        for i in range(0,len(images_list)):
            print(' '+str(i+1)+' - '+str(images_list[i]))
        selected_image = images_list[int(input('-->: ').lower().strip())-1]
        with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image+'/image_data.yml', 'r') as f:
            image_dict = yaml.load(f)

        if image_dict['image_data']['image_status'] == 'staging':
            print('Image is a staging image. Create a new golden with it?')
            answer = str(input('Enter yes or no: ').lower().strip())
            if answer == "yes":
                print('New golden image name ?')
                selected_image_name = str(input('-->: ').lower().strip())

                print('Creating directories...')
                os.system('rm -Rf /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
                os.system('mkdir /var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name)
                os.system('rm -Rf /diskless/images/'+selected_image_name)
                os.system('mkdir /diskless/images/'+selected_image_name)
#                os.system('mkdir /diskless/images/'+selected_image_name+'/golden')
                os.system('mkdir /diskless/images/'+selected_image_name+'/nodes')
                print('Done.')
                print('Cloning staging image to golden...')
                os.system('cp -a /diskless/images/'+selected_image+'/staging /diskless/images/'+selected_image_name+'/golden')
                print('Done.')
                print('Generating related files...')
                file_content = '''image_data:
  image_name: {image_name}
  image_kernel: {image_kernel}
  image_creation_date: {image_date}
  image_type: nfs
  image_status: golden
'''.format(image_name=selected_image_name,image_kernel=image_dict['image_data']['image_kernel'],image_date=datetime.today().strftime('%Y-%m-%d'))
                with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml', "w") as ff:
                    ff.write(file_content)
                print('Done.')
                boot_file_content = '''#!ipxe

# This file is shared between main image (staging -> golden) and its clones
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

kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux=0 text=1 root=nfs:${{next-server}}:/diskless/images/{image_name}/nodes/${{hostname}},vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}

echo | Loading initial ramdisk ...

initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}

echo | ALL DONE! We are ready.
echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
'''.format(image_name=selected_image_name,image_kernel=image_dict['image_data']['image_kernel'],image_initramfs='initramfs-kernel-'+image_dict['image_data']['image_kernel'].strip('vmlinuz-'))
                with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/boot.ipxe', "w") as ff:
                    ff.write(boot_file_content)
                print('Done.')

#        elif image_dict['image_status'] == 'golden':
#            print('Image is a golden. Switch to staging ?')
#            answer = str(input('Enter yes or no: ').lower().strip())
#            if answer == "yes":
#                file = open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml','r')
#                filebuffer = file.readlines()
#                for i in range(len(filebuffer)):
#                    if 'image_status' in filebuffer[i]:
#                        filebuffer[i] = 'image_status: staging\n'
#                file.close
#                file = open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml','w')
#                file.writelines(filebuffer)
#                file.close
#                file = open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image+'/boot.ipxe','r')
#                filebuffer = file.readlines()
#                for i in range(len(filebuffer)):
#                    if 'image-state' in filebuffer[i]:
#                        filebuffer[i] = 'set image-state staging\n'
#                file = open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image_name+'/image_data.yml','w')
#                file.writelines(filebuffer)
#                file.close

    elif sub_main_action == '4':
        print('Please select image to work with')
        images_list = os.listdir('/var/www/html/preboot_execution_environment/diskless/images/')
        for i in range(0,len(images_list)):
            print(' '+str(i+1)+' - '+str(images_list[i]))
        selected_image = images_list[int(input('-->: ').lower().strip())-1]
        with open('/var/www/html/preboot_execution_environment/diskless/images/'+selected_image+'/image_data.yml', 'r') as f:
            image_dict = yaml.load(f)
        if image_dict['image_data']['image_type'] == 'nfs' and image_dict['image_data']['image_status'] == 'golden':
            

            print('Manages nodes of image '+selected_image)
            print(' 1 - List nodes with the image')
            print(' 2 - Add nodes with the image')
            print(' 3 - Remove nodes with the image')

            sub_sub_main_action = str(input('-->: ').lower().strip())

            if sub_sub_main_action == '1':
                images_nodes_list = os.listdir('/diskless/images/'+selected_image+'/nodes/')
                print('Nodes available with this image:')
                for i in images_nodes_list:
                    print(' - '+i)
            elif sub_sub_main_action == '2':
                print('Please enter nodes range to add:')
                nodes_range = str(input('-->: ').lower().strip())
                print('Cloning, this may take some time...')
                for node in NodeSet(nodes_range):
                    print("Working on node: "+str(node))
                    os.system('cp -a /diskless/images/'+selected_image+'/golden /diskless/images/'+selected_image+'/nodes/'+node)
            elif sub_sub_main_action == '3':
                print('Please enter nodes range to remove:')
                nodes_range = str(input('-->: ').lower().strip())
                print('Deleting, this may take some time...')
                for node in NodeSet(nodes_range):
                    print("Working on node: "+str(node))
                    os.system('rm -Rf /diskless/images/'+selected_image+'/nodes/'+node)





quit()


