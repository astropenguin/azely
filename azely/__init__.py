# coding: utf-8

# information
__version__ = '0.1'
__author__  = 'snoopython'

# standard library
import os
import shutil

# dependent packages
import yaml

# submodules
from .azel import *
from .constants import *
from .locations import *
from .objects import *
from .plotting import *
from .utils import *

# create directory and file (if not existing)
if not os.path.exists(AZELY_DIR):
    os.makedirs(AZELY_DIR)
    shutil.copy(SAMPLE_OBJS, AZELY_DIR)

if not os.path.exists(KNOWN_LOCS):
    with open(KNOWN_LOCS, 'w') as f:
        f.write(yaml.dump({}, default_flow_style=False))

# delete items
del os
del shutil
del yaml
del azel
del constants
del locations
del objects
del plotting
del utils
