__version__ = "0.4.0"
__author__ = "Akio Taniguchi"


# load config
def _load_config(filename="config.toml"):
    # standard library
    import os
    from collections import defaultdict
    from pathlib import Path

    # dependent packages
    import toml

    # constants
    AZELY = "azely"
    ENV_AZELY_DIR = "AZELY_DIR"
    XDG_CONFIG_HOME = "XDG_CONFIG_HOME"
    XDG_CONFIG_HOME_ALT = Path().home() / ".config"

    if ENV_AZELY_DIR in os.environ:
        azely_dir = Path(os.getenv(ENV_AZELY_DIR))
    elif XDG_CONFIG_HOME in os.environ:
        azely_dir = Path(os.getenv(XDG_CONFIG_HOME)) / AZELY
    else:
        azely_dir = XDG_CONFIG_HOME_ALT / AZELY

    if not azely_dir.exists():
        azely_dir.mkdir(parents=True)

    (azely_dir / filename).touch()

    with (azely_dir / filename).open() as f:
        return defaultdict(dict, toml.load(f))


config = _load_config()


# base error class
class AzelyError(Exception):
    pass
