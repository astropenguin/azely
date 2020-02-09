__version__ = "0.4.2"
__author__ = "Akio Taniguchi"


# immediate functions
def _get_azely_path(filename: str):
    """Get path of azely file."""
    # standard library
    import os
    from pathlib import Path

    # constants
    AZELY_DIR = "AZELY_DIR"
    XDG_CONFIG_HOME = "XDG_CONFIG_HOME"
    XDG_CONFIG_HOME_ALT = Path().home() / ".config"

    if AZELY_DIR in os.environ:
        azely_dir = Path(os.getenv(AZELY_DIR))
    elif XDG_CONFIG_HOME in os.environ:
        azely_dir = Path(os.getenv(XDG_CONFIG_HOME)) / "azely"
    else:
        azely_dir = XDG_CONFIG_HOME_ALT / "azely"

    return azely_dir / filename


def _load_azely_config(path):
    """Load azely's config written in TOML."""
    # standard library
    from collections import defaultdict

    # dependent packages
    import toml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()

    with path.open("r") as f:
        return defaultdict(dict, toml.load(f))


# constants
AZELY_CONFIG = _get_azely_path("config.toml")
AZELY_OBJECT = _get_azely_path("object.toml")
AZELY_LOCATION = _get_azely_path("location.toml")


# config
config = _load_azely_config(AZELY_CONFIG)


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
