# coding: utf-8

# information
__version__ = '0.1'
__author__  = 'Akio Taniguchi'
__license__ = 'MIT'

# standard library
import os

# dependent packages
import azely
import yaml

# submodules
from .utils import *
from .azel import *
from .constants import *
from .locations import *
from .objects import *

# create directory and file (if not existing)
if not os.path.exists(azely.AZELY_DIR):
    os.makedirs(azely.AZELY_DIR)

if not os.path.exists(azely.KNOWN_LOCS):
    with open(azely.KNOWN_LOCS, 'w') as f:
        f.write(yaml.dump({}, default_flow_style=False))

# delete items
del os
del azely
del yaml
del utils
del azel
del constants
del locations
del objects
