__all__ = [
    # file-related
    "AZELY_DIR",
    "AZELY_CACHE",
    "AZELY_CONFIG",
    # location-related
    "HERE",
    # object-related
    "SOLAR_FRAME",
    "SOLAR_OBJECTS",
    # time-related
    "NOW",
    "TODAY",
    # defaults
    "DAYFIRST",
    "FRAME",
    "FREQ",
    "GOOGLE_API",
    "IPINFO_API",
    "SITE",
    "TIME",
    "TIMEOUT",
    "VIEW",
    "YEARFIRST",
]


# standard library
from os import getenv
from pathlib import Path
from typing import Any, TypeVar, overload


# dependencies
from astropy.coordinates import solar_system_ephemeris as solar
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


@overload
def getval(toml: Path, keys: str, default: type[T]) -> T | None: ...


@overload
def getval(toml: Path, keys: str, default: T) -> T: ...


def getval(toml: Path, keys: str, default: Any) -> Any:
    """Return the value of the keys in a TOML file."""
    if isinstance(default, type):
        type_, default_ = default, None
    else:
        type_, default_ = type(default), default

    with open(toml) as file:
        doc = load(file)

    for key in keys.split("."):
        if (doc := doc.get(key)) is None:
            return default_

    return type_(doc.unwrap())


# file-related
if (env := getenv("AZELY_DIR")) is not None:
    AZELY_DIR = Path(env)
elif (env := getenv("XDG_CONFIG_HOME")) is not None:
    AZELY_DIR = Path(env) / "azely"
else:
    AZELY_DIR = Path.home() / ".config" / "azely"


AZELY_CACHE = ensure(AZELY_DIR / "cache.toml")
AZELY_CONFIG = ensure(AZELY_DIR / "config.toml")


# location-related
HERE = "here"
"""Special query for getting current location information."""


# object-related
SOLAR_FRAME = "solar"
"""Special frame for objects in the solar system."""

SOLAR_OBJECTS: tuple[str, ...] = tuple(solar.bodies)  # type: ignore
"""List of objects in the solar system."""


# time-related
NOW = "now"
"""Special query for getting current time information."""

TODAY = "today"
"""Special query for getting today's time information."""


# defaults
DAYFIRST = getval(AZELY_CONFIG, "defaults.dayfirst", False)
"""Default value for the ``dayfirst`` parameter."""

FRAME = getval(AZELY_CONFIG, "defaults.frame", "icrs")
"""Default value for the ``frame`` parameter."""

FREQ = getval(AZELY_CONFIG, "defaults.freq", "10T")
"""Default value for the ``freq`` parameter."""

GOOGLE_API = getval(AZELY_CONFIG, "defaults.google_api", str)
"""Default value for the ``google_api`` parameter."""

IPINFO_API = getval(AZELY_CONFIG, "defaults.ipinfo_api", str)
"""Default value for the ``ipinfo_api`` parameter."""

SITE = getval(AZELY_CONFIG, "defaults.site", HERE)
"""Default value for the ``site`` parameter."""

TIME = getval(AZELY_CONFIG, "defaults.time", TODAY)
"""Default value for the ``time`` parameter."""

TIMEOUT = getval(AZELY_CONFIG, "defaults.timeout", 10.0)
"""Default value for the ``timeout`` parameter."""

VIEW = getval(AZELY_CONFIG, "defaults.view", str)
"""Default value for the ``view`` parameter."""

YEARFIRST = getval(AZELY_CONFIG, "defaults.yearfirst", False)
"""Default value for the ``yearfirst`` parameter."""
