__version__ = "0.4.0"
__author__ = "Akio Taniguchi"


# get constants
def _get_azely_dir():
    # standard library
    import os
    from pathlib import Path

    # constants
    AZELY = "azely"
    AZELY_DIR = "AZELY_DIR"
    XDG_CONFIG_HOME = "XDG_CONFIG_HOME"
    XDG_CONFIG_HOME_ALT = Path().home() / ".config"

    if AZELY_DIR in os.environ:
        return Path(os.getenv(AZELY_DIR))
    elif XDG_CONFIG_HOME in os.environ:
        return Path(os.getenv(XDG_CONFIG_HOME)) / AZELY
    else:
        return XDG_CONFIG_HOME_ALT / AZELY


AZELY_DIR = _get_azely_dir()
AZELY_CONFIG = AZELY_DIR / "config.toml"
AZELY_OBJECTS = AZELY_DIR / "objects.toml"
AZELY_LOCATIONS = AZELY_DIR / "locations.toml"


# load config
def _load_config(azely_config):
    # standard library
    from collections import defaultdict

    # dependent packages
    import toml

    if not azely_config.parent.exists():
        azely_config.parent.mkdir(parents=True)

    azely_config.touch()

    with azely_config.open() as f:
        return defaultdict(dict, toml.load(f))


config = _load_config(AZELY_CONFIG)


# base error class
class AzelyError(Exception):
    pass
