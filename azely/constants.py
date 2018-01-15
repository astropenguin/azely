# coding: utf-8

# public items
__all__ = ['DATA_DIR',
           'USER_DIR',
           'CLI_CONFIG',
           'KNOWN_LOCS',
           'KNOWN_OBJS',
           'SEPARATORS',
           'DATE_FORMAT']

# standard library
from shutil import copy
from pathlib import Path

# dependent packages
import azely
import yaml

# module constants
HOME = Path('~').expanduser()
LOCS = 'known_locations.yaml'
OBJS = 'known_objects.yaml'
CONFIG = 'cli_config.yaml'
SAMPLE = 'sample_objects.yaml'


# package constants
DATA_DIR = Path(azely.__path__[0]) / 'data'
USER_DIR = HOME / '.azely'
CLI_CONFIG = USER_DIR / CONFIG
KNOWN_LOCS = USER_DIR / LOCS
KNOWN_OBJS = USER_DIR / OBJS
SEPARATORS = '-+_,./ '
DATE_FORMAT = '%Y-%m-%d'


# create directory and file (if not existing)
if not USER_DIR.exists():
    USER_DIR.mkdir()

if not CLI_CONFIG.exists():
    copy(DATA_DIR / CONFIG, USER_DIR)

if not (USER_DIR / SAMPLE).exists():
    copy(DATA_DIR / SAMPLE, USER_DIR)

if not KNOWN_LOCS.exists():
    azely.write_yaml(KNOWN_LOCS, {})

if not KNOWN_OBJS.exists():
    azely.write_yaml(KNOWN_OBJS, {})
