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
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Colors
CBLUE = '\033[94m'
CYELLOW = '\033[93m'
CRED = '\033[31m'
CBLINK = '\033[5m'
CORANGE_BLINK = '\033[1;33;5m'
CGREEN = '\033[1;32;40m'
# Color to close a colored line
CEND = '\033[0m'

# Method to print using color
def printc(text, color):
    """Print a text in the shell with a color

    :param text: The text to print
    :type text: str
    :param color: The color to print
    :type color: str
    """
    print (color + text + CEND)

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
        for index, i in enumerate(_list):
            # Print the index+1 vastaglue of the element and the element
            print(' ' + str(index+1) + ' - ' + i)

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