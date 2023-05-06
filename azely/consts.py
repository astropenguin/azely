"""Azely's consts module (constants).

This module provides static constants used for default values of functions
and constants indicating Azely's directory/files, which are dynamically
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
    "SITE",
    "TIME",
    "TIMEOUT",
    "TODAY",
    "VIEW",
    "YEARFIRST",
]


# standard library
from os import getenv
from pathlib import Path
from typing import TypeVar


# dependencies
from tomlkit import load


# type hints
T = TypeVar("T")


# helper functions
def ensure(toml: Path) -> Path:
    """Create an empty TOML file if it does not exist."""
    if not toml.exists():
        toml.parent.mkdir(parents=True, exist_ok=True)
        toml.touch()

    return toml


def getval(toml: Path, keys: str, default: T) -> T:
    """Return the value of the keys in a TOML file."""
    with open(toml, "r") as file:
        doc = load(file)

    for key in keys.split("."):
        if (doc := doc.get(key)) is None:
            return default

    return type(default)(doc.unwrap())


# config/cache files and directory for them
if (env := getenv("AZELY_DIR")) is not None:
    AZELY_DIR = Path(env)
elif (env := getenv("XDG_CONFIG_HOME")) is not None:
    AZELY_DIR = Path(env) / "azely"
else:
    AZELY_DIR = Path.home() / ".config" / "azely"


AZELY_CONFIG = ensure(AZELY_DIR / "config.toml")
AZELY_OBJECT = ensure(AZELY_DIR / "objects.toml")
AZELY_LOCATION = ensure(AZELY_DIR / "locations.toml")


# default values for public functions
HERE = "here"
"""Special value for getting current location information."""

NOW = "now"
"""Special value for getting current time information."""

TODAY = "today"
"""Special value for getting today's time information."""

DAYFIRST = getval(AZELY_CONFIG, "defaults.dayfirst", False)
"""Default value for the ``dayfirst`` argument."""

FRAME = getval(AZELY_CONFIG, "defaults.frame", "icrs")
"""Default value for the ``frame`` argument."""

FREQ = getval(AZELY_CONFIG, "defaults.freq", "10T")
"""Default value for the ``freq`` argument."""

GOOGLE_API = getval(AZELY_CONFIG, "defaults.google_api", "")
"""Default value for the ``google_api`` argument."""

IPINFO_API = getval(AZELY_CONFIG, "defaults.ipinfo_api", "")
"""Default value for the ``ipinfo_api`` argument."""

SITE = getval(AZELY_CONFIG, "defaults.site", HERE)
"""Default value for the ``site`` argument."""

TIME = getval(AZELY_CONFIG, "defaults.time", TODAY)
"""Default value for the ``time`` argument."""

TIMEOUT = getval(AZELY_CONFIG, "defaults.timeout", 10)
"""Default value for the ``timeout`` argument."""

VIEW = getval(AZELY_CONFIG, "defaults.view", "")
"""Default value for the ``view`` argument."""

YEARFIRST = getval(AZELY_CONFIG, "defaults.yearfirst", False)
"""Default value for the ``yearfirst`` argument."""
