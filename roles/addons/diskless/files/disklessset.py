#!/usr/bin/env python3
#
# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# disklessset script:
#    This python script allows to create and manage diskless
#    images from a linux command line interface.
#
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import basic modules
import sys
import logging
from termios import tcflush, TCIFLUSH

# Add path to files to include
sys.path.append('/lib/python3.6/site-packages/diskless/')

# Import diskless modules from path
from utils import *
from kernel_manager import KernelManager
from image_manager import ImageManager


# Main program
if __name__ == "__main__":

    # Set logging level to INFO level and change default display format
    logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.INFO)
    
    # Set script banner
    BANNER = """\n
  ██████╗ ██╗███████╗██╗  ██╗██╗     ███████╗███████╗███████╗
  ██╔══██╗██║██╔════╝██║ ██╔╝██║     ██╔════╝██╔════╝██╔════╝
  ██║  ██║██║███████╗█████╔╝ ██║     █████╗  ███████╗███████╗
  ██║  ██║██║╚════██║██╔═██╗ ██║     ██╔══╝  ╚════██║╚════██║
  ██████╔╝██║███████║██║  ██╗███████╗███████╗███████║███████║
  ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝
"""
    
    # Print script banner
    printc(BANNER + '\n           Entering BlueBanquise diskless manager', CBLUE)

    # Create a main_action variable
    main_action = ''

    # Stay on main program after a main action executed by the user
    while True:

        # The try/catch manage KeyboardInterrupt and UserWarning program exceptions
        try:
            # When we are in the main menu
            in_main_menu = True

            # Display main menu options
            # There is two parts in this menu

            # The first part is about most used actions
            printc("\n > Diskless image management", CBLUE)

            print(' 1 - Manage and create diskless images (need modules)')
            print(' 2 - List available diskless images')
            print(' 3 - Remove a diskless image')
            print(' 4 - Manage kernel of a diskless image')
            
            # The second part is about other actions
            printc("\n > Other actions", CBLUE)

            print(' 5 - List available kernels')
            print(' 6 - Generate a new initramfs\n')
            print(' 7 - Clear a corrupted image (Use only as a last resort)')
            print(' 8 - Exit\n')
            
            # When the user press CTRL + c in a sub menu, he returns to main menu
            # When the user press CTRL + c in the main menu he exit program 
            printc('At any time: (CTRL + c) => Return to this main menu.\n', CBLUE)

            # Answer to get the action to execute
            print(' Select an action:')
            
            # Prevent old inputs to be taken as current input by cleaning stdin buffer
            tcflush(sys.stdin, TCIFLUSH)

            # Get user choice
            main_action = input('-->: ')
            print('')

            # Now that user has made a choice, we are not longer in the main menu
            in_main_menu = False

            # Clear potential previous bad installations before excecuting a main menu action
            ImageManager.clean_intallations()

            # With ImageManager.cli_use_modules() we can use all available modules
            if main_action == '1':
                ImageManager.cli_use_modules()

            # Display already created diskless images
            elif main_action == '2': 
                ImageManager.cli_display_images()
                printc('\n[OK] Done.', CGREEN)

            # Remove a diskless image
            elif main_action == '3':
                # Get image object to remove
                image = ImageManager.get_created_image(ImageManager.cli_select_created_image())
                printc('\n⚠ Would you realy delete image ' + image.name + ' definitively (yes/no) ?', CRED)

                # get confirmation from user
                confirmation = input('-->: ').replace(" ", "")

                if confirmation == 'yes':
                    # Remove image
                    ImageManager.remove_image(image)
                    printc('\n[OK] Done.', CGREEN)

                elif confirmation == 'no':
                    printc('\n[+] Image deletion cancelled', CYELLOW)

            # Change the kernel of an existing image 
            elif main_action == '4':
                # Select the image to change kernel
                image = ImageManager.get_created_image(ImageManager.cli_select_created_image())
                print('\nCurrent kernel is: '+ image.kernel)
                # Select an available kernel 
                new_kernel = KernelManager.cli_select_kernel()
                # Set image kernel by using image method
                KernelManager.change_kernel(image, new_kernel)
                printc('\n[OK] Done.', CGREEN)

            # Display available kernels for image
            elif main_action == '5':
                KernelManager.cli_display_kernels()
                printc('\n[OK] Done.', CGREEN)

            # Generate a new initramfs file from an existing kernel
            elif main_action == '6':
                selected_kernel = KernelManager.cli_select_kernel()
                KernelManager.generate_initramfs(selected_kernel)
                printc('\n[OK] Done.', CGREEN)

            # Clean an image
            elif main_action == '7':
                # Get list of existing images
                images_names = ImageManager.get_image_names()

                # If there is no images, raise an exception
                if not images_names:
                    raise UserWarning('No images.')
                
                # Don't get in creation images
                image_names = [image_name for image_name in images_names if ImageManager.get_image_status(image_name) != ImageManager.ImageStatus.IN_CREATION]

                # If there is image, select the image
                image_name = select_from_list(image_names)

                printc('\n⚠ Would you realy clean image ' + image_name + ' definitively (yes/no) ?', CRED)

                # get confirmation from user
                confirmation = input('-->: ').replace(" ", "")

                if confirmation == 'yes':
                   # Clean selected image
                    ImageManager.clean_intallation(image_name)
                    printc('\n[OK] Done.', CGREEN)

                elif confirmation == 'no':
                    printc('\n[+] Image cleaning cancelled', CYELLOW)

            # Exit program
            elif main_action == '8':
                exit()

            # Bad entry
            else:
                printc('\n[INFO] \'' + main_action + '\' is not a valid entry. Please enter another value.', CYELLOW)

        # When user press CTRL + c
        except KeyboardInterrupt:
            # If user is not in main menu, just return to the main menu
            if in_main_menu == False:
                pass
            # If user is already in main menu, exit program
            elif in_main_menu == True:
                print('')
                exit()

        # Only catch UserWarning type exceptions
        except UserWarning as e:
            # Display to the user a warning message
            printc('[WARNING] ' + str(e), CYELLOW)

