# information
__version__ = '0.2'
__author__  = 'snoopython'

# submodules
from .utils import *
from .azel import *
from .constants import *
from .locations import *
from .objects import *
from .plotting import *

# delete items
del utils
del azel
del constants
del locations
del objects
del plotting

# for convenience
objects = Objects(reload=True)
locations = Locations(reload=True)
