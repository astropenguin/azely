__version__ = '0.3'
__author__  = 'astropenguin'


def _load_config(config='config.toml'):
    # standard library
    from collections import defaultdict
    from logging import getLogger
    from pathlib import Path
    logger = getLogger(__name__)

    # dependent packages
    import toml

    data = Path(__path__[0]) / 'data'
    user = Path.home() / '.azely'

    if not user.exists():
        logger.info(f'creating {user}')
        user.mkdir(parents=True)

    if not (user/config).exists():
        logger.info(f'creating {user/config}')
        copy(data/config, user/config)

    with (user/config).open() as f:
        return defaultdict(dict, toml.load(f))


config = _load_config()
from . import utils
from . import query
from . import azel
from .query import *
from .azel import *