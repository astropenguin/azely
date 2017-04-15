# coding: utf-8

# standard library
import os

# dependent packages
import yaml

# submodules
from .utils import *
from .locations import *

# information
__version__ = '0.1'
__author__  = 'Akio Taniguchi'
__license__ = 'MIT'

# constants
HOME_DIR = os.environ['HOME']
AZELY_DIR = os.path.join(HOME_DIR, '.azely')
KNOWN_LOCS = os.path.join(AZELY_DIR, 'known_locations.yaml')

# create directory and files (if not exist)
if not os.path.exists(AZELY_DIR):
    os.makedirs(AZELY_DIR)

if not os.path.exists(KNOWN_LOCS):
    with open(KNOWN_LOCS, 'w') as f:
        f.write(yaml.dump({}, default_flow_style=False))
