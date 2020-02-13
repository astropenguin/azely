# standard library
from os import environ, getenv
from pathlib import Path


# constants (static)
DAYFIRST = False
FRAME = "icrs"
FREQ = "10T"
HERE = "here"
NOW = "now"
TIMEOUT = 10
TODAY = "today"
YEARFIRST = False


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
AZELY_OBJECT = AZELY_DIR / "object.toml"
AZELY_LOCATION = AZELY_DIR / "location.toml"
