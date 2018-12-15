__all__ = ['config']


# standard library
from logging import getLogger
from shutil import copy
from pathlib import Path
logger = getLogger(__name__)


# depndent packages
import azely


# initial settings
data_dir = Path(azely.__path__[0]) / 'data'
user_dir = Path.home() / '.azely'
config_file = user_dir / 'config.toml'

if not user_dir.exists():
    logger.info(f'creating {user_dir}')
    user_dir.mkdir(parents=True)

if not config_file.exists():
    logger.info(f'creating {config_file}')
    copy(data_dir/config_file.name, config_file)


# package config
config = azely.read_toml(config_file)