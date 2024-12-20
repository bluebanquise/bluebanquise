#!/usr/bin/env python3
from argparse import ArgumentParser
import os
import importlib

# Get arguments
parser = ArgumentParser()
parser.add_argument("-s", "--server", dest="server",
                    help="Enable or disable server mode", metavar="NODE", default=False)

passed_arguments, cli_request = parser.parse_known_args()

