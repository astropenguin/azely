__version__ = "0.4.0"
__author__ = "Akio Taniguchi"


# immediate functions
def _get_azely_dir():
    """Get path of azely's directory."""
    # standard library
    import os
    from pathlib import Path

    # constants
    AZELY_DIR = "AZELY_DIR"
    XDG_CONFIG_HOME = "XDG_CONFIG_HOME"
    XDG_CONFIG_HOME_ALT = Path().home() / ".config"

    if AZELY_DIR in os.environ:
        return Path(os.getenv(AZELY_DIR))
    elif XDG_CONFIG_HOME in os.environ:
        return Path(os.getenv(XDG_CONFIG_HOME)) / "azely"
    else:
        return XDG_CONFIG_HOME_ALT / "azely"


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
HERE = "here"
NOW = "now"
TODAY = "today"
AZELY_DIR = _get_azely_dir()
AZELY_CONFIG = AZELY_DIR / "config.toml"
AZELY_OBJECT = AZELY_DIR / "object.toml"
AZELY_LOCATION = AZELY_DIR / "location.toml"


# config
config = _load_azely_config(AZELY_CONFIG)


# base error class
class AzelyError(Exception):
    pass


# submodules
from . import utils  # noqa
from .location import *  # noqa
from .object import *  # noqa
from .time import *  # noqa
