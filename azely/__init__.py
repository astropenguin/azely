__version__ = '0.3'
__author__  = 'astropenguin'


# azely's config
def _load_config():
    # standard library
    from collections import defaultdict
    from logging import getLogger
    from shutil import copy
    from pathlib import Path
    logger = getLogger(__name__)

    # dependent packages
    import toml

    data = Path(__path__[0]) / 'data'
    user = Path.home() / '.config' / 'azely'
    config = 'config.toml'

    if not user.exists():
        logger.info(f'creating {user}')
        user.mkdir(parents=True)

    if not (user/config).exists():
        logger.info(f'creating {user/config}')
        copy(data/config, user/config)

    with (user/config).open() as f:
        return defaultdict(dict, toml.load(f))

config = _load_config()


# azely's base error class
class AzelyError(Exception):
    pass


# azely's submodules
from . import utils
from . import query
from . import azel
# from . import plot
from .query import *
# from .azel import *
