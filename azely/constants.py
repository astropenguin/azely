# public items
__all__ = ['DATE',
           'DATA_DIR',
           'USER_DIR',
           'KNOWN_LOCS',
           'KNOWN_OBJS',
           'CLI_PARSER',
           'PASS_FLAG']
           'USER_CONFIG']

# standard library
from logging import getLogger
from shutil import copy
from pathlib import Path
logger = getLogger(__name__)

# dependent packages
import azely
import yaml

# module constants
PKG = Path(azely.__path__[0])
HOME = Path('~').expanduser()
LOCS = 'known_locations.yaml'
OBJS = 'known_objects.yaml'
PARSER = 'cli_parser.yaml'
CONFIG = 'user_config.yaml'
SAMPLE = 'sample_objects.yaml'


# package constants
DATE = azely.parse_date()
DATA_DIR = PKG / 'data'
USER_DIR = HOME / '.azely'
KNOWN_LOCS = USER_DIR / LOCS
KNOWN_OBJS = USER_DIR / OBJS
CLI_PARSER = DATA_DIR / PARSER
USER_CONFIG = USER_DIR / CONFIG
PASS_FLAG = '<PASS>'


# create directory and file (if not existing)
if not USER_DIR.exists():
    logger.info(f'creating {USER_DIR}')
    USER_DIR.mkdir()

if not USER_CONFIG.exists():
    logger.info(f'creating {USER_DIR / CONFIG}')
    copy(DATA_DIR / CONFIG, USER_DIR)

if not (USER_DIR / SAMPLE).exists():
    logger.info(f'creating {USER_DIR / SAMPLE}')
    copy(DATA_DIR / SAMPLE, USER_DIR)

if not KNOWN_LOCS.exists():
    logger.info(f'creating {KNOWN_LOCS}')
    azely.write_yaml(KNOWN_LOCS, dict())

if not KNOWN_OBJS.exists():
    logger.info(f'creating {KNOWN_OBJS}')
    azely.write_yaml(KNOWN_OBJS, dict())
