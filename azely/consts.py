"""Azely's consts module (constants).

This module provides static constants used for default values of functions
and constants indicating Azely's directory/files, which are dinamically
determined by some environment variables of client.

"""
__all__ = [
    "AZELY_DIR",
    "AZELY_CONFIG",
    "AZELY_OBJECT",
    "AZELY_LOCATION",
    "DAYFIRST",
    "FRAME",
    "FREQ",
    "HERE",
    "NOW",
    "TIMEOUT",
    "TODAY",
    "YEARFIRST",
]


# standard library
from os import environ, getenv
from pathlib import Path


# constants (static)
DAYFIRST = False  #: Default value for the ``dayfirst`` argument.
FRAME = "icrs"  #: Default value for the ``frame`` argument.
FREQ = "10T"  #: Default value for the ``freq`` argument.
HERE = "here"  #: Special value for getting location information by current IP address.
NOW = "now"  #: Special value for getting current time information.
TIMEOUT = 10  #: Default value for the ``timeout`` argument.
TODAY = "today"  #: Special value for getting today's time information.
YEARFIRST = False  #: Default value for the ``yearfirst`` argument.


# constants (dynamic)
def get_azely_dir() -> Path:
    if "AZELY_DIR" in environ:
        return Path(getenv("AZELY_DIR"))
    elif "XDG_CONFIG_HOME" in environ:
        return Path(getenv("XDG_CONFIG_HOME")) / "azely"
    else:
        return Path().home() / ".config" / "azely"


AZELY_DIR = get_azely_dir()
AZELY_CONFIG = AZELY_DIR / "config.toml"
AZELY_OBJECT = AZELY_DIR / "objects.toml"
AZELY_LOCATION = AZELY_DIR / "locations.toml"
