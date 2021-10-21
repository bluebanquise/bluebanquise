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
# 1.3.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>, Benoit Leveugle <benoit.leveugle@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license

import yaml
import logging


def load_file(filename):
    """Load a YAML file from a path.

    :param filename: The path to load file.
    :type filename: str
    """

    logging.debug('Loading file ' + filename)
    with open(filename, 'r') as f:
        # return yaml.load(f, Loader=yaml.FullLoader) ## Waiting for PyYaml 5.1
        return yaml.load(f)


class Color():
    """Class that contains all needed color values.
    Each color is represented by a specific shell color expression.
    """

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
    """Print a text in the shell with a color.

    :param text: The text to print
    :type text: str
    :param color: The color to print text
    :type color: Color
    """

    print(color + text + Color.TAG_END)


def display(color, tag, *texts):
    """Print a text in the shell with a color and an tag.

    :param *texts: The texts arguments to print, each argument will be a new line in the shell.
    :type text: str[]
    :param color: The color to print text
    :type color: Color
    :param tag: A string to put in the begining of the text to display
    :type tag: str
    :raises ValueError: When there is a non string value in the textx.
    """

    # Check if all elements are of string type
    if not all(isinstance(item, str) for item in texts):
        raise ValueError("Invalid input")

    # Display first list element
    print(color + '\n' + tag + ' ' + texts[0] + Color.TAG_END)
    # Display other elements in new lines
    for i in range(1, len(texts)):
        print(color + '    ' + texts[i] + Color.TAG_END)


def ask(*texts):
    """Print a text in the shell with the '[+]' tag and the blue color

    :param *texts: Each line to display in the shell
    :type *texts: str
    """

    color = Color.BLUE
    tag = '[+]'
    display(color, tag, *texts)


def ask_module(*texts):
    """Print a text in the shell with the '[+]' tag and the green color

    :param *texts: Each line to display in the shell
    :type *texts: str
    """

    # Color to use in the modules
    color = Color.GREEN
    tag = '[+]'
    display(color, tag, *texts)


def inform(*texts):
    """Print a text in the shell with the '[-]' tag and the yellow color

    :param *texts: Each line to display in the shell
    :type *texts: str
    """

    color = Color.YELLOW
    tag = '[-]'
    display(color, tag, *texts)


def warn(*texts):
    """Print a text in the shell with the '[x]' tag and the red color.

    :param *texts: Each line to display in the shell
    :type *texts: str
    """

    color = Color.RED
    tag = '[x]'
    display(color, tag, *texts)


def ok(text=None):
    """Print a text in the shell with the '[OK]' tag and the green color, or just the '[OK] Done' text.

    :param text: The text to print
    :type text: str
    """
    if text is not None:
        print(Color.GREEN + '\n[OK] ' + text + Color.TAG_END)
    else:
        print(Color.GREEN + '\n[OK] Done' + Color.TAG_END)


def select_from_list(_list):
    """Display to the user an interface for selecting an element in a list.

    :param _list: The list where to select the item
    :type _list: list of objects
    :return: `selected_item` The selected by the user item
    :rtype: object
    :raises ValueError: When the list is empty
    :raises UserWarning: When the user input is not valid
    """

    # If the list is not empty
    if _list:
        # For each element of the list
        for index, element in enumerate(_list):
            # Print the index+1 value of the element in the list and the value of the element itself
            print(' ' + str(index+1) + ' - ' + element)

    else:
        raise ValueError('Cannot select in an empty list.')

    while True:
        item_string_index = input('-->: ')
        if item_string_index.isdigit():
            item_index = int(item_string_index) - 1
            # If the list contains item index
            if (0 <= item_index < len(_list)):
                # Get the selected item by it's index
                selected_item = _list[item_index]
                return selected_item

        inform('\'' + item_string_index + '\' is not in the listed numbers. Please enter another value or return to the main menu (CTRL + c).')
