# flake8: noqa
__version__ = "0.7.0"
__author__ = "Akio Taniguchi"


# submodules
from . import consts
from . import cache
from . import query
from . import utils
from . import location
from . import object
from . import time
from . import azel


# aliases
from .location import get_location
from .object import get_object
from .time import get_time
from .azel import compute


# for sphinx docs
__all__ = dir()
