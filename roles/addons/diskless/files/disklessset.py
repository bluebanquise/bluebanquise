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
# https://github.com/bluebanquise/bluebanquise - MIT license

# Import dependencies
import os
import crypt
import hashlib
import shutil
from argparse import ArgumentParser
from datetime import datetime
from subprocess import check_call

import yaml
from ClusterShell.NodeSet import NodeSet


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


def read_yaml(filename):
    print(bcolors.OKBLUE+'[INFO] Loading '+filename+bcolors.ENDC)
    with open(filename, 'r') as f:
        return yaml.safe_load(f)


def write_yaml(filename, content):
    with open(filename, 'w') as f:
        return yaml.dump(content, f, default_flow_style=False)


def load_kernel_list(kernels_path):
    print(bcolors.OKBLUE+'[INFO] Loading kernels from '+kernels_path+bcolors.ENDC)
    file_list = os.listdir(kernels_path)
    kernel_list = list()
    for i in file_list:
        if 'linu' in i:
            kernel_list.append(i)
    return kernel_list


def select_from_list(list_from, list_name, index_modifier=-1):
    print('\nSelect ' + list_name + ':')
    if list_from[0] is not None and len(list_from) != 0:
        for index, i in enumerate(list_from):
            print(' '+str(index+1)+' - '+i)

    user_input = input('-->: ').strip()

    try:
        selected_item = int(user_input)
    except Exception:
        return select_from_list(list_from, list_name, index_modifier)

    if selected_item < 1 or selected_item > len(list_from):
        return select_from_list(list_from, list_name, index_modifier)

    return selected_item + index_modifier


def generate_ipxe_boot_file(image_type, image_name, image_kernel, image_initramfs, selinux=False):
    if image_type == 'nfs_staging':
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
echo | > Console: ${{eq-console}}
echo | > Additional kernel parameters: ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}}
echo |
echo | Loading linux ...

kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux=0 text=1 root=nfs:${{next-server}}:/diskless/images/{image_name}/staging/,vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4

echo | Loading initial ramdisk ...

initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
'''.format(image_name=image_name, image_kernel=image_kernel, image_initramfs=image_initramfs)
        return boot_file_content
    elif image_type == 'nfs_golden':
        boot_file_content = '''#!ipxe

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

kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} selinux={selinux} text=1 root=nfs:${{next-server}}:/diskless/images/{image_name}/nodes/${{hostname}},vers=4.2,rw rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4

echo | Loading initial ramdisk ...

initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
'''.format(image_name=image_name, image_kernel=image_kernel, image_initramfs=image_initramfs, selinux=int(selinux))
        return boot_file_content
    elif image_type == 'livenet':
        boot_file_content = '''#!ipxe

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

kernel http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-kernel}} initrd=${{image-initramfs}} root=live:http://${{next-server}}/preboot_execution_environment/diskless/images/{image_name}/squashfs.img rw ${{eq-console}} ${{eq-kernel-parameters}} ${{dedicated-kernel-parameters}} rd.net.timeout.carrier=30 rd.net.timeout.ifup=60 rd.net.dhcp.retry=4 selinux={selinux}

echo | Loading initial ramdisk ...

initrd http://${{next-server}}/preboot_execution_environment/diskless/kernels/${{image-initramfs}}

echo | ALL DONE! We are ready.
echo | Downloaded images report:

imgstat

echo | Booting in 4s ...
echo |
echo +----------------------------------------------------+

sleep 4

boot
'''.format(image_name=image_name, image_kernel=image_kernel, image_initramfs=image_initramfs, selinux=int(selinux))
        return boot_file_content


# Get arguments passed
parser = ArgumentParser()
passed_arguments = parser.parse_args()

dnf_cache_directory = '/root/dnf'  # '/dev/shm/'
image_working_directory_base = '/var/tmp/diskless/workdir/'
kernels_path = '/var/www/html/preboot_execution_environment/diskless/kernels/'
images_path = '/var/www/html/preboot_execution_environment/diskless/images/'

print('BlueBanquise Diskless manager')
print(' 1 - List available kernels')
print(' 2 - Generate a new initramfs')
print(' 3 - Generate a new diskless image')
print(' 4 - Manage existing diskless images')

main_action = str(input('-->: ').lower().strip())

if main_action == '1':

    kernel_list = load_kernel_list(kernels_path)

    print('')
    print('Available kernels:')
    print("    │")
    if len(kernel_list) > 0:
        for i in kernel_list:
            if os.path.exists(kernels_path+'/initramfs-kernel-'+(i.strip('vmlinuz-'))):
                initramfs_status = bcolors.OKGREEN+'initramfs present'+bcolors.ENDC
            else:
                initramfs_status = bcolors.WARNING+'missing initramfs-kernel-'+i.strip('vmlinuz-')+bcolors.ENDC
            if i == kernel_list[-1]:
                print("    └── "+str(i)+' - '+initramfs_status)
            else:
                print("    ├── "+str(i)+' - '+initramfs_status)
        print(bcolors.OKGREEN+'\n[OK] Done.'+bcolors.ENDC)
    else:
        print(bcolors.WARNING+'[WARNING] No kernel found!'+bcolors.ENDC)

elif main_action == '2':

    kernel_list = load_kernel_list(kernels_path)

    if len(kernel_list) > 0:
        selected_kernel = select_from_list(kernel_list, 'kernel')
    else:
        print(bcolors.FAIL+'[ERROR] No kernel found!'+bcolors.ENDC)
        exit(1)

    print(bcolors.OKBLUE+'[INFO] Now generating initramfs... May take some time.'+bcolors.ENDC)
    os.system('dracut --xz -v -m "network base nfs" --add "livenet" --add-drivers xfs --no-hostonly --nolvmconf ' + kernels_path + '/initramfs-kernel-' + (kernel_list[selected_kernel].strip('vmlinuz-')) + ' --force --kver={}'.format(kernel_list[selected_kernel].strip('vmlinuz-')))
    os.chmod(kernels_path + '/initramfs-kernel-' + (kernel_list[selected_kernel].strip('vmlinuz-')), 0o644)
    print(bcolors.OKGREEN+'\n[OK] Done.'+bcolors.ENDC)

elif main_action == '3':

    print('\nStarting new image creation phase.')
    print('Many questions will be asked, a recap will be provided before starting procedure.')

    image_types = ["nfs", "livenet"]

    selected_image_type = select_from_list(image_types, 'image type')

    kernel_list = load_kernel_list(kernels_path)
    if len(kernel_list) > 0:
        selected_kernel = select_from_list(kernel_list, 'kernel')
    else:
        print(bcolors.FAIL+'[ERROR] No kernel found!'+bcolors.ENDC)
        exit(1)

    print('Please enter image name ?')
    selected_image_name = str(input('-->: ').lower().strip())

    password_raw = str(input('Please enter clear root password of the new image: '))
    password_hash = crypt.crypt(password_raw, crypt.METHOD_SHA512)

    if selected_image_type == 0:  # BASIC NFS

        print(bcolors.OKBLUE + '[INFO] Entering nfs dedicated part.' + bcolors.ENDC)

        print('Do you want to create a new NFS image with the following parameters:')
        print('  Image name: \t\t' + selected_image_name)
        print('  Kernel version: \t' + kernel_list[selected_kernel])
        print('  Root password: \t' + password_raw)

        answer = str(input("Confirm ? Enter yes or no: ").lower().strip())
        if answer in ['yes', 'y']:

            print(bcolors.OKBLUE + '[INFO] Cleaning and creating image folders.' + bcolors.ENDC)
            try:
                shutil.rmtree(os.path.join('/diskless/images/', selected_image_name))
                os.makedirs(os.path.join('/diskless/images/', selected_image_name, 'staging'))
                shutil.rmtree(os.path.join(images_path, selected_image_name))
                os.mkdir(os.path.join(images_path, selected_image_name))
            except OSError as e:
                print(bcolors.FAIL + '[ERROR] Cannot clean or create image folders: ' + str(e) + bcolors.ENDC)

            print(bcolors.OKBLUE+'[INFO] Generating new ipxe boot file.'+bcolors.ENDC)
            boot_file_content = generate_ipxe_boot_file('nfs_staging', selected_image_name, kernel_list[selected_kernel], 'initramfs-kernel-' + kernel_list[selected_kernel].strip('vmlinuz-'))
            with open(os.path.join(images_path, selected_image_name, 'boot.ipxe'), "w") as ff:
                ff.write(boot_file_content)

            print(bcolors.OKBLUE+'[INFO] Installing new system image... May take some time.'+bcolors.ENDC)
            os.system('dnf groupinstall -y "core" --setopt=module_platform_id=platform:el8 --installroot=/diskless/images/'+selected_image_name+'/staging')

            print(bcolors.OKBLUE+'[INFO] Setting password into image.'+bcolors.ENDC)
            with open('/diskless/images/'+selected_image_name+'/staging/etc/shadow') as ff:
                newText = ff.read().replace('root:*', 'root:'+password_hash)
            with open('/diskless/images/'+selected_image_name+'/staging/etc/shadow', "w") as ff:
                ff.write(newText)

            print(bcolors.OKBLUE+'[INFO] Registering new image.'+bcolors.ENDC)

            metadata = dict()
            metadata['image_name'] = selected_image_name
            metadata['image_kernel'] = kernel_list[selected_kernel]
            metadata['image_creation_date'] = datetime.today().strftime('%Y-%m-%d')
            metadata['image_type'] = 'nfs'
            metadata['image_status'] = 'staging'
            try:
                write_yaml(os.path.join(images_path, selected_image_name, 'image_metadata.yml'), metadata)
            except Exception as e:
                print(e)
            print(bcolors.OKGREEN+'\n[OK] Done creating image.'+bcolors.ENDC)

    if selected_image_type == 1:  # LIVENET

        print(bcolors.OKBLUE+'[INFO] Entering livenet dedicated part.'+bcolors.ENDC)

        print('Please select livenet image generation profile:')
        print(' 1 - Standard: core')
        print(' 2 - Small: openssh, dnf and NetworkManager')
        print(' 3 - Minimal: openssh only')
        print(' 4 - Custom: core + selection of additional packages')

        selected_livenet_type = str(int(input('-->: ').lower().strip()))

        if selected_livenet_type == '4':
            print('Enter list of additional packages to install:')
            selected_packages_list = str(input('-->: ').strip())

        print('Please choose image size:')
        print('(supported units: M=1024*1024, G=1024*1024*1024)')
        print('(Example: 5120M or 5G)')
        selected_livenet_size = str(input('-->: ').strip())
        if selected_livenet_size[-1] == 'G':
            livenet_size = int(selected_livenet_size[:-1])*1024
        elif selected_livenet_size[-1] == 'M':
            livenet_size = int(selected_livenet_size[:-1])

        print('Enter path to SSH public key (left empty to disable key injection):')
        selected_ssh_pub_key = str(input('-->: ').strip())
        if selected_ssh_pub_key and not os.path.exists(selected_ssh_pub_key):
            print('SSH public key not found: {0}'.format(selected_ssh_pub_key))
            exit(1)

        print('Do you want to activate SELinux inside the image?')
        answer_selinux = str(input('Enter yes or no: ').lower().strip())
        if answer_selinux in ['yes', 'y']:
            selinux = True
        else:
            selinux = False

        print('Do you want to create a new livenet image with the following parameters:')
        print('  Image name: \t\t' + selected_image_name)
        print('  Kernel version: \t' + kernel_list[selected_kernel])
        print('  Root password: \t' + password_raw)
        print('  Image profile: \t' + selected_livenet_type)
        print('  Image size: \t\t' + str(livenet_size)+'M')
        print('  SSH pubkey: \t\t' + str(selected_ssh_pub_key))
        print('  Enable SELinux: \t' + str(answer_selinux))
        if selected_livenet_type == '4':
            print('  Additional packages: \t' + selected_packages_list)

        answer = str(input("Confirm ? Enter yes or no: ").lower().strip())

        if answer in ['yes', 'y']:

            image_working_directory = os.path.join(image_working_directory_base, selected_image_name)
            try:
                os.makedirs(image_working_directory)
            except FileExistsError:
                print(bcolors.WARNING + '[WARNING] The directory ' + image_working_directory + ' already exists. Cleaning.' + bcolors.ENDC)
                os.system('umount ' + os.path.join(image_working_directory, 'LiveOS/rootfs.img'))
                shutil.rmtree(image_working_directory)
                os.makedirs(image_working_directory)
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot create directory ' + image_working_directory + bcolors.ENDC)

            installroot = os.path.join(image_working_directory, 'mnt')
            try:
                os.mkdir(installroot)
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot create directory ' + installroot + bcolors.ENDC)

            print(bcolors.OKBLUE+'[INFO] Cleaning and creating image folders.'+bcolors.ENDC)
            try:
                os.mkdir(os.path.join(images_path, selected_image_name))
            except FileExistsError:
                print(bcolors.WARNING + '[WARNING] The directory ' + os.path.join(images_path, selected_image_name) + ' already exists. Cleaning.' + bcolors.ENDC)
                shutil.rmtree(os.path.join(images_path, selected_image_name))
                os.mkdir(os.path.join(images_path, selected_image_name))
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot clean or create image folder ' + os.path.join(images_path, selected_image_name) + bcolors.ENDC)

            print(bcolors.OKBLUE + '[INFO] Generating new ipxe boot file.' + bcolors.ENDC)
            boot_file_content = generate_ipxe_boot_file('livenet', selected_image_name, kernel_list[selected_kernel], 'initramfs-kernel-' + kernel_list[selected_kernel].strip('vmlinuz-'), selinux)
            with open(os.path.join(images_path, selected_image_name, 'boot.ipxe'), "w") as ff:
                ff.write(boot_file_content)

            print(bcolors.OKBLUE + '[INFO] Creating empty image file, format and mount it.' + bcolors.ENDC)
            os.mkdir(os.path.join(image_working_directory, 'LiveOS'))
            os.system('dd if=/dev/zero of=' + os.path.join(image_working_directory, 'LiveOS/rootfs.img') + ' bs=1M count=' + str(livenet_size))
            os.system('mkfs.xfs ' + os.path.join(image_working_directory, 'LiveOS/rootfs.img'))
            if selinux:
                os.system('mount -o defcontext="system_u:object_r:default_t:s0",loop ' + os.path.join(image_working_directory, 'LiveOS/rootfs.img') + ' ' + installroot)
            else:
                os.system('mount -o loop ' + os.path.join(image_working_directory, 'LiveOS/rootfs.img') + ' ' + installroot)

            print(bcolors.OKBLUE+'[INFO] Installing system into image.'+bcolors.ENDC)
            if selected_livenet_type == '3':
                os.system('dnf install -y iproute procps-ng openssh-server  --installroot={0} --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest'.format(installroot))
            elif selected_livenet_type == '2':
                os.system('dnf install -y iproute procps-ng openssh-server NetworkManager  --installroot={0} --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest'.format(installroot))
                os.system('dnf install -y dnf yum --installroot={0} --exclude glibc-all-langpacks --exclude cracklib-dicts --exclude grubby --exclude libxkbcommon --exclude pinentry --exclude python3-unbound --exclude unbound-libs --exclude xkeyboard-config --exclude trousers --exclude diffutils --exclude gnupg2-smime --exclude openssl-pkcs11 --exclude rpm-plugin-systemd-inhibit --exclude shared-mime-info --exclude glibc-langpack-* --setopt=module_platform_id=platform:el8 --nobest'.format(installroot))
            elif selected_livenet_type == '1':
                os.system('dnf groupinstall -y "core"  --setopt=module_platform_id=platform:el8 --installroot={0}'.format(installroot))
            elif selected_livenet_type == '4':
                try:
                    if os.system('dnf install -y @core {0} --setopt=module_platform_id=platform:el8 --installroot={1}'.format(selected_packages_list, installroot)) != 0:
                        raise Exception('dnf install failed')
                except Exception as e:
                    print(bcolors.FAIL+'[ERROR] '+str(e)+': a package was not found or the repositories are broken.'+bcolors.ENDC)
                    exit(1)

            print(bcolors.OKBLUE+'[INFO] Setting password into image.'+bcolors.ENDC)
            with open(os.path.join(installroot, 'etc/shadow'), "r+") as ff:
                newText = ff.read().replace('root:*', 'root:'+password_hash)
                ff.seek(0)
                ff.write(newText)

            if selected_ssh_pub_key:
                print(bcolors.OKBLUE+'[INFO] Injecting SSH public key into image.'+bcolors.ENDC)
                os.mkdir(os.path.join(installroot, 'root/.ssh'))
                shutil.copyfile(selected_ssh_pub_key, os.path.join(installroot, 'root/.ssh/authorized_keys'))

            print(bcolors.OKBLUE+'[INFO] Setting image information.'+bcolors.ENDC)
            with open(os.path.join(installroot, 'etc/os-release'), 'a') as ff:
                ff.writelines(['BLUEBANQUISE_IMAGE_NAME="{0}"\n'.format(selected_image_name),
                               'BLUEBANQUISE_IMAGE_KERNEL="{0}"\n'.format(kernel_list[selected_kernel]),
                               'BLUEBANQUISE_IMAGE_DATE="{0}"\n'.format(datetime.today().strftime('%Y-%m-%d'))])

            if selinux:
                print(bcolors.OKBLUE+'[INFO] Enabling SELinux.'+bcolors.ENDC)
                os.system('dnf install -y libselinux-utils policycoreutils selinux-policy-targeted --installroot={0} --setopt=module_platform_id=platform:el8 --nobest'.format(installroot))
                check_call('mount --bind /proc '+os.path.join(installroot, 'proc'), shell=True)
                check_call('mount --bind /sys '+os.path.join(installroot, 'sys'), shell=True)
                check_call('mount --bind /sys/fs/selinux '+os.path.join(installroot, 'sys/fs/selinux'), shell=True)
                real_root = os.open("/", os.O_RDONLY)
                os.chroot(installroot)
                os.chdir("/")

                check_call('restorecon -Rv /', shell=True)

                os.fchdir(real_root)
                os.chroot(".")
                os.close(real_root)
                check_call('umount ' + installroot + '/{sys/fs/selinux,sys,proc}', shell=True)

            print(bcolors.OKBLUE+'[INFO] Packaging and cleaning files... May take some time.'+bcolors.ENDC)
            os.system('umount ' + installroot)
            os.rmdir(installroot)
            os.system('mksquashfs ' + image_working_directory + ' ' + os.path.join(images_path, selected_image_name, 'squashfs.img'))
            try:
                sha256sum = hashlib.sha256(open(os.path.join(images_path, selected_image_name, 'squashfs.img'), 'rb').read()).hexdigest()
            except Exception as e:
                print(e)
            shutil.rmtree(image_working_directory)

            print(bcolors.OKBLUE+'[INFO] Registering new image.'+bcolors.ENDC)
            metadata = dict()
            metadata['image_name'] = selected_image_name
            metadata['image_kernel'] = kernel_list[selected_kernel]
            metadata['image_creation_date'] = datetime.today().strftime('%Y-%m-%d')
            metadata['image_creation_timestamp'] = int(datetime.now().timestamp())
            metadata['image_selinux_enabled'] = selinux
            metadata['image_sha256'] = sha256sum
            metadata['image_size'] = livenet_size  # Size unit: MiB
            metadata['image_type'] = 'livenet'
            try:
                write_yaml(os.path.join(images_path, selected_image_name, 'image_metadata.yml'), metadata)
            except Exception as e:
                print(e)
            print(bcolors.OKGREEN+'\n[OK] Done creating image.'+bcolors.ENDC)

elif main_action == '4':

    print(bcolors.OKBLUE+'[INFO] Entering images management part.'+bcolors.ENDC)

    print(' 1 - List available images')
    print(' 2 - Manage kernel of an image')
    print(' 3 - Create a golden from a staging NFS image')
    print(' 4 - Manage hosts of an NFS image')
    print(' 5 - Manage livenet images')
    print(' 6 - Remove an image')
    sub_main_action = str(input('-->: ').lower().strip())

    if sub_main_action == '1':
        for image in os.listdir(images_path):
            if os.path.exists(os.path.join(images_path, str(image), 'image_metadata.yml')):
                image_info = read_yaml(os.path.join(images_path, str(image), 'image_metadata.yml'))
                print('')
                print('  Image name: '+str(image))
                print('    ├── Kernel linked: '+str(image_info['image_kernel']))
                print('    ├── Image type: '+str(image_info['image_type']))
                if str(image_info['image_type']) == 'nfs':
                    print('    ├── image status: '+str(image_info['image_status']))
                print('    └── Image creation date: '+str(image_info['image_creation_date']))
            else:
                print(bcolors.WARNING + '[WARNING] The image \'' + image + '\' is incomplete.' + bcolors.ENDC)

    elif sub_main_action == '2':
        print('Manage kernels of an image.')

        images_list = os.listdir(images_path)
        if not images_list:
            print(bcolors.FAIL+'[ERROR] No image found!'+bcolors.ENDC)
            exit(1)

        selected_image = select_from_list(images_list, 'image to work with')
        selected_image_name = images_list[selected_image]

        image_info = read_yaml(os.path.join(images_path, selected_image_name, 'image_metadata.yml'))
        print('Current kernel is: '+str(image_info['image_kernel']))

        kernel_list = load_kernel_list(kernels_path)
        if len(kernel_list) > 0:
            selected_kernel = select_from_list(kernel_list, 'a new kernel to use in the available kernels list')
        else:
            print(bcolors.FAIL+'[ERROR] No kernel found!'+bcolors.ENDC)
            exit(1)

        print(bcolors.OKBLUE+'[INFO] Updating image files.'+bcolors.ENDC)
        file = open(os.path.join(images_path, selected_image_name, 'boot.ipxe'), 'r')
        filebuffer = file.readlines()
        for i in range(len(filebuffer)):
            if 'image-kernel' in filebuffer[i]:
                filebuffer[i] = 'set image-kernel '+kernel_list[selected_kernel]+'\n'
            if 'image-initramfs' in filebuffer[i]:
                filebuffer[i] = 'set image-initramfs '+'initramfs-kernel-'+kernel_list[selected_kernel].strip('vmlinuz-')+'\n'
        file.close
        file = open(os.path.join(images_path, selected_image_name, 'boot.ipxe'), 'w')
        file.writelines(filebuffer)
        file.close
        try:
            image_info = read_yaml(os.path.join(images_path, selected_image_name, 'image_metadata.yml'))
            image_info['image_kernel'] = kernel_list[selected_kernel]
            write_yaml(os.path.join(images_path, selected_image_name, 'image_metadata.yml'), image_info)
        except Exception as e:
            print(e)
        print(bcolors.OKGREEN+'\n[OK] Done.\nYou will need to restart your running nodes for changes to take effect.'+bcolors.ENDC)

    elif sub_main_action == '3':

        images_list = os.listdir(images_path)
        if not images_list:
            print(bcolors.FAIL+'[ERROR] No image found!'+bcolors.ENDC)
            exit(1)

        selected_image = select_from_list(images_list, 'image to work with')
        selected_image_name_copy = images_list[selected_image]

        image_info = read_yaml(os.path.join(images_path, selected_image_name_copy, 'image_metadata.yml'))

        if image_info['image_type'] != 'nfs':
            print('Error: This is not an NFS image.')
        elif image_info['image_status'] == 'staging':
            print('Image is a staging image. Create a new golden with it?')
            answer = str(input('Enter yes or no: ').lower().strip())
            if answer in ['yes', 'y']:
                print('New golden image name ?')
                selected_image_name = str(input('-->: ').lower().strip())

                print(bcolors.OKBLUE+'[INFO] Creating directories.'+bcolors.ENDC)
                try:
                    shutil.rmtree(os.path.join(images_path, selected_image_name))
                    os.mkdir(os.path.join(images_path, selected_image_name))
                    shutil.rmtree(os.path.join('/diskless/images/', selected_image_name))
                    os.makedirs(os.path.join('/diskless/images/', selected_image_name, 'nodes'))
                except OSError as e:
                    print(bcolors.FAIL + '[ERROR] Cannot create directories: ' + str(e) + bcolors.ENDC)

                print(bcolors.OKBLUE+'[INFO] Cloning staging image to golden.'+bcolors.ENDC)
                os.system('cp -a /diskless/images/'+selected_image_name_copy+'/staging /diskless/images/'+selected_image_name+'/golden')
                print(bcolors.OKBLUE+'[INFO] Generating related files.'+bcolors.ENDC)

                metadata = dict()
                metadata['image_name'] = selected_image_name
                metadata['image_kernel'] = image_info['image_kernel']
                metadata['image_creation_date'] = datetime.today().strftime('%Y-%m-%d')
                metadata['image_type'] = 'nfs'
                metadata['image_status'] = 'golden'
                try:
                    write_yaml(os.path.join(images_path, selected_image_name, 'image_metadata.yml'), metadata)
                except Exception as e:
                    print(e)
                print(bcolors.OKBLUE+'[INFO] Generating new ipxe boot file.'+bcolors.ENDC)
                boot_file_content = generate_ipxe_boot_file('nfs_golden', selected_image_name, image_info['image_kernel'], 'initramfs-kernel-'+image_info['image_kernel'].strip('vmlinuz-'))
            with open(os.path.join(images_path, selected_image_name, 'boot.ipxe'), "w") as ff:
                ff.write(boot_file_content)

    elif sub_main_action == '4':
        print('Please select image to work with')
        images_list = os.listdir(images_path)
        if not images_list:
            print(bcolors.FAIL+'[ERROR] No image found!'+bcolors.ENDC)
            exit(1)

        for i in range(0, len(images_list)):
            print(' '+str(i+1)+' - '+str(images_list[i]))
        selected_image = images_list[int(input('-->: ').lower().strip())-1]
        image_info = read_yaml(os.path.join(images_path, selected_image, 'image_metadata.yml'))

        if image_info['image_type'] != 'nfs':
            print('Error: This is not an NFS image.')
        elif image_info['image_status'] == 'golden':

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
                print(bcolors.OKBLUE+'[INFO] Cloning, this may take some time...'+bcolors.ENDC)
                for node in NodeSet(nodes_range):
                    print("Working on node: "+str(node))
                    os.system('cp -a /diskless/images/'+selected_image+'/golden /diskless/images/'+selected_image+'/nodes/'+node)
            elif sub_sub_main_action == '3':
                print('Please enter nodes range to remove:')
                nodes_range = str(input('-->: ').lower().strip())
                print(bcolors.OKBLUE+'[INFO] Deleting, this may take some time...'+bcolors.ENDC)
                for node in NodeSet(nodes_range):
                    print("Working on node: "+str(node))
                    shutil.rmtree(os.path.join('/diskless/images/', selected_image, 'nodes', node))

    elif sub_main_action == '5':
        print('Manages livenet images')
        print(' 1 - Unsquash and mount')
        print(' 2 - Unmount and squash')
        print(' 3 - Resize')
        sub_sub_main_action = str(input('-->: ').lower().strip())

        if sub_sub_main_action == '1':

            images_list = os.listdir(images_path)
            if not images_list:
                print(bcolors.FAIL + '[ERROR] No image found.' + bcolors.ENDC)
                exit(1)

            selected_image = select_from_list(images_list, 'image to work with')
            selected_image_name = images_list[selected_image]

            image_working_directory = os.path.join(image_working_directory_base, selected_image_name)

            print(bcolors.OKBLUE + '[INFO] Creating new working dirs' + bcolors.ENDC)
            try:
                os.makedirs(image_working_directory)
            except FileExistsError:
                print(bcolors.WARNING + '[WARNING] The directory ' + image_working_directory + ' already exists. Cleaning.' + bcolors.ENDC)
                shutil.rmtree(image_working_directory)
                os.makedirs(image_working_directory)
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot create directory ' + image_working_directory + bcolors.ENDC)

            try:
                os.mkdir(os.path.join(image_working_directory, 'mnt'))
                os.mkdir(os.path.join(image_working_directory, 'inventory'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Unsquash image' + bcolors.ENDC)
            try:
                os.system('unsquashfs -d ' + os.path.join(image_working_directory, 'squashfs-root') + ' ' + os.path.join(images_path, selected_image_name, 'squashfs.img'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Mounting image' + bcolors.ENDC)
            try:
                os.system('mount ' + os.path.join(image_working_directory, 'squashfs-root/LiveOS/rootfs.img') + ' ' + os.path.join(image_working_directory, 'mnt/'))
                os.system('mount --bind /proc ' + os.path.join(image_working_directory, 'mnt/proc/'))
                os.system('mount --bind /sys ' + os.path.join(image_working_directory, 'mnt/sys/'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Generating temporary inventory' + bcolors.ENDC)
            try:
                os.system('echo ' + image_working_directory + '/mnt ansible_connection=chroot > ' + image_working_directory + '/inventory/host')
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKGREEN + '[OK] Done' + bcolors.ENDC)
            exit(0)

        if sub_sub_main_action == '2':

            images_list = os.listdir(image_working_directory_base)
            if not images_list:
                print(bcolors.FAIL + '[ERROR] No image found.' + bcolors.ENDC)
                exit(1)

            selected_image = select_from_list(images_list, 'image to work with')
            selected_image_name = images_list[selected_image]

            image_working_directory = os.path.join(image_working_directory_base, selected_image_name)

            print(bcolors.OKBLUE + '[INFO] Unmouting image' + bcolors.ENDC)
            try:
                os.system('umount ' + os.path.join(image_working_directory, 'mnt/proc/'))
                os.system('umount ' + os.path.join(image_working_directory, 'mnt/sys/'))
                os.system('umount ' + os.path.join(image_working_directory, 'mnt/'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Backing up old image and generating new one.' + bcolors.ENDC)
            print(bcolors.OKBLUE + '[INFO] Backup at /var/www/html/preboot_execution_environment/diskless/images/' + selected_image_name + '/squashfs.img.bkp' + bcolors.ENDC)
            try:
                os.rename(os.path.join(images_path, selected_image_name, 'squashfs.img'), os.path.join(images_path, selected_image_name, 'squashfs.img.bkp'))
                os.system('mksquashfs ' + os.path.join(image_working_directory, 'squashfs-root/') + ' ' + os.path.join(images_path, selected_image_name, 'squashfs.img'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Cleaning backup and working dirs' + bcolors.ENDC)
            try:
                shutil.rmtree(image_working_directory)
                os.remove(os.path.join(images_path, selected_image_name, 'squashfs.img.bkp'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKGREEN + '[OK] Done' + bcolors.ENDC)

            exit(0)

        if sub_sub_main_action == '3':

            images_list = os.listdir(images_path)
            if not images_list:
                print(bcolors.FAIL + '[ERROR] No image found.' + bcolors.ENDC)
                exit(1)

            selected_image = select_from_list(images_list, 'image to work with')
            selected_image_name = images_list[selected_image]

            image_working_directory = os.path.join(image_working_directory_base, selected_image_name)

            print('Please choose image new size:')
            print('(supported units: M=1024*1024, G=1024*1024*1024)')
            print('Current tool version do NOT check anything, be carefull to choose enough space')
            selected_livenet_size = str(input('-->: ').strip())
            if selected_livenet_size[-1] == 'G':
                livenet_size = int(selected_livenet_size[:-1])*1024
            elif selected_livenet_size[-1] == 'M':
                livenet_size = int(selected_livenet_size[:-1])

            print(bcolors.OKBLUE + '[INFO] Creating new working dirs' + bcolors.ENDC)
            try:
                os.makedirs(image_working_directory)
            except FileExistsError:
                print(bcolors.WARNING + '[WARNING] The directory ' + image_working_directory + ' already exists. Cleaning.' + bcolors.ENDC)
                shutil.rmtree(image_working_directory)
                os.makedirs(image_working_directory)
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot create directory ' + image_working_directory + bcolors.ENDC)

            try:
                os.makedirs(image_working_directory + '_copy/squashfs-root/LiveOS/')
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot create directory ' + image_working_directory + '_copy/squashfs-root/LiveOS/' + bcolors.ENDC)
            try:
                os.makedirs(os.path.join(image_working_directory, 'mnt'))
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot create directory ' + os.path.join(image_working_directory, 'mnt') + bcolors.ENDC)
            try:
                os.makedirs(os.path.join(image_working_directory, 'mnt_copy'))
            except OSError:
                print(bcolors.FAIL + '[ERROR] Cannot create directory ' + os.path.join(image_working_directory, 'mnt_copy') + bcolors.ENDC)

            print(bcolors.OKBLUE + '[INFO] Generating and mounting new empty image' + bcolors.ENDC)
            try:
                os.system('dd if=/dev/zero of=/' + image_working_directory + '_copy/squashfs-root/LiveOS/rootfs.img bs=1M count=' + str(livenet_size))
                os.system('mkfs.xfs ' + image_working_directory + '_copy/squashfs-root/LiveOS/rootfs.img')
                os.system('mount ' + image_working_directory + '_copy/squashfs-root/LiveOS/rootfs.img ' + os.path.join(image_working_directory, 'mnt_copy/'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Unsquash and mount previous image' + bcolors.ENDC)
            try:
                os.system('unsquashfs -d ' + os.path.join(image_working_directory, 'squashfs-root') + ' ' + os.path.join(images_path, selected_image_name, 'squashfs.img'))
                os.system('mount ' + os.path.join(image_working_directory, 'squashfs-root/LiveOS/rootfs.img') + ' ' + os.path.join(image_working_directory, 'mnt/'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Dumping image: old_image -> cache -> new_image...' + bcolors.ENDC)
            try:
                os.system('xfsdump -l 0 -L ' + selected_image_name + ' -M media -f ' + image_working_directory + 'image.xfsdump ' + os.path.join(image_working_directory, 'mnt'))
                os.system('xfsrestore -f ' + image_working_directory + 'image.xfsdump ' + os.path.join(image_working_directory, 'mnt_copy'))
                os.system('rm -f ' + image_working_directory + 'image.xfsdump')
                os.sync()
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Unmounting both images' + bcolors.ENDC)
            try:
                os.system('umount ' + os.path.join(image_working_directory, 'mnt_copy/'))
                os.system('umount ' + os.path.join(image_working_directory, 'mnt/'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Removing old squashfs and generating new one...' + bcolors.ENDC)
            try:
                os.remove(os.path.join(images_path, selected_image_name, 'squashfs.img'))
                os.system('mksquashfs ' + image_working_directory + '_copy/squashfs-root/ ' + os.path.join(images_path, selected_image_name, 'squashfs.img'))
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKBLUE + '[INFO] Cleaning' + bcolors.ENDC)
            try:
                shutil.rmtree(image_working_directory)
                shutil.rmtree(image_working_directory + '_copy')
            except Exception as e:
                print(e)
                raise

            print(bcolors.OKGREEN + '[OK] Done' + bcolors.ENDC)

            exit(0)

    elif sub_main_action == '6':
        print('Remove an image.')

        images_list = os.listdir(images_path)
        if not images_list:
            print(bcolors.OKGREEN+'[OK] No image found.'+bcolors.ENDC)
            exit(0)

        selected_image = select_from_list(images_list, 'image to work with')
        selected_image_name = images_list[selected_image]

        try:
            shutil.rmtree(os.path.join(images_path, selected_image_name))
            print("Image "+selected_image_name+" has been deleted.")
        except Exception as e:
            print(e)
            raise

quit()
