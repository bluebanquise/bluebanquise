# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# utils:
#    This module allow to create usefull functions
#
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>, Benoit Leveugle <benoit.leveugle@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license

import yaml
import logging


# Load YAML files
def load_file(filename):
    logging.debug('Loading file ' + filename)
    with open(filename, 'r') as f:
        # return yaml.load(f, Loader=yaml.FullLoader) ## Waiting for PyYaml 5.1
        return yaml.load(f)


# Class that contains colors
class Color():
    # Colors
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    BLINK = '\033[5m'
    ORANGE_BLINK = '\033[1;33;5m'
    GREEN = '\033[32m'
    # Color to close a colored line
    TAG_END = '\033[0m'


# Method to print using color
def printc(text, color):
    """Print a text in the shell with a color

    :param text: The text to print
    :type text: str
    :param color: The color to print
    :type color: str
    """
    print(color + text + Color.TAG_END)


def select_from_list(_list):
    """Display to the user an interface for selecting an element in a list.

    :param _list: The list where to select the item
    :type _list: list of objects
    :return: `selected_item` The selected by the user item
    :rtype: object
    :raises ValueError: When the list is empty
    :raises UserWarning: When the use input is not valid
    """
    # If the list is not empty
    if _list:
        # For each element of the list
        for index, element in enumerate(_list):
            # Print the index+1 value of the element in the list and the value of the element itself
            print(' ' + str(index+1) + ' - ' + element)

    else:
        raise ValueError('Cannot select in an empty list.')

    item_string_index = input('-->: ')
    if item_string_index.isdigit():
        item_index = int(item_string_index) - 1
        # If the list contains item index
        if (0 <= item_index < len(_list)):
            # Get the selected item by it's index
            selected_item = _list[item_index]
            return selected_item

    # If one of the previous condition is not True
    raise UserWarning('Not a valid entry !')
