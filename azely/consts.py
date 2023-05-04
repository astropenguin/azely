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
from os import environ
from pathlib import Path


# constants (static)
DAYFIRST = False
"""Default value for the ``dayfirst`` argument."""

FRAME = "icrs"
"""Default value for the ``frame`` argument."""

FREQ = "10T"
"""Default value for the ``freq`` argument."""

HERE = "here"
"""Special value for getting location information by current IP address."""

NOW = "now"
"""Special value for getting current time information."""

TIMEOUT = 10
"""Default value for the ``timeout`` argument."""

TODAY = "today"
"""Special value for getting today's time information."""

YEARFIRST = False
"""Default value for the ``yearfirst`` argument."""


# constants (dynamic)
def ensure(file: Path) -> Path:
    """Create an empty file if it does not exist."""
    if not file.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()

    return file


if "AZELY_DIR" in environ:
    AZELY_DIR = Path(environ["AZELY_DIR"])
elif "XDG_CONFIG_HOME" in environ:
    AZELY_DIR = Path(environ["XDG_CONFIG_HOME"]) / "azely"
else:
    AZELY_DIR = Path().home() / ".config" / "azely"


AZELY_CONFIG = ensure(AZELY_DIR / "config.toml")
AZELY_OBJECT = ensure(AZELY_DIR / "objects.toml")
AZELY_LOCATION = ensure(AZELY_DIR / "locations.toml")
