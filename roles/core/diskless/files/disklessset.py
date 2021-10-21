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
# 1.3.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>, Benoit Leveugle <benoit.leveugle@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import basic modules
import sys
import logging
from termios import tcflush, TCIFLUSH

# Import diskless modules from path
from diskless.utils import Color, printc, inform, ask
from diskless.kernel_manager import KernelManager
from diskless.image_manager import ImageManager


# Main program
if __name__ == "__main__":

    # Set logging logs level, this level can be configured in order to have more or less logging informations.
    # There are four levels (sorted by logs number): (lot of logs) DEBUG (default) > INFO > WARNING > ERROR (few logs)
    # Set logging level from the first argument
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        logging.root.setLevel(logging.DEBUG)
    elif len(sys.argv) > 1 and sys.argv[1] == '-i':
        logging.root.setLevel(logging.INFO)
    else:
        # Default level
        logging.root.setLevel(logging.WARNING)

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
    printc(BANNER + '\n        Entering BlueBanquise diskless manager (v1.3.0)', Color.BLUE)

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
            printc("\n > Diskless image management", Color.BLUE)

            print(' 1 - Manage and create diskless images (need modules)')
            print(' 2 - List available diskless images')
            print(' 3 - Remove a diskless image')
            print(' 4 - Clone a diskless image')
            print(' 5 - Create an image from a parameters file')
            print(' 6 - Manage kernel of a diskless image')

            # The second part is about other actions
            printc("\n > Other actions", Color.BLUE)

            print(' 7 - List available kernels')
            print(' 8 - Generate a new initramfs\n')
            print(' 9 - Clear a corrupted image (Use only as a last resort)')
            print(' 10 - Exit\n')

            # When the user press CTRL + c in a sub menu, it returns to main menu
            # When the user press CTRL + c in the main menu it exit program
            printc('At any time: (CTRL + c) => Return to this main menu.', Color.BLUE)

            # Answer to get the action to execute
            ask(' Select an action:')

            # Prevent old inputs to be taken as current input by cleaning stdin buffer
            tcflush(sys.stdin, TCIFLUSH)

            # Get user choice
            main_action = input('-->: ')

            # Now that user has made a choice, we are not longer in the main menu
            in_main_menu = False

            # Clear potential previous bad installations before excecuting a main menu action
            ImageManager.clean_installations()

            # With ImageManager.cli_use_modules() we can use all available modules
            if main_action == '1':
                ImageManager.cli_use_modules()

            # Display already created diskless images
            elif main_action == '2':
                ImageManager.cli_display_images()

            # Remove a diskless image
            elif main_action == '3':
                ImageManager.cli_remove_image()

            # Clone a diskless image
            elif main_action == '4':
                ImageManager.cli_clone_image()

            # Create image from a parameters file
            elif main_action == '5':
                ImageManager.cli_create_image_from_parameters()

            # Change the kernel of an existing image
            elif main_action == '6':
                KernelManager.cli_change_kernel()

            # Display available kernels for image
            elif main_action == '7':
                KernelManager.cli_display_kernels()

            # Generate a new initramfs file from an existing kernel
            elif main_action == '8':
                KernelManager.cli_generate_initramfs()

            # Clean an image
            elif main_action == '9':
                ImageManager.cli_clear_image()

            # Exit program
            elif main_action == '10':
                exit()

            # Bad entry
            else:
                inform('\'' + main_action + '\' is not a valid entry. Please enter another value.')

        # When user press CTRL + c
        except KeyboardInterrupt:
            # If user is not in main menu, just return to the main menu
            if in_main_menu is False:
                pass
            # If user is already in main menu, exit program
            elif in_main_menu is True:
                print('')
                exit()

        # Only catch UserWarning type exceptions
        except UserWarning as e:
            # Display to the user a warning message
            inform(str(e))
