__version__ = "0.4.3"
__author__ = "Akio Taniguchi"


# immediate functions
def _get_azely_dir():
    """Get path of azely directory."""
    from os import environ, getenv
    from pathlib import Path

    AZELY_DIR = "AZELY_DIR"
    XDG_CONFIG_HOME = "XDG_CONFIG_HOME"

    if AZELY_DIR in environ:
        return Path(getenv(AZELY_DIR))
    elif XDG_CONFIG_HOME in environ:
        return Path(getenv(XDG_CONFIG_HOME)) / "azely"
    else:
        return Path().home() / ".config" / "azely"


# constants
AZELY_DIR = _get_azely_dir()
AZELY_CONFIG = AZELY_DIR / "config.toml"
AZELY_OBJECT = AZELY_DIR / "object.toml"
AZELY_LOCATION = AZELY_DIR / "location.toml"


# base error class
class AzelyError(Exception):
    pass


# submodules
from . import consts  # noqa
from . import utils  # noqa
from .location import *  # noqa
from .object import *  # noqa
from .time import *  # noqa
from .azel import *  # noqa
